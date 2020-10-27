#Add multiple searches in one input 
#Scale up 
#Transform data to telegram bot, email 
#Continuous deployment 

#Depop restricts user login after certain amount of tries.
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
import time
from datetime import datetime 

opt = Options()
opt.add_argument("--incognito")
#opt.add_argument("--headless")
opt.add_argument("--ignore-certificate-errors")

site = input("Please choose the platform to search: eBay or Grailed. ")
search_term = input("Please enter what would you like to search today: ")

todays_date = datetime.today().strftime('%m_%d')

filename= todays_date + "_" + site + "_" + search_term.replace(" ", "_") + ".csv"
f= open(filename, "w")  # "w" for writing permission
headers= "Name, Price, URL\n"
f.write(headers)

driver = WebDriver('/Users/seanlow/Desktop/2020/Vintage Scraper/chromedriver',options=opt)

def init_browser(site):
    url = "https://www."+ site.lower() + ".com"
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete')
    except TimeoutException:
        print("It took too much time")
        return False
    return True


def search(site,search_term):
    #Assume browser is already loaded. 
    if site =='ebay':
        searchbar = driver.find_element_by_name("_nkw")
        searchbar.send_keys(search_term)
        searchbar.send_keys(Keys.ENTER)
        try:
            check_search = EC.presence_of_element_located((By.CLASS_NAME,"s-item__title"))
            WebDriverWait(driver, 10).until(check_search)
        except NoSuchElementException:
            print("None found")
            return False 
        return True 

    # if site == 'depop':
    #     login = driver.find_element_by_xpath('//a[@href="/login/"]')
    #     login.send_keys(Keys.ENTER)
    #     try:
    #         check_login_page = EC.presence_of_element_located((By.ID, 'username'))
    #         WebDriverWait(driver, 10).until(check_login_page)
    #     except NoSuchElementException:
    #         print("None found")
    #     login_name = driver.find_element_by_id("username")
    #     login_name.send_keys(user)
    #     login_pw = driver.find_element_by_id("password")
    #     login_pw.send_keys(pw)

    #     #Buffer before submitting details
    #     time.sleep(5)
    #     login_pw.send_keys(Keys.ENTER)
    #     try:
    #         login_success = EC.presence_of_element_located((By.XPATH,'//a[@href="/search/"]')) 
    #         WebDriverWait(driver, 10).until(login_success)
    #     except NoSuchElementException:
    #         print("Login Failed")
        
    #     #Buffer before searching for search bar
    #     time.sleep(3)
    #     search_button= driver.find_element_by_xpath('//a[@href="/search/"]')
    #     search_button.click()

    #     time.sleep(3)
    #     #Unable to find searchbar
    #     searchbar = driver.find_element_by_xpath("//input[@placeholder='Search']")
    #     searchbar.click()
    #     searchbar.send_keys(search_term)

    #     #Buffer before submitting search input
    #     time.sleep(3)
    #     searchbar.send_keys(Keys.ENTER)

    if site == "grailed":
        try: 
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID,"globalheader_search")))
        except NoSuchElementException:
            print("Searchbar not found.")

        searchbar = driver.find_element_by_id("globalheader_search")
        searchbar.send_keys(search_term)
        searchbar.send_keys(Keys.ENTER)
        try:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "listing-cover-photo")))
        except NoSuchElementException:
            print("No listings found")
            return False

        #Remove login prompt window (might not be necessary if I scrape fast enough)
        try:
            login_prompt = EC.presence_of_element_located((By.CLASS_NAME, "close"))
            WebDriverWait(driver, 20).until(login_prompt)
            exit_button = driver.find_element_by_xpath('//a[@class="close"]')
            exit_button.click()
            print("Done")
        except NoSuchElementException:
            print("No login prompt detected")
    # # WIP
    # if site == "yahoo":
    #     st = search_term.split()
    #     for i in range(len(st)):
    #         url="https://auctions.yahoo.co.jp/search/search?auccat=&tab_ex=commerce&ei=utf-8&aq=-1&oq=&sc_i=&exflg=1&p="+ st[i]+"+"
    #     end = "&x=0&y=0" 
    #     url = url + end 

    #     return True 

def collate(site):
    if site =="ebay":
        listings = driver.find_elements_by_xpath('//li[@class="s-item    s-item--watch-at-corner"]')
        for listing in listings:
            name = listing.find_element_by_xpath('.//h3[contains(@class,"s-item__title")]').text.strip()
            price = listing.find_element_by_xpath('.//span[contains(@class, "s-item__price")]').text.strip()
            url_html = listing.find_element_by_tag_name('a')
            url = url_html.get_attribute('href')
            f.write(name + ',' + price + ',' + url + "\n")
        return True 

    if site == "grailed":
        listings = driver.find_elements_by_class_name("feed-item")
        for listing in listings:
            name = listing.find_element_by_class_name("listing-title").text.strip()
            price = listing.find_element_by_class_name("listing-price").text.strip()
            url_html = listing.find_element_by_tag_name("a")
            url = url_html.get_attribute('href')
            f.write(name + ',' + price + ',' + url + "\n")
            if NoSuchElementException:
                break
        return True

def vintage_search(site, search_term):
    print("Loading browswer...")
    browser_loaded = init_browser(site)
    if not browser_loaded:
        print("Browser failed to load.")
        driver.close()
    print("Searching for "+ search_term)
    search_loaded = search(site,search_term)
    if not search_loaded:
        print("Search failed")
        driver.close()
    print("Collecting data...")
    search_done = collate(site)
    if not search_done:
        print("Scrape failed")
        driver.close()
    driver.quit()

vintage_search(site,search_term)