from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def test():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    print("Loading page...")
    driver.get('https://easymap.moi.gov.tw/Z10Web/Normal')
    
    time.sleep(5)
    print("Page title:", driver.title)
    
    print("Checking globals for map objects...")
    globals_str = driver.execute_script("return Object.keys(window).filter(k => k.toLowerCase().includes('map') || k.startsWith('ol')).join(', ')")
    print("Globals:", globals_str)
    
    # Try to execute Z10Web's specific query function if it exists
    # If it's Vue, we can't easily trigger the component method, but we can trigger a map click
    try:
        # OpenLayers is usually on window.map or window.olMap or something similar
        res = driver.execute_script("""
            if (typeof ol2d !== 'undefined' && ol2d.map) {
                // simulate map click? Or maybe we can just look for the query function
                return "ol2d found";
            }
            return "ol2d not found";
        """)
        print(res)
    except Exception as e:
        print("Error evaluating script:", e)
        
    driver.quit()

if __name__ == "__main__":
    test()
