import requests
import urllib3
import re

urllib3.disable_warnings()

def test_api():
    session = requests.Session()
    session.verify = False
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    }
    
    print("1. Getting main page to establish session...")
    res1 = session.get('https://easymap.moi.gov.tw/Z10Web/Normal', headers=headers)
    print("Cookies:", session.cookies.get_dict())
    
    # Try to find CSRF token if any
    token = ""
    match = re.search(r'setToken\.jsp\?token=([a-zA-Z0-9]+)', res1.text)
    if match:
        token = match.group(1)
        print("Found Token:", token)
        # Call setToken
        session.get(f'https://easymap.moi.gov.tw/Z10Web/layout/setToken.jsp?token={token}', headers=headers)
        
    print("2. Calling Land_json_getMapImageLayersByCoord...")
    # I don't know the exact parameters. Let's guess: x, y or px, py or lon, lat
    data = {
        'x': '121.214',
        'y': '24.939',
        'lon': '121.214',
        'lat': '24.939',
        'px': '121.214',
        'py': '24.939',
        'type': 'land'
    }
    headers['X-Requested-With'] = 'XMLHttpRequest'
    res2 = session.post('https://easymap.moi.gov.tw/Z10Web/Land_json_getMapImageLayersByCoord', data=data, headers=headers)
    print("Status:", res2.status_code)
    print("Response:", res2.text[:500])

if __name__ == "__main__":
    test_api()
