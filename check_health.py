import time, requests
url='http://127.0.0.1:5000/api/health'
for i in range(15):
    try:
        r=requests.get(url, timeout=3)
        print('status', r.status_code, 'body', r.text)
        break
    except Exception as e:
        print('try', i, 'err', repr(e))
        time.sleep(1)
else:
    print('no response')
