import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

# Define the URL to scrape
url = 'https://www.olx.com.br/imoveis/estado-al'

# Define the user-agent header to send with the request
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}

# Send a request to the website and get the HTML response
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')

# Find all the listings on the page
listings = soup.find_all('li', {'class': 'sc-1fcmfeb-2'})

# Create a CSV file with headers for the data we want to scrape
filename = datetime.now().strftime("%Y-%m-%d") + '_olx.csv'
with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['title', 'price', 'location', 'bedrooms', 'bathrooms', 'size', 'cep', 'link']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # Loop through each listing and extract the data we want
    for listing in listings:
        title = listing.find('h2').text.strip()
        price = listing.find('p', {'class': 'sc-ifAKCX'}).text.strip()
        location = listing.find('p', {'class': 'sc-1jw5wvd-0'}).text.strip()
        link = listing.find('a')['href']

        # Follow the link to the listing page to extract more details
        listing_response = requests.get(link, headers=headers)
        listing_soup = BeautifulSoup(listing_response.content, 'html.parser', from_encoding='utf-8')
        details_section = listing_soup.find('section', {'class': 'sc-1bker4h-1'})

        # Extract the number of bedrooms, bathrooms, and size from the details section
        details_list = details_section.find_all('li', {'class': 'sc-1o5u5en-0'})
        bedrooms = None
        bathrooms = None
        size = None
        cep = None
        for detail in details_list:
            label = detail.find('span', {'class': 'sc-1o5u5en-3'}).text.strip()
            value = detail.find('span', {'class': 'sc-1o5u5en-4'}).text.strip()
            if 'Quartos' in label:
                bedrooms = value
            elif 'Banheiros' in label:
                bathrooms = value
            elif 'm²' in label:
                size = value
            elif 'CEP' in label:
                cep = value

        # Write the data to the CSV file
        writer.writerow({'title': title, 'price': price, 'location': location, 'bedrooms': bedrooms, 'bathrooms': bathrooms, 'size': size, 'cep': cep, 'link': link})
