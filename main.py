import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

docs_form_url = os.environ.get("SF_RENTING_RESEARCH_DOCS_FORM")
headers = {
    "Accept-Language": os.environ.get("ACCEPT_LANGUAGE"),
    "User-Agent": os.environ.get("USER_AGENT"),
}
all_links = []
all_prices = []
all_addresses = []

for page_number in range(1, 20):
    try:
        print(f"Processing page: {page_number}")
        zillow_url = (
            f"https://www.zillow.com/homes/for_rent/{page_number}-_beds/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22"
            "%3Anull%2C%22mapBounds%22%3A%7B%22west%22%3A-122.69219435644531%2C%22east%22%3A-122.17446364355469%2C%22south%22%3A37."
            "703343724016136%2C%22north%22%3A37.847169233586946%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22fr%22%3A%7"
            "B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%2"
            "2value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B"
            "%22value%22%3Afalse%7D%2C%22pmf%22%3A%7B%22value%22%3Afalse%7D%2C%22pf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%2"
            "2max%22%3A3000%7D%2C%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A11%7D"
        )

        response = requests.get(url=zillow_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find(class_="photo-cards photo-cards_wow photo-cards_short")

        links = [link["href"] for link in table.find_all("a")]
        links = list(dict.fromkeys(links))
        links = [f"https://www.zillow.com{link}" if not link.startswith("https:") else link for link in links]
        all_links += links

        prices = [price.text.split("+")[0].split("/")[0] for price in table.find_all(class_="list-card-price")]
        all_prices += prices

        addresses = [address.text for address in table.find_all("address")]
        all_addresses += addresses
    except IndexError as error:
        print(f"Page: {page_number}")
        print(error)


driver = webdriver.Chrome(executable_path=os.environ.get("CHROME_DRIVER_PATH"))
driver.get(url=docs_form_url)


def send_info(all_addresses, all_prices, all_links, index):
    time.sleep(1)
    driver.find_element_by_xpath(
        xpath='//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input'
    ).send_keys(all_addresses[index])
    driver.find_element_by_xpath(
        xpath='//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input'
    ).send_keys(all_prices[index])
    driver.find_element_by_xpath(
        xpath='//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input'
    ).send_keys(all_links[index])
    driver.find_element_by_xpath(xpath='//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div/div').click()
    time.sleep(1)
    driver.find_element_by_xpath(xpath="/html/body/div[1]/div[2]/div[1]/div/div[4]/a").click()


for index in range(len(all_links)):
    try:
        send_info(all_addresses, all_prices, all_links, index)
    except NoSuchElementException:
        time.sleep(3)
        send_info(all_addresses, all_prices, all_links, index)
