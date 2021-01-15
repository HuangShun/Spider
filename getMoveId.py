import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
# 导入pymysql模块
import pymysql

proxies = {
    'http': '127.0.0.1:10809',
    'https': '127.0.0.1:10809'
}
headers = {
    "cookie": '__utmc=125690133; __utmz=125690133.1610681343.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); app_uid=ygb3J2ABC/29tYxeMDuPAg==; i3_ab=292af1bd-0ded-4303-8103-8d11d7527b5b; age_check_done=1; _dga=GA1.3.465747007.1610681343; _dga_gid=GA1.3.1342164046.1610681379; i3_recommend_ab=78; _ga=GA1.3.465747007.1610681343; _gid=GA1.3.1150949085.1610681438; _ts_yjad=1610681445044; bypass_auid=db952231-e176-08cd-c9e4-b0b197674e89; adr_id=0dvIwjFWsJvCWRZYQG0c9DspyKfEeRDjZUlNo2yqTGoSmckN; _tdim=cde40d77-1fa2-46f4-f35a-568fc42f2daf; _im_id.1003537=6ee3f3545cd8439e.1610681469.1.1610681469.1610681469.; dmm_service=BFsBAx1FWwQCR0JdUkQFX0NeVwwEAx9KWFsNREEAVkIGCUNNFBRaQQJUAwIRfQ9TVwNzRXVvA0o9QAwVCFANEgkIXVASFFpbAlYBA0AMUg1DE19TRxtfSlhVDURCBFRbBAZVG11FWwYCR0JXQUJEDBJfAQwSSwVXCQtZARBeSk0_; __utma=125690133.465747007.1610681343.1610681343.1610691595.2; __utmb=125690133.0.10.1610691595; AMP_TOKEN=%24NOT_FOUND; adpf_uid=CMLmfTpVLeOeMeCz; ckcy=1; mbox=check#true#1610691689|session#1610691594948-770496#1610693489; _gali=main-src'
}
actor = '宇都宮しをん'
jav_db_link = ''
jav_library_link = ''
page = 1
# 连接database
conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', password='123456', database='dmm', charset='utf8')
# 得到一个可以执行SQL语句的光标对象
cursor = conn.cursor()
# 定义要执行的SQL语句
insert = "INSERT INTO movie(actor, javdb, dmmid, dvdid, title, download,javlibrary) VALUES (%s,%s,%s,%s,%s,%s,%s);"


def start():
    global jav_db_link
    global jav_library_link
    global actor
    cursor.execute("select * from actor where name like '%" + actor + "%'")
    result = cursor.fetchall()
    if len(result) == 1:
        actor = result[0][1]
        jav_db_link = result[0][2]
        jav_library_link = result[0][3]
        get_jav_db_movie()
    else:
        print("查询失败")


def get_jav_db_movie():
    global page
    r = requests.get('https://javdb6.com' + jav_db_link + '?page=' + str(page))
    print('https://javdb6.com' + jav_db_link + '?page=' + str(page))
    soup = BeautifulSoup(r.text, features="html.parser")
    elements = soup.findAll(class_='grid-item')
    if len(elements) > 0:
        for element in elements:
            jav_db_url = element.a['href']
            title = element.a['title']
            dvd_id = element.find(class_='uid').get_text()
            if not check_is_add(dvd_id):
                print(actor, jav_db_url, '', dvd_id, title, 0)
                cursor.execute(insert, [actor, jav_db_url, '', dvd_id, title, 0, ''])
        conn.commit()
        page += 1
        get_jav_db_movie()
    else:
        page = 1
        get_jav_library_movie()


def get_jav_library_movie():
    global page
    r = requests.get('http://www.b47w.com/cn/vl_star.php?&mode=2&s=' + jav_library_link + '&page=' + str(page))
    print('http://www.b47w.com/cn/vl_star.php?&mode=2&s=' + jav_library_link + '&page=' + str(page))
    soup = BeautifulSoup(r.text, features="html.parser")
    elements = soup.findAll(class_='video')
    if len(elements) > 0:
        for element in elements:
            jav_library_url = element.a['href']
            title = element.find(class_='title').get_text()
            dvd_id = element.find(class_='id').get_text()
            if not check_is_add(dvd_id):
                print(actor, '', '', dvd_id, title, 0, jav_library_url)
                cursor.execute(insert, [actor, '', '', dvd_id, title, 0, jav_library_url])
        conn.commit()
        page += 1
        get_jav_library_movie()
    else:
        cursor.close()
        conn.close()


def get_seesaa_movie():
    global page
    r = requests.get('http://sougouwiki.com/d/%B0%C2%E3%B7%A4%E9%A4%E9')
    soup = BeautifulSoup(r.text, features="html.parser")
    elements = soup.find(class_='wiki-section-body-1').findAll(class_='outlink')
    for element in elements:
        if not element['href'].find('pics.dmm.co.jp') == -1:
            arr = element['href'].split("/")
            cid = arr[len(arr) - 2]
            if not check_is_add_by_cid(cid):
                print(cid)


def check_is_add_by_cid(cid):
    cursor.execute("select * from movie where dmmid= '" + cid + "'")
    result = cursor.fetchall()
    if len(result) == 0:
        return False
    else:
        return True


def check_is_add(dvd_id):
    cursor.execute("select * from movie where dvdid= '" + dvd_id + "'")
    result = cursor.fetchall()
    if len(result) == 0:
        return False
    else:
        return True


def trans():
    cursor.execute("select * from movie where dmmid = ''")
    result = cursor.fetchall()
    print("共" + str(len(result)) + "部")
    for item in result:
        print(item[4] + " :start")
        r = requests.get('https://www.dmm.co.jp/mono/dvd/-/search/=/searchstr=' + item[3] + "/", proxies=proxies,
                         headers=headers)
        soup = BeautifulSoup(r.text, features="html.parser")
        node = soup.find(id='list')
        if node:
            elements = node.findAll(class_='tmb')
            for element in elements:
                path = element.a['href']
                cid = path.split('cid=')[1].split("/")[0]
                title = element.find(class_='img').img['alt']
                local_cid = item[3].replace('-', '').lower()
                if title == item[4] or cid == local_cid:
                    sql = "UPDATE movie SET dmmid = %s WHERE dvdid = %s "
                    cursor.execute(sql, (cid, item[3]))
                    conn.commit()
                    print(cid + " :finish")
    cursor.close()
    conn.close()


get_seesaa_movie()
