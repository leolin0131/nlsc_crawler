from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def test_selenium():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get('https://easymap.moi.gov.tw/Z10Web/Normal')
    time.sleep(5)
    
    has_ol = driver.execute_script('return typeof ol !== "undefined"')
    print('Has OL:', has_ol)
    
    has_l = driver.execute_script('return typeof L !== "undefined"')
    print('Has L:', has_l)
    
    globals_str = driver.execute_script('return Object.keys(window).filter(k => k.startsWith("map") || k.startsWith("qt")).join(", ")')
    print('Globals:', globals_str)
    
    driver.quit()

if __name__ == "__main__":
    test_selenium()
