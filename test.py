import csv
import time
import urllib.request
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import pymongo
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}
url = 'https://beijing.8684.cn/'
url_list = url + '/list%d'

for k  in  range(1,10):
    url1=url_list % k
    print(url1)

def get_page_wangFan(wangFan_road_ol):
    wangFan_road_tmp = wangFan_road_ol[0].find_all('li')
    wangFan_road_lst = []
    for road in wangFan_road_tmp:
        temp = road.find('a')
        if temp is None:
            continue
        else:
            wangFan_road_lst.append(temp)

    wangFan_road_lst.pop()
    try:
        wangFan_road_tmp = wangFan_road_ol[1].find_all('li')
    except:
        wangFan_road_tmp = None

    if wangFan_road_tmp is not None:
        for road in wangFan_road_tmp:
            temp = road.find('a')
            if temp is None:
                continue
            else:
                wangFan_road_lst.append(temp)

    wangFan_road = ""
    for r in wangFan_road_lst:
        wangFan_road += r.string + ', '
    return wangFan_road

def get_page_info(urls):
    rep = urllib.request.Request(url=urls, headers=headers)
    html = urllib.request.urlopen(rep)
    soup = bs(html.read(), 'html.parser')
    bus_name = soup.select('div.info > h1.title > span')[0].string
    bus_type = soup.select('div.info > h1.title > a.category')[0].string
    time_select = soup.select('div.info > ul.bus-desc > li')
    bus_time = time_select[0].string
    bus_ticket = time_select[1].string
    gongsi = time_select[2].find('a').string
    gengxin = time_select[3].find('span').string
    try:
        licheng = soup.find('div', class_="change-info mb20").string
    except:
        licheng = None
    wang_info1 = bus_name
    wang_info2 = soup.select('div > div > div.trip')[0].string
    wang_total = soup.select('div > div > div.total')[0].string
    wang_road_ol = soup.find_all('div', class_='bus-lzlist mb15')[0].find_all('ol')
    wang_road = get_page_wangFan(wang_road_ol)
    try:
        fan_info1 = bus_name
        fan_info2 = soup.select('div > div > div.trip')[1].string
        fan_total = soup.select('div > div > div.total')[1].string
        fan_road_ol = soup.find_all('div', class_='bus-lzlist mb15')[1].find_all('ol')
        fan_road = get_page_wangFan(fan_road_ol)
    except IndexError:
        fan_info1 = None
        fan_info2 = None
        fan_total = None
        fan_road = None
    result_lst = [bus_name, bus_type, bus_time, bus_ticket, gongsi, gengxin, licheng, wang_info1, wang_info2,
                  wang_total, wang_road, fan_info1, fan_info2, fan_total, fan_road]
    print(result_lst)
    with open('BusInfo.csv', 'a', newline="", encoding='utf-8') as cs:
        writer = csv.writer(cs)
        writer.writerow(result_lst)
        print("-"*80)
        time.sleep(5)
    client = pymongo.MongoClient()
    db = client["BusDatabase"]
    col = db["BusCollection"]
    with client.start_session() as session:
        col.insert_one({
            "bus_name": bus_name,
            "bus_type": bus_type,
            "bus_time": bus_time,
            "bus_ticket": bus_ticket,
            "gongsi": gongsi,
            "gengxin": gengxin,
            "licheng": licheng,
            "wang_info1": wang_info1,
            "wang_info2": wang_info2,
            "wang_total": wang_total,
            "wang_road": wang_road,
            "fan_info1": fan_info1,
            "fan_info2": fan_info2,
            "fan_total": fan_total,
            "fan_road": fan_road
        }, session=session)
        client.close()
def get_page_url(urls):
    rep = urllib.request.Request(urls, headers=headers)
    html = urllib.request.urlopen(rep)
    btsoup = bs(html.read(), 'html.parser')
    lu = btsoup.find('div', class_='list clearfix')
    hrefs = lu.find_all('a')
    for i in hrefs:
        print(i)
        urls = urljoin(url, i['href'])
        print(urls)
        get_page_info(urls)


if __name__ == '__main__':
    for k in range(1, 2):
        urls = url_list % k
        time.sleep(3)
        get_page_url(urls)
