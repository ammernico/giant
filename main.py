import logging
import requests
import json
from pprint import pprint
from bs4 import BeautifulSoup

header = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(filename="./giant.log", level=logging.DEBUG, format=LOG_FORMAT, filemode='w')
logger = logging.getLogger()


class Bike:
    def __init__(self, name, price, price_str, specs):
        self.name = name
        self.price = price
        self.price_str = price_str
        self.specs = specs

    def __repr__(self):
        from pprint import pformat
        return pformat(vars(self))


def get_bike_stats_for_bike_site(rel_link: str):
    base_link = "https://www.giant-bicycles.com"
    link = base_link + rel_link

    soup = BeautifulSoup(requests.get(link).text, features="html.parser")
    logging.debug(soup)

    price_str = soup.find("div", {"class": "price"}).text
    price = price_str
    price = price.replace("€", "")
    price = price.replace(".", "")
    price = price.replace(" ", "")
    price = int(price)

    spec_table = soup.find("ul", {"class": "specifications"})
    spec_table = spec_table.find_all("li", {"class", "datarow"})
    specs = []
    for i in spec_table:
        label = i.find("div", {"class", "label"}).text
        value = i.find("div", {"class", "value"}).text
        specs.append({label: value})
    return Bike(rel_link, price, price_str, specs)


def check_multiple(link: str):
    """ gets something like https://www.giant-bicycles.com/de/trance-x-1-2023 """
    soup = BeautifulSoup(requests.get(link).text, features="html.parser")
    logging.debug(soup)

    just_one = soup.find("div", {"class": "breadcrumbs"})
    if just_one is None:
        # if there is more than one bike on the site return the bike sites
        logging.debug("more than one")
        bikes = soup.find_all("a", {"class": "textlink track-GA4-event"})
        return bikes
    logging.debug("just one")
    return 0


def parse_site(link: str):
    logging.debug(link)
    soup = BeautifulSoup(requests.get(link).text, features="html.parser")
    logging.debug(soup)

    table_of_bikes = soup.find("div", {"id": "productsContainer"})
    bikes_on_table = table_of_bikes.find_all("a", {"class": "textlink track-GA4-event"})
    rel_bike_sites = get_rel_bike_sites(bikes_on_table)

    all_bikes = []

    for i in rel_bike_sites:
        all_bikes.append(get_bike_stats_for_bike_site(i))
    all_bikes.sort(key=lambda x: x.price)
    for i in all_bikes:
        pprint(i)
        print()


def get_rel_bike_sites(bike_table) -> []:
    names = []
    base_link = "https://www.giant-bicycles.com"
    for i in bike_table:
        full_bike_name = parse_bike_name(i)
        if full_bike_name == "":
            continue
        bike_link = base_link + full_bike_name  # check if multiple

        multiple = check_multiple(bike_link)
        if multiple == 0:  # just one
            names.append(full_bike_name)
        else:
            for j in multiple:
                full_bike_name = parse_bike_name(j)
                if full_bike_name == "":
                    continue
                names.append(full_bike_name)
    return names


def parse_bike_name(bike_html):
    bike = bike_html["data-ga4_items"]
    bike = bike.strip('[]')
    bike = json.loads(bike)
    # {'item_id': 'series-1175', 'item_name': 'reign advanced pro', 'index': 3, 'item_brand': 'giant', 'item_category': 'bikes', 'item_category2': 'mountain bikes', 'item_category3': 'full suspension', 'price': 5299.0, 'discount': 0.0, 'quantity': 1}
    bike_name = bike["item_name"]
    if bike_name == "":
        return bike_name
    full_bike_name = bike_html["href"]
    return full_bike_name


def main():
    links = [
            "https://www.giant-bicycles.com/de/bikes/mountain/full-suspension"
            ]
    for i in links:
        parse_site(i)


if __name__ == "__main__":
    main()