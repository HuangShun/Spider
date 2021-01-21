import requests
import pymysql
from retrying import retry
from bs4 import BeautifulSoup
import urllib.parse
import os
# 导入pymysql模块


proxies = {
    'http': '127.0.0.1:10809',
    'https': '127.0.0.1:10809'
}
headers = {
    "cookie": '__utmc=125690133; __utmz=125690133.1610681343.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); '
              'app_uid=ygb3J2ABC/29tYxeMDuPAg==; i3_ab=292af1bd-0ded-4303-8103-8d11d7527b5b; age_check_done=1; '
              '_dga=GA1.3.465747007.1610681343; _dga_gid=GA1.3.1342164046.1610681379; i3_recommend_ab=78; '
              '_ga=GA1.3.465747007.1610681343; _gid=GA1.3.1150949085.1610681438; _ts_yjad=1610681445044; '
              'bypass_auid=db952231-e176-08cd-c9e4-b0b197674e89; '
              'adr_id=0dvIwjFWsJvCWRZYQG0c9DspyKfEeRDjZUlNo2yqTGoSmckN; _tdim=cde40d77-1fa2-46f4-f35a-568fc42f2daf; '
              '_im_id.1003537=6ee3f3545cd8439e.1610681469.1.1610681469.1610681469.; '
              'dmm_service'
              '=BFsBAx1FWwQCR0JdUkQFX0NeVwwEAx9KWFsNREEAVkIGCUNNFBRaQQJUAwIRfQ9TVwNzRXVvA0o9QAwVCFANEgkIXVASFFpbAlYBA0AMUg1DE19TRxtfSlhVDURCBFRbBAZVG11FWwYCR0JXQUJEDBJfAQwSSwVXCQtZARBeSk0_; __utma=125690133.465747007.1610681343.1610681343.1610691595.2; __utmb=125690133.0.10.1610691595; AMP_TOKEN=%24NOT_FOUND; adpf_uid=CMLmfTpVLeOeMeCz; ckcy=1; mbox=check#true#1610691689|session#1610691594948-770496#1610693489; _gali=main-src '
}

jav_db_header = {
    "cookie": '_jdb_session=smsQ5dWt4i8CFcTAtcdSRllfyDwqbyrYXrq6dbvAPrAPKALUht%2FubS27LrfHt3oy%2FS'
              '%2BrjebuZW5CygQql3J4yb4AXlx%2B%2F%2B2wCvofxlAUtk9VkmV7vlCT9RVwM2v4tVxYBGygs5dm42di3ByeKXyE51F'
              '%2Fke1J0iaXpl5kwx8ixZpvreDRyhvkgSShAIKFO8PoppVUHn2Mi6ki3BASrjxBec0O5Anw2naEGeBs3T9OZCWaKNd48kSeucNSbMv8lLa2QmfP5LdK3eK9H474rasr%2B%2BBqQhpRrQKxw%2FRsRcHdFjQohUFEo%2BlDjGds%2F%2FkkzEe40Vu8jldYXGeIFoA8b%2FF%2BO9e0--eG5OsfUiO2WGgYGq--Vh8Rts0QK58tHdmzVpR26A%3D%3D; path=/; expires=Thu, 04 Feb 2021 08:26:23 -0000; HttpOnly; SameSite=Lax '
}

keyword = '田中瞳'
main_actor = ''
jav_db_link = ''
jav_library_link = ''
page = 1

conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', password='123456', database='dmm', charset='utf8')
cursor = conn.cursor()
jav_db_insert = "INSERT INTO movie(main_actor,cover, main_image, dvd_id, dmm_id, title, publish_date, duration, " \
                "javdb_dvd_series_url, javdb_series, javdb_series_url, javdb_maker, javdb_maker_url, javdb_actor, " \
                "javdb_tag,jav_db_url,javlibrary_publish,javlibrary_publish_url, javlibrary_actor, javlibrary_url,  " \
                "javlibrary_tag,download,subtitles)" \
                " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); "

jav_library_update = 'UPDATE movie SET cover = %s,javlibrary_publish = %s,javlibrary_publish_url = ' \
                     '%s,javlibrary_actor = %s ,javlibrary_url = %s , javlibrary_tag = %s where dvd_id = %s'


def start():
    global jav_db_link
    global jav_library_link
    global main_actor
    cursor.execute("select * from javdb_actor where name like '%" + keyword + "%'")
    res = cursor.fetchall()
    if len(res) == 1:
        main_actor = res[0][1]
        jav_db_link = res[0][2]
    else:
        print("javdb查询失败")
        return

    cursor.execute("select * from javlibrary_actor where name = '" + keyword + "'")
    result = cursor.fetchall()
    if len(result) == 1:
        jav_library_link = result[0][2]
    else:
        print("javlibrary查询失败")
        return
    get_jav_db_movie()
    # get_jav_library_movie()


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
                get_jav_ab_detail(title, jav_db_url)
        page += 1
        get_jav_db_movie()
    else:
        page = 1
        get_jav_library_movie()


#     https: // pics.dmm.co.jp / mono / movie / adult / venu896 / venu896pl.jpg
# https://pics.dmm.co.jp/digital/video/venu00896/venu00896ps.jpg
# https://pics.dmm.co.jp/mono/movie/adult/venx001/venx001pl.jpg
# https://pics.dmm.co.jp/mono/movie/adult/h_1495bank029/h_1495bank029pl.jpg
# https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=mide726/?i3_ref=ad&dmmref=pickup001&i3_ord=3
# https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=mide00726/?i3_ref=list&i3_ord=1
@retry
def get_jav_ab_detail(title, jav_db_url):
    r = requests.get('https://javdb6.com' + jav_db_url, headers=jav_db_header, timeout=10)
    # print('https://javdb6.com' + jav_db_url)
    soup = BeautifulSoup(r.text, features="html.parser")
    container = soup.find(class_='movie-info-panel')
    video_info = soup.find(class_='video-panel-info')
    panel = video_info.findAll(class_='panel-block')
    # print(panel)

    cover = ''
    main_image = container.find(class_='video-cover')['src']
    dvd_id = container.find(class_='copy-to-clipboard')["data-clipboard-text"]
    dmm_id = ''
    dvd_id_url = get_jav_db_dvd_series_url(panel)
    publish_date = get_jav_db_date(panel)
    duration = get_jav_db_duration(panel)
    jav_db_actor = get_jav_db_actor(panel)
    series = get_jav_db_series(panel)[0]
    series_url = get_jav_db_series(panel)[1]
    maker = get_jav_db_maker(panel)[0]
    maker_url = get_jav_db_maker(panel)[1]
    tag = get_jav_db_tag(panel)
    print(main_actor, cover, main_image, dvd_id, dmm_id, title, publish_date, duration, dvd_id_url, series, series_url,
          maker, maker_url, jav_db_actor, tag)
    cursor.execute(jav_db_insert, (
        main_actor, cover, main_image, dvd_id, dmm_id, title, publish_date, duration, dvd_id_url, series, series_url,
        maker, maker_url, jav_db_actor, tag, jav_db_url, '', '', '', '', '', 0, 0))
    conn.commit()


def get_jav_db_dvd_series_url(panels):
    panel = get_jav_db_select_panel('番號:', panels)
    if panel and panel.a:
        try:
            content = panel.a['href']
            return content
        except KeyError:
            return ''


def get_jav_db_actor(panels):
    _actor = []
    panel = get_jav_db_select_panel('演員:', panels)
    _actors = panel.findAll('a')
    if len(_actors) > 0:
        for item in _actors:
            _actor.append(item.get_text() + "-" + item['href'])
        return '|'.join(_actor)
    else:
        return ''


def get_jav_db_date(panels):
    panel = get_jav_db_select_panel('日期:', panels)
    content = panel.span.get_text()
    return content


def get_jav_db_duration(panels):
    panel = get_jav_db_select_panel('時長:', panels)
    content = panel.span.get_text().split(" ")
    return content[0]


def get_jav_db_series(panels):
    panel = get_jav_db_select_panel('系列:', panels)
    if panel and panel.a:
        series = panel.a.get_text()
        url = panel.a['href']
        return series, url
    else:
        return '', ''


def get_jav_db_maker(panels):
    panel = get_jav_db_select_panel('片商:', panels)
    if panel and panel.a:
        maker = panel.a.get_text()
        url = panel.a['href']
        return maker, url
    return '', ''


def get_jav_db_tag(panels):
    _tag = []
    panel = get_jav_db_select_panel('類別:', panels)
    if panel:
        _tags = panel.findAll('a')
        if len(_tags) > 0:
            for item in _tags:
                _tag.append(item.get_text() + "-" + item['href'])
        return '|'.join(_tag)
    return ''


def get_jav_db_select_panel(item, panels):
    for panel in panels:
        if panel.strong and panel.strong.get_text() == item:
            return panel


def get_jav_library_movie():
    global page
    r = requests.get('http://www.b47w.com/tw/' + jav_library_link + '&page=' + str(page) + "&mode=2")
    print('http://www.b47w.com/tw/' + jav_library_link + '&page=' + str(page) + "&mode=2")
    soup = BeautifulSoup(r.text, features="html.parser")
    elements = soup.findAll(class_='video')
    if len(elements) > 0:
        for element in elements:
            jav_library_url = element.a['href']
            dvd_id = element.find(class_='id').get_text()
            title = element.find(class_='title').get_text()
            cover = element.img['src']
            if not check_is_full(dvd_id):
                get_jav_library_detail(title, jav_library_url.split('/')[1], 'https:' + cover)
        page += 1
        get_jav_library_movie()


def get_jav_library_detail(title, jav_library_url, cover):
    r = requests.get('http://www.b47w.com/tw/' + jav_library_url)
    print('http://www.b47w.com/tw/' + jav_library_url)
    soup = BeautifulSoup(r.text, features="html.parser")
    container = soup.find(id='video_jacket_info')
    main_image = 'https' + container.find(id='video_jacket_img')['src']
    dvd_id = container.find(id='video_id').find(class_='text').get_text()
    dmm_id = ''
    dvd_id_url = ''
    publish_date = container.find(id='video_date').find(class_='text').get_text()
    duration = container.find(id='video_length').find(class_='text').get_text()
    jav_library_actor = get_jav_library_info(container, 'video_cast', 'cast')
    series = ''
    series_url = ''
    maker = container.find(id='video_maker').a.get_text()
    maker_url = container.find(id='video_maker').a['href']
    if container.find(id='video_label').a:
        publish = container.find(id='video_label').a.get_text()
        publish_url = container.find(id='video_label').a['href']
    else:
        publish = ''
        publish_url = ''
    tag = get_jav_library_info(container, 'video_genres', 'genre')
    if check_is_add(dvd_id):
        print("update", dvd_id, cover, publish, publish_url, jav_library_actor, jav_library_url)
        cursor.execute(jav_library_update,
                       (cover, publish, publish_url, jav_library_actor, jav_library_url, tag, dvd_id))
    else:
        print("insert", dvd_id, main_actor, cover, main_image, dvd_id, dmm_id, title, publish_date, duration,
              dvd_id_url, series, series_url, maker, maker_url, '', '', '', publish, publish_url, jav_library_actor,
              jav_library_url, tag, 0, 0)
        cursor.execute(jav_db_insert, (
            main_actor, cover, main_image, dvd_id, dmm_id, title, publish_date, duration, dvd_id_url, series,
            series_url, maker, maker_url, '', '', '', publish, publish_url, jav_library_actor, jav_library_url, tag, 0,
            0))
    conn.commit()


def get_jav_library_info(container, type, detail):
    _actor = []
    content = container.find(id=type).findAll(class_=detail)
    if len(content) > 0:
        for item in content:
            _str = item.a.get_text() + "-" + item.a['href'].split('=')[1]
            _actor.append(_str)
        return "|".join(_actor)
    else:
        return ''


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
    cursor.execute("select * from movie where dmm_id= '" + cid + "'")
    result = cursor.fetchall()
    if len(result) == 0:
        return False
    else:
        return True


def check_is_add(dvd_id):
    cursor.execute("select * from movie where dvd_id= '" + dvd_id + "'")
    result = cursor.fetchall()
    if len(result) == 0:
        return False
    else:
        return True


def check_is_full(dvd_id):
    cursor.execute("select * from movie where dvd_id= '" + dvd_id + "' and javlibrary_url != ''")
    result = cursor.fetchall()
    if len(result) == 0:
        return False
    else:
        return True


def trans():
    cursor.execute("select * from movie where dmm_id = ''")
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
                    sql = "UPDATE movie SET dmm_id = %s WHERE dvd_id = %s "
                    cursor.execute(sql, (cid, item[3]))
                    conn.commit()
                    print(cid + " :finish")
    cursor.close()
    conn.close()


start()
