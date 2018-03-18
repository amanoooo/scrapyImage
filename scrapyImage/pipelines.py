# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import time
from PIL import Image
import MySQLdb
import MySQLdb.cursors
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
import re
from settings import IMAGES_STORE
from twisted.enterprise import adbapi

class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['image'][0] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['image'][0])
            return item

class DownImage(ImagesPipeline):

    def get_media_requests(self, item, info):
        print('pipelines item is ', item)
        for image_url in item['image']:
            yield Request(image_url, meta={'item': item, 'img_url': image_url})

    def file_path(self, request, response=None, info=None):
        """
        :param request: 每一个图片下载管道请求
        :param response:
        :param info:
        :param strip :清洗Windows系统的文件夹非法字符，避免无法创建目录
        :return: 每套图的分类目录
        """
        item = request.meta['item']
        folder = item['title']
        folder_strip = strip(folder)
        image_guid = request.url.split('/')[-1]
        print 'image_guid is ', image_guid
        # filename = u'full/{0}/{1}'.format(folder_strip, image_guid)
        filename = IMAGES_STORE + folder + '/' + image_guid
        print 'filename is', filename
        return filename

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('图片未下载好 %s' % image_paths)
        print 'over, item is', item
        item['image'] = image_paths
        return item

def strip(path):
    """
    :param path: 需要清洗的文件夹名字
    :return: 清洗掉Windows系统非法文件夹名字的字符串
    """
    path = re.sub(r'[？\\*|“<>:/]', '', str(path))
    return path


class MySQLPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    # pipeline默认调用
    def process_item(self, item, spider):
        d = self.dbpool.runInteraction(self._conditional_insert, item)
        return d

    @staticmethod
    def _conditional_insert(tb, item):
        cTime = round(time.time() * 1000)
        if (item['image'][0].startswith('http') ):
            print 'error item ', item
        else:
            print 'right item ', item
            img0 = Image.open(item['image'][0])
            title0 = item['title']
            size0 = img0.size
            print 'size0 is ', size0
            dbPath = item['image'][0].replace('../../dbImage/','')
            tb.execute('insert into image_list (id, head_image, height, title, type, upload_dt, width) '
                       'values (%s, %s, %s, %s, %s, %s, %s)',
                       (cTime, dbPath, size0[1], title0, '1', cTime, size0[0]))
            for a in item["image"]:
                dbPath = a.replace('../../dbImage/','')
                img = Image.open(a)
                size = img.size
                tb.execute('insert into image_detail (width, height, image_list_id, url) values (%s, %s, %s, %s)',
                           (size[0], size[1], cTime, dbPath))
