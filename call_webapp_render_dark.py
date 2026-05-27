import requests

url = 'http://127.0.0.1:5000/api/render'
files = {'file': open('he test.xlsx','rb')}
# include dark_mode to request a dark image
data = {'sheet': '', 'title': 'debug-webapp-test', 'scale_mode':'auto', 'dark_mode':'on'}
resp = requests.post(url, files=files, data=data)
if resp.status_code == 200 and resp.headers.get('Content-Type','').startswith('image'):
    open('outputs/webapp_response_dark.png','wb').write(resp.content)
    print('Wrote outputs/webapp_response_dark.png')
else:
    print('Status:', resp.status_code, 'Body:', resp.text)
