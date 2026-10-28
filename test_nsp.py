import requests
import urllib3

urllib3.disable_warnings()

def check():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
    }
    res = requests.get('https://nsp.nlma.gov.tw/ngis/', headers=headers, verify=False)
    # the site is likely big5 or cp950
    res.encoding = res.apparent_encoding
    print('Status:', res.status_code)
    print(res.text[:500])

if __name__ == "__main__":
    check()
