# -*- coding: utf-8 -*-
import scrapy
import re
from lxml import etree
import time
import hashlib
import json
from scrapy_pack.mafengwo.items import CityItem,SpotItem

class CitySpider(scrapy.Spider):
    name = 'city'
    allowed_domains = ['mafengwo.cn']
    #start_urls = ['http://www.mafengwo.cn/mdd/base/list/pagedata_citylist']

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.10 Safari/537.36"
    }

    def get_time_st(self):

        now_time = str(time.time()).split('.')
        timest = now_time[0] + now_time[1][:3]
        #print(timest)
        return timest

    def start_requests(self):

        url = 'http://www.mafengwo.cn/mdd/base/list/pagedata_citylist'
        data = {
            "mddid": '21536',
            "page": '1'
        }
        # FormRequest 是Scrapy发送POST请求的方法
        yield scrapy.FormRequest(url, method='POST', headers=self.header, formdata=data, callback=self.parse_page)

    def parse(self, response):
        html = response.body.decode('UTF-8')
        #print(html)


    # 获取地区总页数
    def parse_page(self, response):

        html = response.body.decode('unicode_escape')
        etr_html = etree.HTML(html)

        page_count = etr_html.xpath('//span[contains(@class,"count")][1]/text()')

        # 总页数
        count = re.search(".*?(\d+).*?",page_count[0]).group(1)

        url = 'http://www.mafengwo.cn/mdd/base/list/pagedata_citylist'

        page_count = int(count)+1
        for i in range(1,page_count):
            #time.sleep(2)
            data = {
                "mddid": '21536',
                "page": str(i)
            }
            yield scrapy.FormRequest(url, method='POST', headers=self.header, formdata=data, callback=self.parse_city, dont_filter = True)
            #break

    #返回每个城市的链接
    def parse_city(self, response):

        city_list = response.xpath('//li[contains(@class,"item")]/div/a/@href').extract()

        ##print(city_list)
        for i in city_list:
            #time.sleep(2)

            id = re.search('.*?(\d+).*?',i).group(1)
            url = "http://www.mafengwo.cn/jd/"+id+"/gonglve.html"
            ##print("城市编号",id)
            request = scrapy.FormRequest(url, method='GET', headers=self.header, callback=self.parse_spot)
            request.meta['id'] = id
            ##print(url)
            yield request
            #break


    # 景 点 详 情
    def parse_spot(self, response):
        html = response.body.decode('UTF-8')
        etr_html = etree.HTML(html)
        ##print(html)
        hd = etr_html.xpath('//span[contains(@class,"hd")]/a/text()')
        address = ""
        for h in hd:
            address += h + " "
        id = response.meta['id']

        #获取当前时间戳
        now_time = self.get_time_st()
        url = 'http://www.mafengwo.cn/ajax/router.php'
        qdata = '{"_ts":"'+now_time+'","iMddid":"'+id+'","iPage":"1","iTagId":"0","sAct":"KMdd_StructWebAjax|GetPoisByTag"}c9d6618dbc657b41a66eb0af952906f1'
        sn = self.par(qdata.encode('utf-8'))
        data = {
            'sAct': 'KMdd_StructWebAjax|GetPoisByTag',
            'iTagId': '0',
            "iMddid": id,
            "iPage": '1',
            '_ts':now_time,
            '_sn': sn
        }
        ##print("sn=",sn)
        # FormRequest 是Scrapy发送POST请求的方法
        request =  scrapy.FormRequest(url, method='POST', headers=self.header, formdata=data, callback=self.parse_spot_page, dont_filter = True)
        request.meta['id'] = id
        request.meta['address'] = address
        #request.meta['address'] = address
        yield  request

        ##print(page_count)

    def par(self,content):
        hl = hashlib.md5()
        hl.update(content)
        return hl.hexdigest()[2:12]

    #全部景点分页信息
    def parse_spot_page(self, response):

        html = response.body.decode('unicode_escape').replace("\\",'')
        #print(html)

        spot_counts = re.search(r'<span class="count">共<span>(\d+)</span>页 / <span>(\d+)</span>条</span>',html,re.S)

        id = response.meta['id']
        address = response.meta['address']

        item = CityItem()

        item['city_id'] = id
        item['city_name'] = address
        item['city_num'] = spot_counts.group(2)

        yield item

        #print("城市编号", id)
        #print("城市名称", address)
        #print("景点总数量", spot_counts.group(2))

        spot_count = spot_counts.group(1)
        ##print(spot_count)

        url = 'http://www.mafengwo.cn/ajax/router.php'


        for i in range(1,int(spot_count)):
            # 获取当前时间戳
            now_time = self.get_time_st()
            #time.sleep(2)
            qdata = '{"_ts":"'+now_time+'","iMddid":"' + id + '","iPage":"'+str(i)+'","iTagId":"0","sAct":"KMdd_StructWebAjax|GetPoisByTag"}c9d6618dbc657b41a66eb0af952906f1'
            sn = self.par(qdata.encode('utf-8'))
            data = {
                'sAct': 'KMdd_StructWebAjax|GetPoisByTag',
                "iMddid": id,
                'iTagId': '0',
                "iPage": str(i),
                '_ts': now_time,
                '_sn': sn
            }
            request = scrapy.FormRequest(url, method='POST', headers=self.header, formdata=data, callback=self.parse_spot_list,dont_filter=True)
            request.meta['city_id'] = id
            #break
    #获取每一页的每一个景点的信息
    def parse_spot_list(self, response):

        html = response.body.decode('unicode_escape').replace("\\",'')

        page_list = re.findall(r'<a href="(.*?)" target="_blank" title=".*?">',html)

        ##print(page_list)
        for i in page_list:
            #time.sleep(2)
            url = 'http://www.mafengwo.cn'+i
            request = scrapy.FormRequest(url, method='GET', headers=self.header, callback=self.parse_spot_desc)
            request.meta['url'] = url
            request.meta['city_id'] = response.meta['city_id']
            # # #print(url)
            yield request
            #break


    # 景点详细信息
    def parse_spot_desc(self,response):

        url = response.meta['url']
        ##print(response.body.decode('utf-8'))
        id = re.search('.*?(\d+).*?',url).group(1)
        #print("景点编号",id)

        title = response.xpath('//div[contains(@class,"title")][1]/h1/text()').extract()
        #print("景点名称", title[0])

        desc = response.xpath('string(//div[contains(@class,"summary")][1])').extract()
        #print("景点简介", desc[0].strip())

        phone = response.xpath('//ul[contains(@class,"baseinfo clearfix")][1]/li/div[2]/text()').extract()
        #print("景点电话", phone[0])

        traffic = response.xpath('string(//div[contains(@class,"mod mod-detail")]/dl[1]/dd)').extract()
        #print("景点交通", traffic[0])

        ticket = response.xpath('string(//div[contains(@class,"mod mod-detail")]/dl[2]/dd/div[1])').extract()
        #print("景点门票", ticket[0])

        open_time = response.xpath('string(//div[contains(@class,"mod mod-detail")]/dl[3]/dd)').extract()
        #print("景点开放时间", open_time[0])

        address = response.xpath('string(//p[contains(@class,"sub")][1])').extract()
        #print("景点地址", address[0])

        item = SpotItem()
        item['city_id'] = response.meta['city_id']
        item['spot_id'] = id
        item['spot_name'] = title[0] if len(title)>0 else '暂无'
        item['spot_desc'] = desc[0].strip() if len(desc)>0 else '暂无'
        item['spot_phone'] = phone[0] if len(phone)>0 else '暂无'
        item['spot_traffic'] = traffic[0] if len(traffic)>0 else '暂无'
        item['spot_ticket'] = ticket[0] if len(ticket)>0 else '暂无'
        item['spot_open_time'] = open_time[0] if len(open_time)>0 else '暂无'
        item['spot_address'] = address[0] if len(address)>0 else '暂无'

        url = "http://pagelet.mafengwo.cn/poi/pagelet/poiCommentListApi?"

        t = self.get_time_st()
        qdata = '{"_ts": "' + str(t) + '", "params": "{"poi_id":"' + str(id) + '"}"}c9d6618dbc657b41a66eb0af952906f1'
        sn = self.par(qdata.encode('utf-8'))
        querystring = {
            "callback": "jQuery1810276052151146426_1555747207836",
            "params": "%7B%22poi_id%22%3A%22{}%22%7D".format(str(id)),
            "_ts": t,
            "_sn": sn,
            "_": t + 1
        }

        for key, value in querystring.items():
            url += (key + '=' + str(value) + '&')
        url = url[:-1]

        request = scrapy.FormRequest(url, method='GET', headers=self.header,  callback=self.parse_comment)
        request.meta['item'] = item
        yield request

        #获取评论信息
    def parse_comment(self, response):

        item = response.meta['item']


        html = response.body.decode('unicode_escape').replace("\\", '')
        etr_html = etree.HTML(html)

        num = etr_html.xpath('//div[contains(@class,"mhd mhd-large")]/span/em/text()')
        #print("点评总数量", num[0])

        num1 = etr_html.xpath('//div[contains(@class,"review-nav")]/ul/li[3]/a/span[2]/text()')
        #print("好评数量", num1[0])

        num2 = etr_html.xpath('//div[contains(@class,"review-nav")]/ul/li[4]/a/span[2]/text()')
        #print("中评数量", num2[0])

        num3 = etr_html.xpath('//div[contains(@class,"review-nav")]/ul/li[5]/a/span[2]/text()')
        #print("差评数量", num3[0])

        item['num'] = num[0] if len(num)>0  else '暂无'
        item['num1'] = num1[0] if len(num1)>0  else '暂无'
        item['num2'] = num2[0] if len(num2)>0  else '暂无'
        item['num3'] = num3[0] if len(num3)>0  else '暂无'

        print(item)

        yield item
