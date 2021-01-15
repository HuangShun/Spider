import requests
import os
# 导入pymysql模块
import pymysql

# 连接database
conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', password='123456', database='douyin', charset='utf8')
# 得到一个可以执行SQL语句的光标对象
cursor = conn.cursor()
# 定义要执行的SQL语句
insert = "REPLACE INTO videos(url) VALUES (%s);"

path = 'C:/Users/Admin/Desktop/taitaiorder'
videos = set()
download = set()
for name in os.listdir(path):
    download.add(name.split('.')[0])


def geturl():
    try:
        r = requests.get('http://www.kuaidoushe.com/video.php?_t=0.08053270802064239', allow_redirects=False)
        url = r.headers.get('location')
        print(url)
        arr = url.split('_')[0].split("=")[0].split("/")
        filename = arr[len(arr) - 1]
        cursor.execute(insert, [url])
        if filename not in download:
            videos.add(url)
        if len(videos) < 500:
            geturl()
        else:
            conn.commit()
            cursor.close()
            conn.close()
    except:
        geturl()


def download_video(download_url, title_list):  # 写入mp4
    title = title_list + '.mp4'
    print(title)
    response = requests.get(download_url)
    f = open(title, 'wb')
    f.write(response.content)
    print("%s is over" % title)
    f.close()


geturl()
