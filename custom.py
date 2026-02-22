from curl_cffi import requests
import json

url="https://hentai-manga.onrender.com/api"

parameters={
    "manga_id":10
}

response=requests.get(url=url,params=parameters,impersonate="chrome")
response.raise_for_status()

with open(f"{parameters['manga_id']}.json","w",encoding="utf-8") as filp:
    json.dump(response.json(),filp,indent=4,ensure_ascii=False)