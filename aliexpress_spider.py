import requests
from lxml import etree
import psycopg2
import time
import random
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import multiprocessing,threading
Tlock = threading.Lock()
Plock = multiprocessing.Lock()
class alexpress_spider(object):
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}
        self.proxies = [
            'http://180.108.120.155',
            'http://183.142.120.231',
            'http://27.29.44.49',
            'http://180.117.100.67',
            'http://112.87.68.104',
            'http://59.62.167.42',
            'http://182.44.221.106'
        ]
        self.n = 0
        self.count = 0
        self.all_data = []
    def ip_geter(self):
        # 代理服务器
        proxyHost = "http-dyn.abuyun.com"
        proxyPort = "9020"

        # 代理隧道验证信息
        proxyUser = "HCM58LJ79A15RH4D"
        proxyPass = "F55B7AC1BC4744F4"

        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }

        proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }

        return proxies
    def load_file(self):
        conn = psycopg2.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1', port='5432')
        cur = conn.cursor()
        cur.execute("SELECT * FROM crawl_category_conf")
        rows = cur.fetchall()
        executor = ThreadPoolExecutor(max_workers=1)
        for row in rows:
            if row[4] == '1'or row[4] == 1:
                url = row[1]
                if not row[2]:
                    executor.submit(self.get_data,url)
                else:
                    executor.submit(self.get_data,url,row[2],row[3])
            else:
                continue
        executor.shutdown(wait=True)
        conn.commit()
        conn.close()

    def get_data(self,url,low=None,high=None):
        executor2 = ThreadPoolExecutor(max_workers=20)
        for i in range(2):
            for page in range(1,102):
                executor2.submit(self.time_saver,page,url,low,high)
        executor2.shutdown(wait=True)

    def time_saver(self,page,url,low,high):
        params = {
            "page": str(page),
            'SortType': 'total_tranpro_desc',
        }
        if not low:
            params['minPrice'] = low
            params['maxPrice'] = high
        res = requests.get(url, params=params, headers=self.headers, proxies={'http': random.choice(self.proxies)})
        html = res.content
        parsehtml = etree.HTML(html)
        cat_name = url.split(r'/')[-1].split(r'.', 1)[0]
        executor2 = ThreadPoolExecutor(max_workers=50)
        for i in range(1, 49):
            executor2.submit(self.time_saver2,i,parsehtml,cat_name,low,high)
        executor2.shutdown(wait=True)

    def time_saver2(self,i,parsehtml,cat_name,low,high):
        price = parsehtml.xpath('//li[{}]/div/div/span/span[1]/text()'.format(i))[0].split('-')[0].split('$')[-1]
        votes = parsehtml.xpath('//*[@id="list-items"]/ul/li[{}]/div/div/div[@class="rate-history"]/a/text()'.format(i))[0][1:-1]
        orders = parsehtml.xpath('//li[{}]/div/div/div[@class="rate-history"]/span[3]/a/em/text()'.format(i))[0][10:-1]
        rating = parsehtml.xpath('//*[@id="list-items"]/ul/li[{}]/div/div/div/span[1]/@title'.format(i))[0][13:16]
        link = 'https:' + parsehtml.xpath('//li[{}]/div/div/h3/a/@href'.format(i))[0].split('?')[0]
        pid = link.split('/')[-1].split('.')[0]
        pic_res = requests.get(link, headers=self.headers, proxies={'http': random.choice(self.proxies)})
        pic_html = pic_res.content
        pic_parsehtml = etree.HTML(pic_html)
        pic_url = pic_parsehtml.xpath('//div/a/img/@src')[1]
        if pid and price and votes and orders and rating and pic_url and link and cat_name:
            self.all_in_one(pid, price, votes, orders, rating, pic_url, link, cat_name, low, high)

    def all_in_one(self,pid,price,votes,order,rating,pic_url,link,cat_name,low,high):
        # Tlock.acquire()
        self.n += 1
        if self.count != 500:
            self.count += 1
            self.all_data.append([pid,price,votes,order,rating,pic_url,link,cat_name])
            # print(self.n)
        else:
            self.n -= 1
            if low != None:
                print(cat_name, "price" + '[' + str(low) + ',' + str(high) + ']', 'spy', self.n)
            else:
                print(cat_name, "price" + '[all]', 'spy', self.n)
            self.count = 0
            self.save_data(self.all_data)
        # Tlock.release()

    def save_data(self,all_data):
        conn = psycopg2.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1', port='5432')
        cur = conn.cursor()
        for one_list in all_data:
            cur_time = time.strftime("%Y%m%d",time.localtime())
            cur.execute("INSERT INTO product_info_meta (pid,price,votes,orders,rating,pic_url,link,cat_name,date,cft )"
                         " VALUES ({},{},{},{},{},'{}','{}','{}','{}','{}') on conflict (cft) do nothing; "
                        .format(one_list[0],one_list[1],one_list[2],one_list[3],one_list[4],one_list[5],one_list[6],one_list[7],cur_time,one_list[0]+cur_time))

        self.all_data.clear()
        conn.commit()
        conn.close()
        print('进行了一次数据库插入')

if __name__ == '__main__':
    s = alexpress_spider()
    s.load_file()


