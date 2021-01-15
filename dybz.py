import requests

def geturl():
    r = requests.get('http://www.kuaidoushe.com/video.php?_t=0.08053270802064239')
    url = r.headers.get('location')
    print(url)

geturl()
