import requests
from lxml import etree
import psycopg2

def get_url():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}
    res = requests.get('https://www.aliexpress.com/',headers=headers)
    html = res.content
    parsehtml = etree.HTML(html)
    main_name_list = parsehtml.xpath('//dl/dt/span/a/text()')
    main_url_list = parsehtml.xpath('//dl/dt/span/a/@href')
    create_table('main_url')
    for n,i in enumerate(main_name_list):
        print((str(i.encode('utf-8'))[2:-1]).strip().replace(r'\xe2\x80\x99','’').replace('\'','’'),'https:'+main_url_list[n])
        save_to_DB('main_url',(str(i.encode('utf-8'))[2:-1]).strip().replace(r'\xe2\x80\x99','’').replace('\'','’'),main_url_list[n])

def get_sub_url():
    conn = psycopg2.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1', port='5432')
    # 创建cursor以访问数据库
    cur = conn.cursor()
    # 查询数据
    cur.execute("SELECT * FROM main_url")
    rows = cur.fetchall()
    for row in rows:
        print(row[1])
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}
        res = requests.get(row[1],headers=headers)
        html = res.content
        parsehtml = etree.HTML(html)
        sub_name_list = parsehtml.xpath('//dl/ul/li/a/text()')
        sub_url_list = parsehtml.xpath('//dl/ul/li/a/@href')
        create_table('sub_url')
        for n,i in enumerate(sub_name_list):
            print((str(i.encode('utf-8'))[2:-1]).strip().replace(r'\xe2\x80\x99','’').replace('\'','’'),'https:'+sub_url_list[n])
            save_to_DB('sub_url',row[0]+'-'+(str(i.encode('utf-8'))[2:-1]).strip().replace(r'\xe2\x80\x99','’').replace('\'','’'),sub_url_list[n])
    # 提交事务
    conn.commit()
    # 关闭连接
    conn.close()


def create_table(name):
    conn = psycopg2.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1', port='5432')
    # 创建cursor以访问数据库
    cur = conn.cursor()
    # 创建表
    try:
        cur.execute(
            'CREATE TABLE {} ('
            'NAME varchar(80),'
            'URL varchar(160)'
            ')'.format(name)
        )
    except:
        pass
    # 提交事务
    conn.commit()
    # 关闭连接
    conn.close()
def save_to_DB(type,name,url):
    conn = psycopg2.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1', port='5432')
    # 创建cursor以访问数据库
    cur = conn.cursor()
    # 插入数据
    cur.execute("INSERT INTO {} (NAME,URL) VALUES ('{}','{}')".format(type,name,'https:'+url))
    # 去重
    cur.execute('DELETE FROM {} WHERE ctid NOT IN (SELECT max(ctid) FROM {} GROUP BY NAME,URL);'.format(type,type))
    #  提交事务
    conn.commit()
    # 关闭连接
    conn.close()
get_url()
get_sub_url()
