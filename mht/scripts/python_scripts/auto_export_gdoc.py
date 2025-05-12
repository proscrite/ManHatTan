from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
opts = Options()
opts.add_argument('user-data-dir=/Users/pabloherrero/Library/Application Support/Google/Chrome')
opts.add_argument('--allow-running-insecure-content')
opts.add_argument('--ignore-certificate-errors')

driver = webdriver.Chrome(executable_path='../chromedriver', options=opts)
mail_address = 'pablogfr94@gmail.com'
password = 'Eez/eh4813'

driver.get("https://docs.google.com/document/d/1q5LpTfMBZF7LBsGaMyiKoMezIwrOR1s9szLBZ3rsbb8/edit")
driver.find_element_by_id("identifierId").send_keys(mail_address)
driver.find_element_by_id("identifierNext").click()
time.sleep(1)
driver.find_element_by_name("password").send_keys(password)
driver.find_element_by_id("passwordNext").click()
time.sleep(20)
driver.quit()
