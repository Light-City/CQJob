# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CqjobItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field() # 职位
    company = scrapy.Field() # 公司名称
    location = scrapy.Field() # 公司地点
    welfare = scrapy.Field() # 福利
    salaryMin = scrapy.Field() # 工资下限
    salaryMax = scrapy.Field() # 工资上限
    salaryMid = scrapy.Field() # 平均工资
    experience = scrapy.Field() # 工作经验
    education = scrapy.Field() # 教育程度
    companyType = scrapy.Field() # 公司类型
    companyLevel = scrapy.Field() # 公司级别
    companySize = scrapy.Field() # 公司人数规模
