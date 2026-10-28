import requests
import urllib3
import xml.etree.ElementTree as ET

urllib3.disable_warnings()

def get_layers():
    res = requests.get('https://landmaps.nlsc.gov.tw/S_Maps/wms?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetCapabilities', verify=False)
    root = ET.fromstring(res.content)
    for layer in root.iter():
        if 'Layer' in layer.tag:
            name = layer.find('.//{*}Name')
            title = layer.find('.//{*}Title')
            if name is not None:
                print(f"Name: {name.text}, Title: {title.text if title is not None else ''}")

if __name__ == "__main__":
    get_layers()
