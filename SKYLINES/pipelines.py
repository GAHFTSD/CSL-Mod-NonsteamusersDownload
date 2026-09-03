# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
# 导入 ANPmysql
from SKYLINES.ANPMYSQL import ANPmysql

class SkylinesPipeline:
    def __init__(self):
        self.anpmysql = ANPmysql()
        if not self.anpmysql.connect():
            raise Exception("无法连接到数据库")
        if not self.anpmysql.create_table():
            raise Exception("无法创建表")
        self.i = 0
        self.j = 0

    def process_item(self, item, spider):
        # 将 item 转换为字典格式
        item_data = ItemAdapter(item).asdict()
            
        # 与def create_table中定义的列名一致
        required_fields = {'modname', 'modlink', 'modimg', 'modattr', 'publishdate', 'upgradedate', 'downloadurl', 'filesize', 'steamlink'}
        ##检查是否一致
        if not required_fields.issubset(item_data.keys()):
            print(f"item 缺少字段: {required_fields - item_data.keys()}")
            return item
             
        # （主要）调用 insert 方法一次性将数据插入到指定的表中
        affected_rows = self.anpmysql.insert('CITYSKYLINESMODS', item_data)
        #item_data是字典形式，里面已经包含爬取的所有的数据
        if affected_rows <= 0:
            print("插入数据失败")
        else:
            self.i = self.i + 1;
            if self.i % 10 == 0:#能被10整除的都是10的倍数，每页十个数据，逢十进一
                self.j = self.j + 1;
                print(f"已经完成{self.j}页") 
        return item

    def close_spider(self, spider):
        # 当爬虫关闭时，关闭数据库连接
        self.anpmysql.close()