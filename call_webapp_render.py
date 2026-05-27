import requests

url = 'http://127.0.0.1:5000/api/render'
files = {'file': open('he test.xlsx','rb')}
# send minimal form data, leave dark_mode unchecked to match a typical user
data = {'sheet': '', 'title': 'debug-webapp-test', 'scale_mode':'auto'}
resp = requests.post(url, files=files, data=data)
if resp.status_code == 200 and resp.headers.get('Content-Type','').startswith('image'):
    open('outputs/webapp_response.png','wb').write(resp.content)
    print('Wrote outputs/webapp_response.png')
else:
    print('Status:', resp.status_code, 'Body:', resp.text)
