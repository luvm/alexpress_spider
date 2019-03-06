import psycopg2

conn = psycopg2.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1', port='5432')
# 创建cursor以访问数据库
cur = conn.cursor()
# cur.execute('CREATE TABLE  crawl_category_conf('
#             'id SERIAL primary key,'
#             'cat_name varchar(50),'
#             'min_price  real,'
#             'max_price real,'
#             'stat integer,'
#             'date date)')
cur.execute("INSERT INTO crawl_category_conf (start_url,min_price,max_price)"
                    " VALUES ('https://www.aliexpress.com/category/200003482/dresses.html?spm=2114.11010108.101.3.650c649b6e2eAe&g=y','5','10')")
cur.execute("INSERT INTO crawl_category_conf (start_url)"
                    " VALUES ('https://www.aliexpress.com/category/5090301/mobile-phones.html?spm=2114.11010108.103.9.650c649bejxtgR&site=glo&pvId=200000233-200006062&attrRel=or&isrefine=y')")
cur.execute("INSERT INTO crawl_category_conf (start_url,min_price,max_price,stat)"
                    " VALUES ('https://www.aliexpress.com/category/200003482/dresses.html?spm=2114.11010108.101.3.650c649b6e2eAe&g=y','5','10','1')")
cur.execute("INSERT INTO crawl_category_conf (start_url,stat)"
                    " VALUES ('https://www.aliexpress.com/category/100003084/hoodies-sweatshirts.html?spm=2114.11010108.102.3.650c649bBG3phY','1')")
# cur.execute("INSERT INTO product_info_meta (pid,price,votes,rating,orders,pic_url,link,cat_name,date,conflict )"
#             " VALUES ({},{},{},{},{},'{}','{}','{}','{}','{}') on conflict (conflict) do nothing; "
#             .format(1,2,3,4,5,'6','7','8',20190603,'9'))
# 提交事务
conn.commit()
# 关闭连接
conn.close()