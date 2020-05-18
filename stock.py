import scrapy
import pymongo
import requests
import json
import pandas as pd

class CrawlTest(scrapy.Spider):
    name = 'stock'

    def start_requests(self):
        #判斷資料庫中是否有數據，如果沒有就先從2018/12/27的資料開始爬取，獲得數據量
        try:
            result = self.collection.find()
            df = pd.DataFrame([i for i in result]).drop(columns="_id")
            time1 = str(int(list(df['表單1'])[-1])+86400)
            time2 = str(int(list(df['表單2'])[-1])+86400)
        except :
            #'''2018/12/27'''
            time1 = '1545868800'
            time2 = '1545868815'
        n_list = ['0050', '2330', '3008']
        for i in n_list:
            key = i
            url = "https://ws.api.cnyes.com/charting/api/v1/history?resolution=D&symbol=TWS:" + key + ':STOCK&from=' + time2 + '&to=' + time1
            url2 = "https://marketinfo.api.cnyes.com/mi/api/v1/investors/buysell/TWS%3A" + key + '%3ASTOCK?from=' + time2 + '&to=' + time1
            url3 = "https://ws.api.cnyes.com/quote/api/v1/quotes/TWS%3A" + key + '%3ASTOCK?column=J'
            yield self.parse(url, url2, url3, time1, time2)

    def __init__(self):
        #連接資料庫
        self.client = pymongo.MongoClient("localhost", port = 27017)
        self.db = self.client.StockData
        self.collection = self.db.StockDec
        self.headers = {"User-Agent":"Mozilla/5.0"}

    def parse(self, url, url2, url3, time1, time2):
        res = requests.get(url, headers = self.headers)
        res.status_code
        rawData = json.loads(res.content)
        res2 = requests.get(url2, headers = self.headers)
        res2.status_code
        raw2Data = json.loads(res2.content)
        res3 = requests.get(url3, headers = self.headers)
        res3.status_code
        raw3Data = json.loads(res3.content)
        titlelist = ['公司名稱', '日期', '開盤', '高價', '低價', '收盤', '成交量', '外資', '投信', '自營商', '買賣超', '表單1', '表單2']
        time1 = time1
        time2 = time2
        dataDict = {}
        d_list = []
        #判斷今日是否開盤，沒有開盤則更新url編碼，避免格式抓取數據資料錯誤
        try:
            date = raw2Data['data'][0]['date'] 
            name = raw3Data['data'][0]['200009']
            hdata = rawData['data']['h'][0]
            ldata = rawData['data']['l'][0]
            odata = rawData['data']['o'][0]
            cdata = rawData['data']['c'][0]
            volume =rawData['data']['v'][0]
            total = raw2Data['data'][0]['totalNetBuySellVolume']
            a1 = raw2Data['data'][0]['foreignNetBuySellVolume']
            a2 = raw2Data['data'][0]['domesticNetBuySellVolume']
            a3 = raw2Data['data'][0]['dealerNetBuySellVolume']
            date = raw2Data['data'][0]['date']                    
            d_list = [str(name)] + [str(date)] + [str(odata)] + [str(hdata)] + [str(ldata)] + [str(cdata)] + [str(volume)] + [str(a1)] + [str(a2)] + [str(a3)] + [str(total)] + [time1] + [time2]
            # print(d_list)
            for a, b in zip(titlelist, d_list):
                dataDict[a] = b
            # print(dataDict)
            self.collection.insert(dataDict)
        except :
            name = raw3Data['data'][0]['200009']
            d_list = [str(name)] + ['0'] + ['0'] + ['0'] + ['0'] + ['0']+ ['0'] + ['0'] + ['0'] + ['0'] + ['0'] + [time1] + [time2]
            # print(d_list)
            for a, b in zip(titlelist, d_list):
                dataDict[a] = b
            # print(dataDict)
            self.collection.insert(dataDict)
