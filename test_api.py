import requests
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_js_content():
    session = requests.Session()
    session.verify = False
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    url = "https://maps.nlsc.gov.tw/T09/mobile/js/qt_ajax.js"
    res = session.get(url, headers=headers)
    if res.status_code == 200:
        lines = res.text.split('\n')
        # Find getLcdetypeFlag
        in_func = False
        brace_count = 0
        for i, line in enumerate(lines):
            if 'function getLcdetypeFlag' in line:
                in_func = True
            if in_func:
                print(f"L{i}: {line.rstrip()}")
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0 and '}' in line:
                    break

if __name__ == "__main__":
    get_js_content()
