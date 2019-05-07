# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from scrapy_pack.mafengwo.items import CityItem,SpotItem

class MafengwoPipeline(object):

    def __init__(self):

        # 1. 建立数据库的连接
        self.connect = pymysql.connect(
            host='localhost',
            port = 3306,
            user ='root',
            passwd ='root',
            db ='data',
            charset ='utf8'
        )
        self.cursor = self.connect.cursor()
        sql = '''create table IF NOT EXISTS mafengwo_city(
                city_id int primary key auto_increment,
                city_name varchar(255),
                city_num int
            )'''
        self.cursor.execute(sql)
        sql = '''create table IF NOT EXISTS mafengwo_spot(
                    spot_id int primary key auto_increment,
                    city_id int,
                    spot_name varchar(255),
                    spot_desc text,
                    spot_phone varchar(255),
                    spot_traffic varchar(255),
                    spot_ticket varchar(255),
                    spot_open_time varchar(255),
                    spot_address varchar(255),
                    num varchar(255),
                    num1 varchar(255),
                    num2 varchar(255),
                    num3 varchar(255)
                )'''
        self.cursor.execute(sql)

    def process_item(self, item, spider):
        if isinstance(item, CityItem):
            self.insert_city(item)
        elif isinstance(item, SpotItem):
            self.insert_spot(item)
        print(item)
        #return item

    #插入数据库
    def insert_city(self, item):
        print("执行了")
        try:
            insert_sql = "INSERT INTO mafengwo_city(city_id, city_name, city_num) " \
                         "VALUES (%s, %s, %s)"
            self.cursor.execute(insert_sql,(item['city_id'],item['city_name'],item['city_num']))  # 执行sql语句
            self.connect.commit()  # 提交到数据库执行
        except Exception as e:
            print(e)
            self.connect.rollback()  # 如果发生错误则回滚

    def insert_spot(self, item):
        try:
            insert_sql = "INSERT INTO mafengwo_spot(" \
                         "spot_id, city_id, spot_name, spot_desc, spot_phone, spot_traffic, spot_ticket, spot_open_time, " \
                         "spot_address, num, num1, num2, num3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            self.cursor.execute(insert_sql,(item['spot_id'],item['city_id'], item['spot_name'],item['spot_desc'], item['spot_phone'], item['spot_traffic']
                                            , item['spot_ticket'], item['spot_open_time'], item['spot_address'], item['num'], item['num1']
                                            , item['num2'], item['num3']))  # 执行sql语句
            self.connect.commit()  # 提交到数据库执行
        except Exception as e:
            print(e)
            self.connect.rollback()  # 如果发生错误则回滚

    def close_spider(self, spider):
        #self.connect.commit()  # 提交事务
        self.cursor.close()
        self.connect.close()

