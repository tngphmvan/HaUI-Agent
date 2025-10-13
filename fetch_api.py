import requests

url = "http://172.16.21.110:5280/api/v1/for-a-luong/full-option"
params = {"maNganh": "1107"}
headers = {"accept": "text/plain"}

response = requests.get(url, headers=headers, params=params)
print(response.json()['data']['khung_chuong_trinh'])
