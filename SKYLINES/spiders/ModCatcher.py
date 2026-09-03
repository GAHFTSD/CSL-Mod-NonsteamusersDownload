import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from SKYLINES.items import SkylinesItem
from pyecharts import options as opts
from pyecharts.charts import Pie, WordCloud
import os
from pyecharts.charts import Page

class ModcatcherSpider(scrapy.Spider):
    name = "ModCatcher"
    allowed_domains = ["smods.ru"]
    start_urls = ["https://smods.ru/"]
    chest = []
    TotalPage = 5000#最大爬取页

    def parse(self, response):
        html = response.body
        soup = BeautifulSoup(html, "html.parser")
        body = soup.find("div", attrs ={"class": "hu-pad group"})

        
        #内容(一页五排，一排两个)
        content = body.find("div", attrs={"class": "post-list group"})
        dimods = content.find_all("div", attrs={"class": "post-row"})
        for dimod in dimods:
            articles = dimod.find_all("article")
            for article in articles:
                wallet = {}
                information = article.find("div", attrs={"class": "post-inner post-hover"})
                detail = information.find("div", attrs={"class": "post-thumbnail"})
                modlink = detail.find("a")
                wallet["模组链接"] = modlink.get("href") if modlink else "NONE"


                modimg = detail.find("img")
                wallet["模组图片"] = modimg.get("src") if modimg else "NONE"


                informations = information.find("div", attrs={"class": "post-meta group"})
                modname = information.find("h2", attrs={"class": "post-title entry-title"})
                modname = modname.find("a") if modname else "NONE"
                wallet["模组名称（英）"] = modname.text if modname != "NONE" else "NONE"
                #翻译（拓展）
                
                
                translationDict = {
                    "Mod": "模组",
                    "Vehicle": "车辆",
                    "Prop": "道具",
                    "Building": "建筑",
                    "Citizen": "市民",
                    "Collections": "收藏夹",
                    "Color Correction LUT": "色彩校正LUT",
                    "District Style": "资产包",
                    "Intersection": "立交",
                    "Map": "地图",
                    "Map Theme": "地图主题",
                    "Park": "公园",
                    "Park Area": "公园区域",
                    "Road": "道路",
                    "SaveGame": "存档",
                    "Scenario": "剧情",
                    "Tree": "树木",
                    "Electricity": "电力",
                    "Uncategorized": "未分类",
                    "Cinematic Cameras":"视觉镜头"
                }

                modattr = informations.find("p", attrs={"class": "post-category"})
                modattr = modattr.find("a") if modattr else "NONE"
                translated = translationDict.get(modattr.text, modattr.text)
                wallet["模组属性"] = translated if translated else "NONE"
                
                
                date = informations.find("time")
                wallet["上传日期"] = date.get("datetime") if date else "NONE"
               
               
                upgradedate = information.find("span", attrs={"class": "skymods-item-date"})
                wallet["更新日期"] = upgradedate.text if upgradedate else "NONE"
                
                
                downloadurl = information.find("a", attrs={"class": "skymods-excerpt-btn"})
                wallet["下载链接"] = downloadurl.get("href") if downloadurl else "NONE"
                
                
                filesize = information.find("span", attrs={"class": "skymods-item-file-size"})
                wallet["文件大小"] = filesize.text if filesize else "NONE"
                
                
                steaminfo = information.find("div", attrs={"class": "skymods-excerpt-meta"})
                steaminfo = steaminfo.find_all("p") if steaminfo else "NONE"
                steamlink = steaminfo[3].find("a", attrs={"target": "_blank"}) if steaminfo != "NONE" and len(steaminfo) > 3 else "NONE"
                wallet["Steam商店链接"] = steamlink.get("href") if steamlink != "NONE" else "NONE"
                self.chest.append(wallet)
                
                item = SkylinesItem()
                item["modlink"] = wallet["模组链接"]
                item["modimg"] = wallet["模组图片"]
                item["modname"] = wallet["模组名称（英）"]
                item["modattr"] = wallet["模组属性"]
                item["publishdate"] = wallet["上传日期"]
                item["upgradedate"] = wallet["更新日期"]
                item["downloadurl"] = wallet["下载链接"]
                item["filesize"] = wallet["文件大小"]
                item["steamlink"] = wallet["Steam商店链接"]
                yield item
                #翻页
                #navi = body.find("nav",attrs = {"class":"pagination group"})
                #navi = navi.find("a")
                #nav = navi.get("href") #下一页的链接
                #只能获得前三页
        for i in range(2,self.TotalPage+1):
            yield scrapy.Request(f"https://smods.ru/page/{i}",callback=self.parse)

    def close(self):
       #建立一个Output文件夹保存
        if not os.path.exists("Output"):
            os.mkdir("Output")

        c = pd.DataFrame(self.chest)
        c.to_csv("Output/modchest.csv", index=False, encoding="utf-8-sig")
        print("保存到 csv 文件")
        c.to_excel("Output/modchest.xlsx", index=False)
        print("保存到 excel 文件")
        with open("Output/modchest.json", "w", encoding="utf-8") as f:
            f.write(c.to_json(orient="records", force_ascii=False))
        print("保存到 json 文件")

        #提取pandas所保存的模组属性
        mod_attributes = c['模组属性'].tolist()
        modattrCount = {}
        for attr in mod_attributes:
            if attr in modattrCount:
                modattrCount[attr] += 1
            else:
                modattrCount[attr] = 1
        with open("Output/modattrCount.json", "w", encoding="utf-8") as f:
            f.write(str(modattrCount))
        print("保存到 modattrCount.json 文件")
        data_pair = [(attr, count) for attr, count in modattrCount.items()]
        # 创建词云图
        wordcloud = (
            WordCloud(init_opts=opts.InitOpts(width="800px", height="600px"))
            .add(
                series_name="模组属性",
                data_pair=data_pair,
                word_size_range=[12, 100],
                shape="circle",
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="天际线模组属性词云图"),
                tooltip_opts=opts.TooltipOpts(is_show=True),
            )
            .set_series_opts(
                tooltip_opts=opts.TooltipOpts(is_show=True),
                textstyle_opts=opts.TextStyleOpts(font_size=16, color="source", font_family="cursive"),
            )
        )

        # 创建饼图
        pie_data = [(attr, count) for attr, count in modattrCount.items()]
        pie = (
            Pie(init_opts=opts.InitOpts(width="800px", height="600px"))
            .add(
                series_name="模组属性",
                data_pair=pie_data,
                radius=["40%", "75%"]
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="天际线模组属性饼图"),
                legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%")
            )
            .set_series_opts(
                tooltip_opts=opts.TooltipOpts(trigger="item", formatter="{a} <br/>{b}: {c} ({d}%)"),
                label_opts=opts.LabelOpts(formatter="{b}: {c}")
            )
        )

        # 将词云图和饼图组合到一个 HTML 文件中


        page = Page(layout=Page.SimplePageLayout)
        page.add(wordcloud, pie)
        page.render("Output/modchest_wordcloud_pie.html")
        print("生成词云图和饼图 ")