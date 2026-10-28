from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

def test_selenium():
    options = Options()
    # options.add_argument('--headless') # Run non-headless to see if it works
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=options)
    
    print("1. Loading Z10Web...")
    driver.get('https://easymap.moi.gov.tw/Z10Web/Normal')
    
    # Wait for map to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "map"))
        )
        print("Map loaded.")
    except Exception as e:
        print("Timeout waiting for map:", e)
        driver.quit()
        return

    time.sleep(3) # Wait for tiles to load
    
    print("2. Clicking on the map at the center...")
    # Find map element
    map_el = driver.find_element(By.ID, "map")
    
    # We can try to use ActionChains to click
    from selenium.webdriver.common.action_chains import ActionChains
    actions = ActionChains(driver)
    actions.move_to_element(map_el).click().perform()
    print("Clicked.")
    
    # Wait a bit for the popup to appear
    time.sleep(3)
    
    # Check if there is any text in the popup
    try:
        popup = driver.find_element(By.ID, "popup")
        print("Popup found:")
        print(popup.text)
    except:
        print("No popup with ID 'popup' found.")
        
    print("3. Executing global JS to see if we can trigger coordinate query...")
    try:
        # Check if we can access the Vue instance or openlayers map
        ol_center = driver.execute_script("if(typeof ol2d !== 'undefined' && ol2d.map) { return ol2d.map.getView().getCenter(); } return null;")
        print("OL Center:", ol_center)
    except Exception as e:
        print("Error getting OL Center:", e)
        
    driver.quit()

if __name__ == "__main__":
    test_selenium()
