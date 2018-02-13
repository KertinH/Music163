# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.files import FilesPipeline
from io import BytesIO
import sys
from scrapy.utils.misc import md5sum
from scrapy.http import Request


class TheFilesPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        '''重载，增加传回item的功能'''
        return [Request(x,meta={'item':item}) for x in item.get(self.files_urls_field, [])]

    def file_downloaded(self, response, request, info):
        '''重载，增加输出文件大小的功能'''
        path = self.file_path(request, response=response, info=info)
        buf = BytesIO(response.body)
        checksum = md5sum(buf)
        buf.seek(0)
        file_size = sys.getsizeof(response.body)
        print(file_size,'************'*30)
        buf.seek(0)
        self.store.persist_file(path, buf, info)
        return checksum

    def file_path(self, request, response=None, info=None):
        '''重载，自定义文件存储地址及文件名'''
        item = request.meta['item']
        file_name = '{}-{}'.format(item['song_name'], item['singer']) + '.mp3'
        return '%s' % file_name

class Music163Pipeline(object):
    def process_item(self, item, spider):
        return item
