import requests
import pandas as pd

url = "http://172.30.1.129:8011/fetch/CEN_db_mysql/cenCiscoXE_Interface"



response = requests.request("GET", url)

df = pd.read_json(response.json(), orient='split')
print(df)