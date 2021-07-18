import requests
from requests.structures import CaseInsensitiveDict
from bs4 import BeautifulSoup
import pandas as pd
import json

url = 'https://www.auchan.ru'
headers = CaseInsensitiveDict()
headers[
    "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
headers[
    "Cookie"] = "_gid=GA1.2.1328720489.1626382960; isAddressPopupShown_=true; region_id=1; merchant_ID_=1; methodDelivery_=1; _GASHOP=001_Mitishchi; rrpvid=45559367280892; _gcl_au=1.1.281931752.1626382966; rcuid=60f0a27525de560001d50b99; _ym_uid=1626380786127970853; _ym_d=1626382968; mindboxDeviceUUID=daa8f9a0-bee5-4f05-b235-bf03c206b67b; directCrm-session=%7B%22deviceGuid%22%3A%22daa8f9a0-bee5-4f05-b235-bf03c206b67b%22%7D; tmr_lvid=aa80088ccabb6676bb9ce35d8ad40642; tmr_lvidTS=1626380785695; _clck=1yf967k; _fbp=fb.1.1626382969263.577588319; rrlevt=1626533366500; _ym_isad=2; _ga=GA1.2.1133299417.1626380786; tmr_detect=0%7C1626634090925; _ga_6KC2J1XGF1=GS1.1.1626638919.18.0.1626638919.60; _clsk=3cv9og|1626638919548|2|1|eus2/collect; tmr_reqNum=239; qrator_jsr=1626639043.582.B3QmoloY35jsIs2C-4t5k43aetnpm56trcf72o9dsna5qgj02-00; qrator_jsid=1626639043.582.B3QmoloY35jsIs2C-8p0qpja9p7klt2ds0rd0most5j73ial3; qrator_ssid=1626639046.045.OXaJk41VQ4YTRGcZ-57r347n2jc2fqniifuucha5o7p80i508"
# Для работы с этим функциями нужно вставить куки из своего браузера(обход защиты сайта)

def parser_category(category_link):
    """
    Фуннкция для парсинга товаров одной категории
    :parameter category_link: ссылка на категорию
    """
    i = 0
    product_names = []
    product_brands = []
    product_prices = []
    for num in range(1, 60):
        # Перебор каждой из страниц
        response = requests.get(url + category_link + '?page=' + str(num), headers=headers, timeout=5)
        if response.status_code != 200:
            return product_names, product_brands, product_prices
        soup = BeautifulSoup(response.content, 'html.parser')
        list_html = soup.find_all(class_="linkToPDP active css-1kl2eos")
        if list_html is None:
            return product_names, product_brands, product_prices
        product_links = [product["href"] for product in list_html]
        for link in product_links:
            product = parser_product(link)
            i += 1
            if product is not None:
                product_names.append(product[0])
                product_brands.append(product[1])
                product_prices.append(product[2])
#             print(i, parser_product(link))

def parser_product(product_link):
    """
    Фуннкция для извлечения информации из товара
    :parameter product_link: ссылка на товар
    """
    response = requests.get(url + product_link, headers=headers, timeout=5)
    assert response.status_code == 200, "Connection failed"
    soup = BeautifulSoup(response.content, 'html.parser')
    if soup.find(type="application/ld+json"):
        product_json = json.loads(soup.find(type="application/ld+json").string)
        product_name = product_json['name']
        product_brand = product_json['brand']
        price = product_json['offers']['price']
        return product_name, product_brand, price


def parser_achan():
    """"Фуннкция для извлечения списка товаров с сайта auchan.ru """
    all_names = []
    all_brands = []
    all_prices = []
    response = requests.get(url, headers=headers, timeout=5)
    assert response.status_code == 200, "Connection failed"
    soup = BeautifulSoup(response.content, 'html.parser')
    html_product = soup.find(class_="css-1hyfx7x")
    categories_html = html_product.find_all('a')[3:527]
    categories_names = [category.text.strip() for category in categories_html]
    categories_link = [category["href"] for category in categories_html]
    categories_name_to_link = dict(zip(categories_names, categories_link))
    categories_name_to_link
    i = 0
    for category in categories_link:
        if category.count('/') != 5:
            # исключение подкатегорий
            continue
        i += 1
        print(i)
        category_names, category_brands, category_prices = parser_category(category)
        all_names += category_names
        all_brands += category_brands
        all_prices += category_prices
    # Создание датафрема с собранными данными
    df = pd.DataFrame(
        {
            'name': all_names,
            'brand': all_brands,
            'price': all_prices
        })
    return df
