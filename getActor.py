import requests
from bs4 import BeautifulSoup
import os
# 导入pymysql模块
import pymysql

page = 1
prefix = 65

# 连接database
conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', password='123456', database='dmm', charset='utf8')
# 得到一个可以执行SQL语句的光标对象
cursor = conn.cursor()
# 定义要执行的SQL语句
insert = "INSERT INTO actor(name, javdb) VALUES (%s,%s);"
select = "select * from actor where javdb='/actors/2B6Wd'"




def get_jav_db_actor():
    global page
    r = requests.get('https://javdb6.com/actors?page=' + str(page))
    print('https://javdb6.com/actors?page=' + str(page))
    soup = BeautifulSoup(r.text, features="html.parser")
    box = soup.findAll(class_="actor-box")
    if (len(box)) > 0:
        for item in box:
            url = item.a['href']
            actor = item.a['title']
            cursor.execute("select * from actor where javdb= '" + url + "'")
            data = cursor.fetchall()
            if len(data) == 0:
                print(url + "-------" + actor)
                cursor.execute(insert, [actor, url])
        conn.commit()
        page += 1
        if page <= 30:
            get_jav_db_actor()
        else:
            cursor.close()
            conn.close()


def get_jav_library_actor():
    # http://www.b47w.com/cn/star_list.php?prefix=A&page=2
    global page
    global prefix
    r = requests.get('http://www.b47w.com/cn/star_list.php?prefix=' + chr(prefix) + '&page=' + str(page))
    print('http://www.b47w.com/cn/star_list.php?prefix=' + chr(prefix) + '&page=' + str(page))
    soup = BeautifulSoup(r.text, features="html.parser")
    elements = soup.findAll(class_="searchitem")
    if len(elements) > 0:
        for element in elements:
            link = element.a['href']
            actor = element.a.get_text()
            cursor.execute("SELECT * from javlibrary_actor where name= %s and url=%s", [actor, link])
            data = cursor.fetchall()
            if len(data) == 0:
                print(actor)
                cursor.execute("INSERT INTO javlibrary_actor(name,url) VALUES (%s,%s);", [actor, link])
        conn.commit()
        page += 1
        get_jav_library_actor()
    else:
        if prefix < 90:
            prefix += 1
            page = 1
            get_jav_library_actor()


get_jav_library_actor()
