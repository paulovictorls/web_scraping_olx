#!/usr/bin/env python
# coding: utf-8

# In[1]:


from urllib.request import urlopen, urlretrieve, Request
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from math import ceil, modf
from time import perf_counter


# In[2]:


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
        return soup

    except HTTPError as e:
        print(e.status, e.reason)
        return None

    except URLError as e:
        print(e.reason)
        return None


# In[3]:


df = pd.read_csv('./output/data/dataset_cars_olx.csv', sep=';', encoding='utf-8-sig')
links_ad = df.Link
ids_ad = df.ID

for i in tqdm(range(len(links_ad))):
    soup_ad = url_reader(links_ad[i])
    if soup_ad is not None:
        id_ad = ids_ad[i]
        
        img_list_tag = soup_ad.find('div', class_='h3us20-6 fAprjt')
        if img_list_tag is not None:
            img_list = img_list_tag.findAll('img', class_='image')
            count=1
            for img in img_list:
                urlretrieve(img.get('src'), './output/img/' + str(id_ad) + '_' + str(count) + '.jpg')
                count+=1

