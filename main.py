import logging
import requests
import json
from bs4 import BeautifulSoup

header = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(filename = "./giant.log",
                                level=logging.DEBUG,
                                format = LOG_FORMAT,
                                filemode = 'w')
logger = logging.getLogger()

class Bike:
    def __init__(self, name: str, price: float, stats: dir):
        self.name = name
        self.price = price
        self.stats = stats

def parse_bike_site(link: str):
    ''' gets something like https://www.giant-bicycles.com/de/trance-x-1-2023 '''
    # then the //*[@id="specifications"] contains a table with the information we are after
    soup = BeautifulSoup(requests.get(link).text)
    logging.debug(soup)
    table = soup.find("div", {"id": "specifications"})
    print(table)

def parse_site(link: str):
    logging.debug(link)
    soup = BeautifulSoup(requests.get(link).text, features="html.parser")
    logging.debug(soup)

    table_of_bikes = soup.find("div", {"id": "productsContainer"})
    bikes = table_of_bikes.find_all("a", {"class": "textlink track-GA4-event"})

    base_link = "https://www.giant-bicycles.com"

    for i in bikes:
        bike = i["data-ga4_items"]
        bike = bike.strip('[]')
        bike = json.loads(bike)
        # {'item_id': 'series-1175', 'item_name': 'reign advanced pro', 'index': 3, 'item_brand': 'giant', 'item_category': 'bikes', 'item_category2': 'mountain bikes', 'item_category3': 'full suspension', 'price': 5299.0, 'discount': 0.0, 'quantity': 1}
        bike_name = bike["item_name"]
        bike_price = bike["price"]
        if bike_name == "":
            continue

        bike_link = base_link + i["href"]  # link for retrieving the stats of the bike
        print(bike_link)
        print(bike_name, bike_price)
        print()


def main():
    links = [
            "https://www.giant-bicycles.com/de/bikes/mountain/full-suspension"
            ]
    for i in links:
        parse_site(i)

if __name__ == "__main__":
    main()