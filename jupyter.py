import pymongo
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import matplotlib.dates as mdate
import matplotlib.patches as mpatches
from datetime import datetime
pd.set_option('display.max_columns', 3000)
pd.set_option('display.width', 3000)
sns.set(font = ['Microsoft YaHei'])

client = pymongo.MongoClient('localhost', 27017)
db = client.StockData
collection = db.StockDec

result = collection.find()
df = pd.DataFrame([i for i in result]).drop(columns="_id")

# df_2 = df["日期"]
# df_2 = df_2.astype("string")
# L = []
# for i in df_2:
#     str(i).replace('-','/')  
df = df[df["日期"] != '0']
df["日期"] = pd.to_datetime(df["日期"])
cList = ["開盤","高價","低價","收盤", "成交量"]
for i in df.columns:
    if i in cList:
        df[i] = df[i].astype("float")
aList = ["投信","外資","自營商","買賣超", "加總"]
for i in df.columns:
    if i in aList:
        df[i] = df[i].astype("int")

def adjustDate():
    global df
    alldaylocator = mdate.WeekdayLocator()#設定日期
    plt.gcf().autofmt_xdate()#自動調整刻度
    plt.gca().xaxis.set_major_locator(alldaylocator)#設定美日為主要刻度
    plt.gca().xaxis.set_major_formatter(mdate.DateFormatter('%m/%d'))#設定時間 mm-dd  
    plt.xlim(list(df["日期"])[100], list(df["日期"])[-1])


mid = df["收盤"].rolling(26).mean()
tim2 = df["收盤"].rolling(20).std()
upper = mid + 2*tim2
lower = mid - 2*tim2
sma5 = df["收盤"].rolling(5).mean()
sma20 = df["收盤"].rolling(20).mean()
sma100 = df["收盤"].rolling(100).mean()
volume = df["成交量"].rolling(5).mean()

result = plt.figure(figsize = (30, 25))
result.tight_layout()
result.suptitle(str(list(df["公司名稱"])[0])+'\n'+str(list(df["日期"])[-1])[:-8].replace('-', '/')+'\n'+
                '  開 = '+str(list(df["開盤"])[-1])+'  高 = '+str(list(df["高價"])[-1])+'  低 = '+
                str(list(df["低價"])[-1])+'  收 = '+str(list(df["收盤"])[0])+'\n'+
                '  三大法人買賣超張數      外資 : '+str(list(df["外資"])[0])+
                '  投信 : '+str(list(df["投信"])[0])+
                '  自營商 : '+str(list(df["自營商"])[0]), fontsize = 30)
ax0 = plt.subplot2grid((5,1), (0,0), rowspan=2)
ax0.tick_params(pad=1, labelsize = 10)
rise = df["收盤"] - df["開盤"] > 0
fall = df["收盤"] - df["開盤"] < 0
srise = df["買賣超"] > 0
sfall = df["買賣超"] < 0
fa = np.zeros(df.shape[0],dtype = "3f4")
fc = np.zeros(df.shape[0],dtype = "3f4")
fc[rise] = (1,0,0)
fc[fall] = (0,1,0)
fa[srise] = (1,0,0)
fa[sfall] = (0,1,0)
ax0.bar(df["日期"], df["高價"] - df["低價"], 0.1, df["低價"], color = fc, edgecolor = fc)
ax0.bar(df["日期"], df["收盤"] - df["開盤"], 1, df["開盤"], color = fc, edgecolor = fc)
ax0.plot(df['日期'], sma5, color = "sienna", alpha = 0.6, label = 'SMA(5)')
ax0.plot(df['日期'], sma20, color = "magenta", alpha = 0.6, label = 'SMA(20)')
ax0.plot(df['日期'], sma100, color = "cyan", alpha = 0.6, label = 'SMA(100)')
plt.legend()
high = max(df["高價"]) + 5
low = min(df["低價"]) - 5
plt.ylim(low, high)
ax0.grid(axis = "y", color = "k", linestyle = "--", alpha = 0.5)
adjustDate()
ax3 = plt.subplot2grid((5,1), (2,0))
ax3.plot(df['日期'], df["收盤"], color = "red", alpha = 0.8)
ax3.plot(df['日期'], mid, color = "blue", alpha = 0.6, label = '20MA')
ax3.plot(df['日期'], upper, color = "orange", alpha = 0.6, label = 'Upper BB')
ax3.plot(df['日期'], lower, color = "purple", alpha = 0.6, label = 'Lower BB')
plt.legend()
high = max(df["高價"]) + 25
low = min(df["低價"]) - 25
plt.ylim(low, high)
ax3.grid(axis = "y", color = "k", linestyle = "--", alpha = 0.5)
adjustDate()

ax2 = plt.subplot2grid((5,1), (3,0))
ax2.bar(df["日期"], df["成交量"], 0.8, color = fa, edgecolor = fa)
ax2.plot(df['日期'], volume, color = "blue", alpha = 0.6, label = '成交量')
high = max(df["成交量"]) +5000
plt.legend()
ax2.set_ylim([0, high])
ax2.grid(axis = "y", color = "k", linestyle = "--", alpha = 0.5)
adjustDate()

ax1 = plt.subplot2grid((5,1), (4,0))
ax1.bar(df["日期"], df["買賣超"], 0.8, color = fa, edgecolor = fa)
ax1.plot(df['日期'], df["買賣超"], color = "blue", alpha = 0, label = '單日買賣超數量')
ax1.plot(df["日期"], df["外資"], color = 'c', label = '外資')
ax1.plot(df["日期"], df["投信"], color = 'b', label = '投信')
ax1.plot(df["日期"], df["自營商"], color = 'orange', label = '自營商')
plt.legend()

high = max(df["買賣超"]) +5000
low = min(df["買賣超"]) - 5000
ax1.set_ylim([low, high])
ax1.grid(axis = "y", color = "k", linestyle = "--", alpha = 0.5)
adjustDate()
plt.show()
