from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core import serializers
import requests
import json

from .models import stockList

#for stock_predict
from bs4 import BeautifulSoup
import pandas as pd
#import utility as util

@require_http_methods(["GET"])
def stockSelectList(request):
    dataSet = stockList.objects.all()
    print('123')
    response = {}
    try:
        response['msg'] = 'success'
        response['error_num'] = 0
        response['result'] = json.loads(serializers.serialize("json", dataSet))
    except  Exception as e:
        response['msg'] = str(e)
        response['error_num'] = 1

    return JsonResponse(response)


@require_http_methods(["GET"])
def stock_predict(request):
    result_lists = [] #產製報表結果
    # stock_code_array = ['9911', '2382', '2884', '2886', '2330','4104','9939','3029','2471','2453','5439']
    stockArrStr = request.GET.get('stockCode')
    print('stockArrStr=='+str(stockArrStr))
    stock_code_array = stockArrStr.split(',')
    print('stock_code_array=='+str(stock_code_array))

    parameter_array = ['每股淨值(F)(TSE公告數)','ROE(A)-稅後', 'ROE(A)─稅後','最低本益比','最高本益比']
    for i in stock_code_array:
        stock_code = i
    #for i in range(0, 9999) :
        # stock_code = str(i).zfill(4)
        try:
            print('i==' + i + ' ,stock_code==' + str(stock_code))
            lists = [] #過程驗證數據(含公式內使用參數的明細<8年內>)
            ## 各項數據獲取
            url = "https://jdata.yuanta.com.tw/z/zc/zcr/zcra/zcra_" + stock_code + ".djhtm"
            r = requests.get(url)
            soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser
            # #取出公司名字
            company = soup.find("div", {"id": "oScrollHead"}).text
            
            company = company.split('\n')[1][:company.index(')')-1]
            
            #找到我要的指標from 上述網址
            # dataRow = [7,12,26] # 7:年、12:ROE(稅後)、26:每股淨值
            dataRow = range(7, 35)
            title = []
            print('flag1')
            for i in dataRow:
                mini_list = []
                for j in soup.select("div")[i].text.split('\n')[1:]: #只取我要的部分就好
                    # print(j)
                    if j != '' and soup.select("div")[i].text.split('\n')[1:][0] in parameter_array:
                        mini_list.append(j) 
                if len(mini_list) > 0 : 
                    lists.append(mini_list)         
                if i == 7 :
                    title.append(mini_list)
            print('flag2')
                
            #找到我要的指標from 下述網址   
            url = "https://jdata.yuanta.com.tw/z/zc/zca/zca_" + stock_code + ".djhtm"  
            r = requests.get(url)
            soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser
            date = soup.select("tr")[3].text
            date = date[date.find('最近交易日')+6 : date.find('最近交易日')+11] #抓出日期
            stock_price_array = soup.select("tr")[4].text.split('\n')[1:-1]
            stock_price_now = stock_price_array[7] # 最新收盤價
            dataRow = [4,5] # 4:最高本益比、5:最低本益比
            for i in dataRow:
                mini_list = []
                for j in soup.select("tr")[27].text.split('\n\n')[i].split('\n')[1:]: #只取我要的部分就好
                    if j != '' :
                        mini_list.append(j)  
                lists.append(mini_list)    
            
            print('flag3')
            # title[0][0] = company    
            # df = pd.DataFrame(lists, columns=title[0])
            # df = df.astype(str)
            # df = df.apply(lambda s:s.str.replace(',',''))
            
            est_ROE = lists[0][1] # 預估ROE 
            NAV = lists[1][1] #淨值
            reason_PE = lists[3][1] #合理(低)本益比
            
            # 合理價及股災價計算
            reasonP = 0.92 # 1.14 # 合理價本益比估計比例(我自己估的)
            low_P = 0.82 # 1.01 # 股災價本益比估計比例(我自己估的)
            reason_price = round(cal_Stock_reason_price(est_ROE, NAV, reason_PE, reasonP), 2) #合理價
            disaster_price = round(cal_Stock_reason_price(est_ROE, NAV, reason_PE, low_P), 2) #股災價
            
            print('flag4')
            result_list = []
            result_list.append(company) #公司名稱及代號
            result_list.append(stock_price_now) #最新股價
            result_list.append(date) #最新股價日期
            result_list.append(reason_price) #合理價
            result_list.append(disaster_price) #股災價
            result_list.append(reason_price >= float(stock_price_now))
            result_list.append(disaster_price >= float(stock_price_now))
            # 避免被近期(前季~一年內)等離峰值影響，需適當判斷並乘以固定比例得出更恰當的合理進場價錢
            # 或者應該抓平穩時期(至少不要大漲時)的合理本益比及預估ROE => 避免受大漲影響導致合理價失真
            # 2022-11-06 因有些股易受指數影響，故本益比需抓低，不易受影響者則須高一些，故分兩種價格來看
            reasonP = 1.1 # 1.14 # 合理價本益比估計比例(我自己估的)
            low_P = 0.99 # 1.01 # 股災價本益比估計比例(我自己估的)
            reason_price = round(cal_Stock_reason_price(est_ROE, NAV, reason_PE, reasonP), 2) #合理價
            disaster_price = round(cal_Stock_reason_price(est_ROE, NAV, reason_PE, low_P), 2) #股災價
            result_list.append(reason_price) #合理價
            result_list.append(disaster_price) #股災價
            result_list.append(reason_price >= float(stock_price_now))
            result_list.append(disaster_price >= float(stock_price_now))
            
            result_lists.append(result_list)
            print('flag5')
        except:
            print('報錯代碼:' + stock_code)

    response = {}
    try:
        print('result_lists==' + str(result_lists))
        response['list']  = result_lists
        response['msg'] = 'success'
        response['error_num'] = 0
    except  Exception as e:
        response['msg'] = str(e)
        response['error_num'] = 1
    return JsonResponse(response)
        #df_result = pd.DataFrame(result_lists, 
        # columns=['公司名稱','最新股價','最新股價日期','易受影響股合理價','易受影響股股災價','低於合理價','低於股災價',
        #                                            '不易受影響股合理價','不易受影響股股災價','低於合理價','低於股災價'])
        #df_result.to_excel('stock_Ref_result.xlsx')


def cal_Stock_reason_price(est_ROE, NAV, reason_PE, percent) :
    #合理價與股災價只差在本益比(reason_PE)    
    # percent，因預估目前，但這些數據皆是過去的，理論上正常公司會越來越好，
    # 所以縱使是股災價的預估本益比也應該比過去好
    return (float(est_ROE) * 0.01) * float(NAV) * (float(reason_PE) * percent)