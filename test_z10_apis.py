import requests
import re
import urllib3

urllib3.disable_warnings()

def get_z10_apis():
    # Base URLs
    base = 'https://easymap.moi.gov.tw/Z10Web/'
    
    js_files = [
        'dist/qtAjax.js',
        'dist/qtCommon.js',
        'dist/chunk-vendors.js',
        'js/index.js'
    ]
    
    endpoints = set()
    for js in js_files:
        print(f"Fetching {js}...")
        try:
            res = requests.get(base + js, verify=False, timeout=10)
            text = res.text
            # Look for typical AJAX URLs in Z10Web
            # They usually don't have .do or .action, just endpoints like "Identify_json_getIdentifyXY"
            urls = re.findall(r'\"([a-zA-Z0-9_]+_json_[a-zA-Z0-9_]+)\"', text)
            endpoints.update(urls)
            
            # Also look for any string that looks like an endpoint path
            paths = re.findall(r'\"(/[a-zA-Z0-9_/-]+)\"', text)
            endpoints.update(paths)
        except Exception as e:
            print(f"Error fetching {js}: {e}")
            
    print("\n--- Found Endpoints ---")
    for ep in sorted(endpoints):
        if len(ep) > 3 and not ep.endswith('.js') and not ep.endswith('.css') and not ep.endswith('.png'):
            print(ep)

if __name__ == "__main__":
    get_z10_apis()
