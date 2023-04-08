# Importing libraries

from urllib.request import urlopen, urlretrieve, Request
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import pandas as pd
from tqdm.notebook import tqdm_notebook
from tqdm import tqdm
from math import ceil
from datetime import datetime
from pathlib import Path
from utils import url_reader, text_from_tag, create_csv, get_ads_list, get_ad_data


def main(get_images=False, number_of_pages=None, main_page_url=None):
    """
    This function scrapes the olx website and returns a dataframe with all the ads properties.

    Parameters:
    get_images (bool): If True, the images of the ads will be downloaded.
    number_of_pages (int): The number of pages to be scraped.

    Returns:
    df (pandas.DataFrame): A dataframe with all the ads properties.
    """

    # Reads the main page
    soup = url_reader(main_page_url)

    # Gets the number of pages and ads
    aux = soup.find(
        'span', class_="sc-1mi5vq6-0 eDXljX sc-bdVaJa juraBY").get_text().split()
    ad_per_page = int(aux[2])
    n_total_ads = int(aux[-2].replace('.', ''))

    # If number_of_pages is not specified, calculate the number of pages
    if number_of_pages is not None:
        n_pages = number_of_pages
    else:
        n_pages = ceil(n_total_ads/ad_per_page)

    # Initialize the dataframe
    all_data = []

    # Loop over the pages
    for page_number in tqdm(range(n_pages), desc='Ad pages', colour='red'):
        url = f'{main_page_url}?o={page_number+1}'
        ad_links = get_ads_list(url_reader(url), main_page_url)

        # Loop through all the ads
        for ad in tqdm(ad_links, desc='Ad links', colour='blue'):
            all_data.append(get_ad_data(ad))

    return all_data


url = "https://al.olx.com.br/alagoas/imoveis"
data = main(get_images=False, number_of_pages=2, main_page_url=url)
create_csv(data)