
![](http://p20tr36iw.bkt.clouddn.com/scrapy_tree.png)

<!--more-->

# Scrapy框架之爬取拉勾网

## 0.前言

- scrapy框架
- BeautifulSoup
- lxml
- selenium
- pyecharts
- pymysql

## 1.建立项目

```python
scrapy startproject CQJob
scrapy genspider cqjobs
```

## 2.spider+selenium

**start_urls配置**

```python
start_urls = ['https://www.lagou.com/jobs/list_?px=default&hy=%E5%8C%BB%E7%96%97%E5%81%A5%E5%BA%B7&city=%E9%87%8D%E5%BA%86'] # 配置url
```

**chromedriver配置**

```python
# 开启chromedriver
browser = webdriver.Chrome()
browser.get(self.start_urls[0])
browser.implicitly_wait(10) 
# 
# 写入源html
# f = open('./wr.txt', 'w', encoding='utf8')
# raw_html = browser.page_source
# f.write(raw_html)
# f.close()
.......
BeautifulSoup及xpath使用对多页面处理代码
............
browser.close() # 关闭浏览器
```

**BeautifulSoup及xpath使用对多页面处理**

```python
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
        # 这里一定要注意不能直接copy源代码的xpath，因为每个页面元素标签有可能不一样！
        browser.find_element_by_xpath('//*[@id="s_position_list"]/div[2]/div/span[@action="next"]').click()  # 点击下一页 
    time.sleep(5)
    print('第{}页抓取完毕'.format(i + 1))
```

**数据定义及封装**

`items.py`

```python
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
```

`cqjobs.py(spiders文件)`  

```python
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
```

**xpath爬取特定数据**

```python
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
        salaryMin = salaryList[0][:len(salaryList[0]) - 1]  # 10 去除k,只留数字
        self.salaryMin_list.append(salaryMin)
        salaryMax = salaryList[1][:len(salaryList[1]) - 1]  # 15
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
```

**数据分析**

```python
# TreeMap数据格式
def getTreeData(self, treedata):
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
    data = self.getTreeData(treemap_data)  # 转换为相应的TreeMap数据
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
    data = self.getTreeData(treemap_data)  # 转换为相应的TreeMap数据
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
    bar.add("工资数据", axis_data, ayis_data, mark_line=["average"], mark_point=["max", "min"], legend_pos='right',
            is_xaxis_show=False)
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
```

**数据分析调用**

```python
self.LocAnalysis(items)
self.educaAnalysis(items)
self.CompanyAnalysis(items)
self.SalaryAnalysis(items)
self.SalaryTreeAnalysis(items)
```

![](http://p20tr36iw.bkt.clouddn.com/2018-09-05_192601.png)

![](http://p20tr36iw.bkt.clouddn.com/%E9%87%8D%E5%BA%86%E5%8C%BB%E7%96%97%E7%9B%B8%E5%85%B3%E5%85%AC%E5%8F%B8%E5%88%86%E5%B8%83%E5%9B%BE.png)

![](http://p20tr36iw.bkt.clouddn.com/%E9%87%8D%E5%BA%86%E4%BA%92%E8%81%94%E7%BD%91%E5%8C%BB%E7%96%97%E7%9F%A9%E5%BD%A2%E6%A0%91%E5%9B%BE.png)

![](http://p20tr36iw.bkt.clouddn.com/%E9%87%8D%E5%BA%86%E5%8C%BB%E7%96%97%E8%81%8C%E4%BD%8D%E5%B7%A5%E8%B5%84%E5%88%86%E5%B8%83%E5%9B%BE.png)

![](http://p20tr36iw.bkt.clouddn.com/%E9%87%8D%E5%BA%86%E5%8C%BB%E7%96%97%E8%81%8C%E4%BD%8D%E5%B9%B3%E5%9D%87%E5%B7%A5%E8%B5%84%E5%9B%BE.png)



## 3.数据存储

`settings.py`

```python
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

ITEM_PIPELINES = {
   'CQJob.pipelines.CqjobPipeline': 300,
}
```

`pipelines.py`

```python
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
```

![](http://p20tr36iw.bkt.clouddn.com/py_scrapy_mongo.png)

## 4.项目地址

[戳这里!!!](https://github.com/Light-City/CQJob)

