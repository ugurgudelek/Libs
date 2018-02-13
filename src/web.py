import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

WINDOW_SIZE = "1920,1080"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)

driver = webdriver.Chrome(chrome_options=chrome_options)  # Optional argument, if not specified will search path.

driver.get('https://tbs.tarbil.gov.tr/(X(1)S(aj5etvomsof11z3ijw1is22v))/Authentication.aspx')
time.sleep(2) # Let the user actually see something!
username_box = driver.find_element_by_name('username')
password_box = driver.find_element_by_name('password')
username_box.send_keys('12345678910')
password_box.send_keys('12345678910')

submit_btn = driver.find_element_by_name('btnSubmit')
submit_btn.click()

username_box.submit()
password_box.submit()
submit_btn.submit()

time.sleep(5) # Let the user actually see something!
# driver.quit()