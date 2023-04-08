# Importing libraries

from urllib.request import urlopen, urlretrieve, Request
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from math import ceil
from datetime import datetime
from pathlib import Path


def url_reader(url) -> object:

    """"
    This function reads the html code of the url and returns a BeautifulSoup object.

    Parameters:
    url (str): The url to be read.
    """

    # Need to set user agent to avoid 403 error
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
        

def list_of_ads(soup) -> list:
    
    """
    This function returns a list of all the ads in the page.

    Parameters:
    soup (object): The BeautifulSoup object of the page.

    Returns:
    ad_links (list): A list of all the ads in the page.
    """

    ad_list = soup.findAll('a', class_='sc-cqpYsc kveahL')

    ad_links = []
    for ad in ad_list:
        ad_links.append((ad.get('href')))
        
    return ad_links
    

def text_from_tag(tag):

    """
    This function returns the text from a tag.

    Parameters:
    tag (object): The BeautifulSoup object of the page.

    Returns:
    text (str): The text from the tag.
    """

    if tag is not None:
        return tag.get_text()
    else:
        return 'None'
    

def create_csv(data):

    """
    This function creates a csv file with all the ads properties.

    Parameters:
    data (list): A list with all the ads properties.

    Returns:
    None
    """

    dataset = pd.DataFrame(data)

    today = datetime.now().strftime('%Y-%m-%d')

    # Creates the path directory
    Path("./output/data").mkdir(parents=True, exist_ok=True)

    return dataset.to_csv('./output/data/' + today + '_dataset.csv', sep=';', index = False, encoding = 'utf-8-sig')
    

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
    aux = soup.find('span', class_='sc-1mi5vq6-0 dQbOE sc-ifAKCX lgjPoE').get_text().split()
    ad_per_page = int(aux[2])
    n_total_ads = int(aux[-2].replace('.', ''))


    # If number_of_pages is not specified, calculate the number of pages
    if number_of_pages is not None:
      n_pages = number_of_pages
    else:
      n_pages = ceil(n_total_ads/ad_per_page)

    # Initialize the dataframe
    all_ad_data = []

    # Loop over the pages
    for page_number in tqdm(range(n_pages), desc='Pages', colour='red'):
        soup = url_reader(main_page_url + '?o={}'.format(page_number+1))
        ad_links = list_of_ads(soup)
        
        # Loop through all the ads
        for ad in ad_links:
            soup = url_reader(ad)
            if soup is not None:
            
              # Title
              title_tag = soup.find('h1', class_='ad__sc-45jt43-0 fAoUhe sc-cooIXK kMRyJF')
              title = text_from_tag(title_tag)

              # ID
              id_tag = soup.find('span', class_='ad__sc-16iz3i7-0 bTSFxO sc-ifAKCX fizSrB')
              id_ad = text_from_tag(id_tag).split()[-1]

              # Date and hour
              datetime_tag = soup.find('span', class_='ad__sc-1oq8jzc-0 hSZkck sc-ifAKCX fizSrB')
              datetime = text_from_tag(datetime_tag).split()
              date_ad, hour_ad = datetime[2], datetime[-1]

              # Description
              description_tag = soup.find('span', class_='ad__sc-1sj3nln-1 fMgwdS sc-ifAKCX cmFKIN')
              description = text_from_tag(description_tag).replace('\n',' ')

              # Price
              price_tag = soup.find('h2', class_='ad__sc-1wimjbb-1 hoHpcC sc-cooIXK cXlgiS')
              price = text_from_tag(price_tag).replace('.','')

              # Ad class
              class_ad = 'amateur'
              if soup.find('span', class_='ad__sc-16bj9n5-0 jTxUyi sc-ifAKCX fizSrB') is not None: 
                  class_ad = 'professional'

              # Product data
              data_tags = soup.findAll('div', class_='sc-hmzhuo ad__sc-1f2ug0x-3 sSzeX sc-jTzLTM iwtnNi')
              data = []
              subdata = []

              for tag in data_tags:
                tag_soup = BeautifulSoup(str(tag), 'html.parser')
                data.append(tag_soup.find('dt', class_='ad__sc-1f2ug0x-0 dOlajQ sc-ifAKCX cmFKIN').get_text())

                subdata_tag = tag_soup.find('a', class_='sc-gPWkxV dsTsUE') # when its a clickable link
                if subdata_tag == None:
                  subdata_tag = tag_soup.find('dd', class_ = 'ad__sc-1f2ug0x-1 cpGpXB sc-ifAKCX kaNiaQ')

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
                          urlretrieve(img.get('src'), './output/img/' + id_ad + '_' + str(i) + '.jpg')

              # Create a dictionary with all the data
              ad_data = {}
              ad_data['Title'] = title
              ad_data['ID'] = id_ad
              ad_data['Description'] = description
              ad_data['Date'] = date_ad
              ad_data['Hour'] = hour_ad
              ad_data['Class'] = class_ad
              ad_data['Price'] = price

              for i, _ in enumerate(range(len(data))):
                  ad_data[data[i]] = subdata[i]

              ad_data['Link'] = ad

              # Append the dictionary to the list
              all_ad_data.append(ad_data)

            else:
              continue

    return all_ad_data

# if number_of_pages is not specified, scrape all the ads from all the pages
main_page_url = "https://www.olx.com.br/imoveis/venda/estado-al/alagoas/maceio"
alldata = main(get_images = False, number_of_pages = 1, main_page_url = main_page_url)
create_csv(alldata)