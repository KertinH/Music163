import scrapy
from ..items import Music163Item

all_page=[]

class Music_spider(scrapy.Spider):
    '''网易云音乐爬虫'''
    name = 'music'

    def start_requests(self):
        '''初始链接'''
        url = ['http://music.163.com']
        for u in url:
            yield scrapy.Request(u,callback=self.parse_songlist)

    def parse_songlist(self,response):
        '''歌单分类链接'''
        url = response.xpath("//ul[@class='nav']/li[3]/a/@href").extract_first()
        url = response.urljoin(url)
        yield scrapy.Request(url,callback=self.parse_list_type)

    def parse_list_type(self,response):
        '''歌单类型链接'''
        '''获取所有类型的歌单的链接'''
        url = response.xpath("//dl[@class='f-cb']/dd/a/@href").extract()
        for i in url:
            url = response.urljoin(i)
            yield scrapy.Request(url,callback=self.parse_next)

    def parse_next(self,response):
        '''翻页'''
        '''用来获取某一类型歌单下的所有页面'''
        next = response.xpath("//div[@class='u-page']/a[contains(text(),'下一页')]/@href").extract()
        if 'javascript' not in next[0]:
            url = response.urljoin(next[0])
            global all_page
            all_page.append(url)
            yield scrapy.Request(url,callback=self.parse_next)
        else:
            for i in all_page:
                all_page = all_page[1:]
                #在这一句中不启用 Reuest 的url去重功能（dont_filter=Trun）
                yield scrapy.Request(i,callback=self.parse_list,dont_filter=True)

    def parse_list(self,response):
        '''歌单链接'''
        '''获取页面中所有歌单的链接'''
        url = response.xpath("//ul[@class='m-cvrlst f-cb']/li/div/a/@href").extract()
        for i in url:
            url = response.urljoin(i)
            yield scrapy.Request(url, callback=self.parse_list_song)

    def parse_list_song(self,response):
        '''歌单中的歌曲链接'''
        '''获取歌单中所有歌曲的链接'''
        url = response.xpath("//ul[@class='f-hide']/li/a/@href").extract()
        for i in url:
            url = response.urljoin(i)
            yield scrapy.Request(url,callback=self.parse_song)

    def parse_song(self,response):
        '''获取歌曲信息与下载地址，并传入item中'''
        i = Music163Item()
        src = []
        song_id = response.url.split('=')[1]
        song_name = response.xpath("//em[@class='f-ff2']/text()").extract_first()
        album = response.xpath("//p[@class='des s-fc4']/a[@class='s-fc7']/text()").extract_first()
        singer = '&'.join(response.xpath("//p[@class='des s-fc4']/span/a/text()").extract())
        song_src = 'http://music.163.com/song/media/outer/url?id={}.mp3'.format(song_id)
        src.append(song_src)
        i['file_urls'] = src
        i['song_name'] = song_name
        i['singer'] = singer
        yield i
