from urllib.request import urlopen, urlretrieve, Request
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import pandas as pd
from tqdm.notebook import tqdm_notebook
from math import ceil
from datetime import datetime
from pathlib import Path
import re


def url_reader(url) -> object:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}

    try:
        req = Request(url, headers = headers)
        response = urlopen(req)
        html = response.read().decode('utf-8')
        soup_obj = BeautifulSoup(html, 'html.parser')
        return soup_obj

    except HTTPError as e:
        print(e.status, e.reason)

    except URLError as e:
        print(e.reason)
        

def text_from_tag(tag):
    if tag is not None:
        return tag.get_text()
    else:
        return 'None'

def create_csv(data):
    dataset = pd.DataFrame(data)

    today = datetime.now().strftime('%Y-%m-%d')

    # Creates the path directory
    Path("./output/data").mkdir(parents=True, exist_ok=True)

    return dataset.to_csv('./output/data/' + today + '_dataset.csv', sep=';', index = False, encoding = 'utf-8-sig')


def is_valid(link, base_link):
    return link[-1].isdigit() and link.startswith(f'{base_link}/')

def get_ads_list(soup, base_link):
    regex = fr'href="({base_link}.*?)"'
    link_list = re.findall(regex, str(soup))
    return [link for link in link_list if is_valid(link, base_link)]

def get_ad_data(ad_link, get_images=False):
    soup = url_reader(ad_link)

    if soup is not None:

        # Title
        title_tag = soup.find(
            'h1', class_='sc-45jt43-0 eCghYu sc-ifAKCX cmFKIN')
        title = text_from_tag(title_tag)

        # ID
        id_tag = soup.find(
            'span', class_='sc-16iz3i7-0 qJvUT sc-ifAKCX fizSrB')
        id_ad = text_from_tag(id_tag).split()[-1]

        # Date and hour
        datetime_tag = soup.find(
            'span', class_='sc-1oq8jzc-0 jvuXUB sc-ifAKCX fizSrB')
        datetime = text_from_tag(datetime_tag).split()
        date_ad, hour_ad = datetime[2], datetime[-1]

        # Description
        description_tag = soup.find(
            'span', class_='sc-1sj3nln-1 eOSweo sc-ifAKCX cmFKIN')
        description = text_from_tag(description_tag).replace('\n', ' ')

        # Price
        price_tag = soup.find('h2', class_='sc-ifAKCX eQLrcK')
        price = text_from_tag(price_tag).replace('.', '')

        # Ad class
        calss_ad = 'amateur'
        if soup.find('span', class_='sc-16bj9n5-0 IIBHN sc-ifAKCX fizSrB') is not None:
            calss_ad = 'professional'

        # Product data
        data_tags = soup.findAll(
            'div', class_='sc-hmzhuo sc-1f2ug0x-3 ONRJp sc-jTzLTM iwtnNi')

        data = []
        subdata = []

        for tag in data_tags:
            tag_soup = BeautifulSoup(str(tag), 'html.parser')
            data.append(tag_soup.find(
                'dt', class_='sc-1f2ug0x-0 cLGFbW sc-ifAKCX cmFKIN').get_text())

            subdata_tag = tag_soup.find(
                'a', class_='sc-57pm5w-0 sc-1f2ug0x-2 dBeEuJ')
            if subdata_tag == None:
                subdata_tag = tag_soup.find(
                    'dd', class_='sc-1f2ug0x-1 ljYeKO sc-ifAKCX kaNiaQ')

            subdata.append(subdata_tag.get_text())

        # Get images
        if get_images:
            img_tags = soup.find('div', class_='h3us20-6 fAprjt')

            # Checks if exists images
            if img_tags is not None:
                # Creates the path directory
                Path("./output/img").mkdir(parents=True, exist_ok=True)

                img_list = img_tags.findAll('img', class_='image')
                if img_list is not None:
                    for i, img in enumerate(img_list):
                        urlretrieve(
                            img.get('src'), './output/img/' + id_ad + '_' + str(i) + '.jpg')

        # Create a dictionary with all the data
        ad_data = {}
        ad_data['Title'] = title
        ad_data['ID'] = id_ad
        ad_data['Description'] = description
        ad_data['Date'] = date_ad
        ad_data['Hour'] = hour_ad
        ad_data['Class'] = calss_ad
        ad_data['Price'] = price

        for i, _ in enumerate(range(len(data))):
            ad_data[data[i]] = subdata[i]

        ad_data['Link'] = ad_link

        return ad_data