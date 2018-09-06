# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

# import logging
#
# logger = logging.getLogger(__name__)
import pymysql
class CqjobPipeline(object):
    def process_item(self, item, spider):
        '''
        将爬取的信息保存到mysql
        '''

        connection = pymysql.connect(host='localhost', user='root', password='xxxx', db='scrapydb', charset='utf8mb4')
        try:

            with connection.cursor() as cursor:
                for i in range(len(item['name'])):
                    sql = "insert into `cqjobs`(`name`,`company`,`location`,`welfare`,`salaryMin`,`salaryMax`,`salaryMid`,`experience`,`education`,`companyType`,`companyLevel`,`companySize`)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql, (
                        item['name'][i], item['company'][i], item['location'][i], item['welfare'][i],
                        item['salaryMin'][i], item['salaryMax'][i], item['salaryMid'][i], item['experience'][i],
                        item['education'][i], item['companyType'][i], item['companyLevel'][i], item['companySize'][i]))

                    connection.commit()
        # except pymysql.err.IntegrityError as e:
        #     print('重复数据，勿再次插入!')
        finally:
            connection.close()

        return item