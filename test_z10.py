import requests
import re
import urllib3

urllib3.disable_warnings()

def get_apis():
    res = requests.get('https://easymap.moi.gov.tw/Z10Web/dist/chunk-vendors.js', verify=False)
    text = res.text
    
    # search for /Z10Web/ or .do or .action or json
    apis = re.findall(r'\"([/A-Za-z0-9_]+\.do)\"|\"([/A-Za-z0-9_]+\.action)\"|\"(/[A-Za-z0-9_]+/json[A-Za-z0-9_]*)\"', text)
    print("Found APIs in chunk-vendors:")
    for a in apis[:30]:
        print(a)
        
    res = requests.get('https://easymap.moi.gov.tw/Z10Web/js/index.js', verify=False)
    print("\nAPIs in index.js:")
    urls = re.findall(r'url\s*:\s*[\'\"]([^\'\"]+)[\'\"]', res.text)
    for u in urls:
        print(u)

if __name__ == "__main__":
    get_apis()
