# -*- coding: utf-8 -*-
import time

import scrapy
from selenium import webdriver
from bs4 import BeautifulSoup
from lxml import etree
from CQJob.items import CqjobItem
from pyecharts import TreeMap, Pie, Bar


class CqjobsSpider(scrapy.Spider):
    name = 'cqjobs'
    allowed_domains = ['lagou.com']
    start_urls = ['https://www.lagou.com/jobs/list_?px=default&hy=%E5%8C%BB%E7%96%97%E5%81%A5%E5%BA%B7&city=%E9%87%8D%E5%BA%86']

    def parse(self, response):

        # 开启chromedriver
        browser = webdriver.Chrome()
        browser.get(self.start_urls[0])
        browser.implicitly_wait(10)
        # 写入源html
        # f = open('./wr.txt', 'w', encoding='utf8')
        # raw_html = browser.page_source
        # f.write(raw_html)
        # f.close()

        # 使用BeautifulSoup定位
        '''
        pager_next 
        pager_next pager_next_disabled
        '''
        for i in range(11):
            selector = etree.HTML(browser.page_source)  # 获取源码
            soup = BeautifulSoup(browser.page_source, features='lxml')
            # a = soup.find_all("div", class_="pager_container")
            span = soup.find("div", attrs={"class": "pager_container"}).find("span", attrs={"action": "next"})
            # f = open('./new.txt', 'w', encoding='utf8')
            # f.write(str(span))
            # f.close()
            classSpan = span['class']
            print('----------------------------------------------')
            print(classSpan) # 输出内容为 -> ['pager_next', 'pager_next_disabled']
            next_flag = classSpan[1]
            self.parsedata(selector)
            if next_flag == "pager_next_disabled":
                print("已经爬到最后一页，爬虫结束")
                break
            else:
                print("还有下一页，爬虫继续")
                browser.find_element_by_xpath('//*[@id="s_position_list"]/div[2]/div/span[@action="next"]').click()  # 点击下一页
            time.sleep(5)
            print('第{}页抓取完毕'.format(i + 1))


        browser.close()

        items = CqjobItem()
        items['name'] = self.name_list
        items['company'] = self.company_list
        items['location'] = self.location_list
        items['welfare'] = self.welfare_list
        items['salaryMin'] = self.salaryMin_list
        items['salaryMax'] = self.salaryMax_list
        items['salaryMid'] = self.salaryMid_list
        items['experience'] = self.experience_list
        items['education'] = self.education_list
        items['companyType'] = self.companyType_list
        items['companyLevel'] = self.companyLevel_list
        items['companySize'] = self.companySize_list
        print(items)
        self.LocAnalysis(items)
        self.educaAnalysis(items)
        self.CompanyAnalysis(items)
        self.SalaryAnalysis(items)
        self.SalaryTreeAnalysis(items)

        yield items
    name_list = []
    location_list = []
    company_list = []
    welfare_list = []
    salaryMin_list = []
    salaryMax_list = []
    salaryMid_list = []
    experience_list = []
    education_list = []
    companyType_list = []
    companyLevel_list = []
    companySize_list = []
    def parsedata(self, selector):
        sel_list = selector.xpath('//*[@id="s_position_list"]/ul/li')
        for item in sel_list:
            name = item.xpath('div[1]/div[1]/div[1]/a/h3/text()')[0]
            self.name_list.append(name)
            location = item.xpath('div[1]/div[1]/div[1]/a/span/em/text()')[0]
            self.location_list.append(location)
            company = item.xpath('div[1]/div[2]/div[1]/a/text()')[0]
            self.company_list.append(company)
            welfare = item.xpath('div[2]/div[2]/text()')[0]
            self.welfare_list.append(welfare)
            salaryList = item.xpath('div[1]/div[1]/div[2]/div/span/text()')[0].strip().split("-")
            # print(salaryList) # [10k-15k]
            salaryMin = salaryList[0][:len(salaryList[0]) - 1] # 10 去除k,只留数字
            self.salaryMin_list.append(salaryMin)
            salaryMax = salaryList[1][:len(salaryList[1]) - 1] # 15
            self.salaryMax_list.append(salaryMax)
            salaryMid = (int(salaryMin) + int(salaryMax)) / 2
            self.salaryMid_list.append(salaryMid)

            educationArray = item.xpath('div[1]/div[1]/div[2]/div//text()')[3].strip().split("/")
            # print(educationArray)
            experience = educationArray[0].strip()
            self.experience_list.append(experience)
            education = educationArray[1].strip()
            self.education_list.append(education)
            # conmpanyMsgArray = item.xpath('div[1]/div[2]/div[2]/text()')[0].strip().split("/")
            conmpanyMsgList = item.xpath('div[1]/div[2]/div[2]/text()')[0].strip().split("/")
            companyType = conmpanyMsgList[0].strip()
            self.companyType_list.append(companyType)
            companyLevel = conmpanyMsgList[1].strip()
            self.companyLevel_list.append(companyLevel)
            companySize = conmpanyMsgList[2].strip()
            self.companySize_list.append(companySize)
    # TreeMap数据格式
    def getTreeData(self,treedata):
        treemap_data = []
        for key in treedata:
            if key != '重庆':
                treemap_data.append({"value": treedata[key], "name": key})
        return treemap_data

    # 位置数据分析
    def LocAnalysis(self, items):
        loca_data = items['location']
        list_data = set(loca_data)
        treemap_data = {}
        for item in list_data:
            treemap_data[item] = loca_data.count(item)
        print(treemap_data)
        data = self.getTreeData(treemap_data) # 转换为相应的TreeMap数据
        print(data)

        treemap = TreeMap("重庆医疗健康位置分布图", width=1200, height=600, title_pos="center")
        treemap.add("位置数据", data, is_label_show=True, label_pos='inside', label_text_color='#000', is_legend_show=False)
        treemap.render()

    def educaAnalysis(self, items):
        educa_data = items['education']
        educalist_data = set(educa_data)
        print(educalist_data)
        edupie_list = []
        edupie_data = []
        for item in educalist_data:
            edupie_list.append(item)
            edupie_data.append(educa_data.count(item))
        print(edupie_list)
        print(edupie_data)
        pie = Pie("重庆医疗健康招聘学历要求", title_pos='center')
        pie.add(
            "学历",
            edupie_list,
            edupie_data,
            center=[50, 50],
            is_random=True,
            radius=[30, 75],
            rosetype="area",
            is_legend_show=False,
            is_label_show=True,
        )
        pie.render()

    # 位置数据分析
    def CompanyAnalysis(self, items):
        loca_data = items['company']
        list_data = set(loca_data)
        treemap_data = {}
        for item in list_data:
            treemap_data[item] = loca_data.count(item)
        print(treemap_data)
        data = self.getTreeData(treemap_data) # 转换为相应的TreeMap数据
        print(data)

        treemap = TreeMap("重庆医疗相关公司分布图", width=1500, height=900, title_pos="center")
        treemap.add("公司数据", data, is_label_show=True, label_pos='inside', label_text_color='#000', is_legend_show=False)
        treemap.render()

    # 工资数据分析
    def SalaryAnalysis(self, items):
        axis_data = items['name']
        print(axis_data)
        ayis_data = items['salaryMid']
        print(ayis_data)
        bar = Bar("重庆医疗职位平均工资图", width=1500, height=450, title_pos="center")
        bar.add("工资数据", axis_data, ayis_data, mark_line=["average"], mark_point=["max", "min"], legend_pos='right', is_xaxis_show=False)
        bar.render()

    def SalaryTreeAnalysis(self, items):
        salary_name = items['name']
        salary_data = items['salaryMid']
        salary_set = set(salary_name)
        treemap_data = {}
        for item in salary_set:
            treemap_data[item] = salary_data
        print(treemap_data)
        data = self.getTreeData(treemap_data)  # 转换为相应的TreeMap数据
        print(data)

        treemap = TreeMap("重庆医疗职位工资分布图", width=1500, height=900, title_pos="center")
        treemap.add("职位数据", data, is_label_show=True, label_pos='inside', label_text_color='#000', is_legend_show=False)
        treemap.render()

