from os import X_OK
from urllib.request import urlopen, urlretrieve, Request
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from math import ceil, modf
from time import perf_counter

def url_reader(url) -> object:

    """[summary]

    Returns:
        [type]: [description]
    """

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}

    try:
        req = Request(url, headers = headers)
        response = urlopen(req)
        html = response.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        # print('succesful read')

    except HTTPError as e:
        print(e.status, e.reason)

    except URLError as e:
        print(e.reason)
        
    return soup

def list_of_ads(soup) -> list:
    """[summary]

    Args:
        soup ([type]): [description]

    Returns:
        list: [description]
    """

    ad_list = soup.findAll('a', class_='fnmrjs-0 fyjObc')

    ad_links = []
    for ad in ad_list:
        ad_links.append((ad.get('href')))
        
    return ad_links

def time_remaining(t0, t1, n_total_ads, page_number, count_ad) -> float:
    """
    Function that returns an estimation on the time remaining to complete the script

    Args:
        t0 (float): Time when the main function was started
        t1 (float): Time when retrieve the new ad html code
        n_total_ads (int): total number of ads to be scrapped
        page_number (int): ads page number
        count_ad (int): ad number on the current page

    Returns:
        float: hours, minutes, seconds, ad number
    """

    # Calculating the time remaining
    dt = t1-t0
    ad_number = page_number*50+count_ad
    ads_remaining = n_total_ads - ad_number
    time_left = (dt*ads_remaining)/ad_number # seconds

    # Converting time to from seconds to hours
    time_left /= 3600

    # Acquire the integer part of a float
    aux = modf(time_left)
    hours = aux[1]

    # Convert the float part to minutes and split into minutes and seconds
    aux_2 = modf(aux[0]*60)
    minutes, seconds = aux_2[1], ceil(aux[0]*60)

    return hours, minutes, seconds, ad_number

def text_from_tag(tag):
    if tag is not None:
        return tag.get_text()
    else:
        return 'None'

def main(get_images=False):

    """[summary]

    Returns:
        [type]: [description]
    """

    # Start timer
    t0 = perf_counter()

    # Acquire the number of pages
    main_page = 'https://al.olx.com.br/alagoas/maceio/autos-e-pecas/carros-vans-e-utilitarios'
    main_page = 'https://al.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios'
    soup = url_reader(main_page)

    aux = soup.find('span', class_='sc-1mi5vq6-0 eDXljX sc-ifAKCX fhJlIo').get_text().split()

    ad_per_page = int(aux[2])
    n_total_ads = int(aux[-2].replace('.', ''))

    n_pages = ceil(n_total_ads/ad_per_page)
    n_pages, n_total_ads = 3, 10*50

    all_ad_data = []

    for page_number in tqdm(range(n_pages), desc='Pages', colour='red'):

        soup = url_reader('https://al.olx.com.br/alagoas/maceio/autos-e-pecas/carros-vans-e-utilitarios?o={}'.format(page_number+1))
        ad_links = list_of_ads(soup)
        
        count_ad = 1
        for ad in tqdm(ad_links, desc='Ads on page', colour='green'):
            
            # t1 = perf_counter()
            # hours, minutes, seconds, ad_number = time_remaining(t0, t1, n_total_ads, page_number, count_ad)
            # print('Page {} of {} - Ad {} of {} - exp time: {}h - {}min - {}sec  -  {:.2f}%'.format(page_number+1, n_pages, ad_number, n_total_ads, int(hours), int(minutes), int(seconds), 100*ad_number/n_total_ads))
            # count_ad += 1
        
            soup = url_reader(ad)
            
            # Title
            title_tag = soup.find('h1', class_='sc-1q2spfr-0 lcTcEs sc-ifAKCX cmFKIN')
            title = text_from_tag(title_tag)

            # ID
            id_tag = soup.find('span', class_='sc-16iz3i7-0 qJvUT sc-ifAKCX fizSrB')
            id_ad = text_from_tag(id_tag).split()[-1]

            # Date and hour
            datetime_tag = soup.find('span', class_='sc-1oq8jzc-0 jvuXUB sc-ifAKCX fizSrB')
            datetime = text_from_tag(datetime_tag).split()
            date_ad, hour_ad = datetime[2], datetime[-1]

            # Description
            description_tag = soup.find('span', class_='sc-1sj3nln-1 eOSweo sc-ifAKCX cmFKIN')
            description = text_from_tag(description_tag).replace('\n',' ')

            # Price
            price_tag = soup.find('h2', class_='sc-ifAKCX eQLrcK')
            price = text_from_tag(price_tag).replace('.','')

            # Ad class
            calss_ad = 'amateur'
            if soup.find('span', class_='sc-16bj9n5-0 IIBHN sc-ifAKCX fizSrB') is not None: 
                calss_ad = 'professional'

            # Vehicle data
            items_tags = soup.findAll('span', class_='sc-ifAKCX dCObfG')
            data = []
            if items_tags is not None:
                items_tags.pop()
                for tag in items_tags:
                    data.append(tag.get_text())

            # Vehicle subdata
            subitems_tags = soup.findAll('div', class_='duvuxf-0 h3us20-0 hCwZcX') + soup.findAll('div', class_='duvuxf-0 h3us20-0 kjKryV')
            subdata = []
            if subitems_tags is not None:
                for tag in subitems_tags:
                    a = tag.find('span', class_='sc-ifAKCX cmFKIN')
                    b = tag.find('a')

                    if a is None:
                        subdata.append(b.get_text())
                    else:
                        subdata.append(a.get_text())

            # Optionals
            optionals_tags_parent = soup.find('div', class_='sc-bwzfXH h3us20-0 cNYGOs')
            optionals = []
            if optionals_tags_parent is not None:
                optionals_tags = optionals_tags_parent.findAll('div', class_="duvuxf-0 h3us20-0 jyICCp")
                for tag in optionals_tags:
                    optionals.append(tag.get_text())

            # Location
            location_tags = soup.find('div', class_='h3us20-6 govcZZ').findAll('dd', class_='sc-1f2ug0x-1 ljYeKO sc-ifAKCX kaNiaQ')
            location_titles = ['CEP', 'City', 'Neighborhood']
            location = []
            if location_tags is not None:
                for tag in location_tags:
                    location.append(tag.get_text())

            # Get images
            if get_images:
                img_list = soup.find('div', class_='h3us20-6 fAprjt').findAll('img', class_='image')
                count=1
                for i in img_list:
                    urlretrieve(i.get('src'), './output/img/' + id_ad + '_' + str(count) + '.jpg')
                    count+=1

            # Creating the card

            ad_data = {}
            ad_data['Title'] = title
            ad_data['ID'] = id_ad
            ad_data['Description'] = description
            ad_data['Date'] = date_ad
            ad_data['Hour'] = hour_ad
            ad_data['Class'] = calss_ad
            ad_data['Price'] = price

            count = 0
            for i in range(len(data)):
                ad_data[data[count]] = subdata[count]
                count+=1

            if soup.find('div', class_='sc-bwzfXH h3us20-0 cNYGOs') is not None:
                for o in optionals:
                    ad_data[o] = 'yes'

            count = 0
            for i in range(len(location)):
                ad_data[location_titles[count]] = location[count]
                count+=1
                

            ad_data['Link'] = ad

            all_ad_data.append(ad_data)

    return all_ad_data

def create_csv(data):

    """[summary]
    """

    dataset = pd.DataFrame(data)
    dataset.to_csv('./output/data/dataset.csv', sep=';', index = False, encoding = 'utf-8-sig')


alldata = main(get_images = True)
create_csv(alldata)