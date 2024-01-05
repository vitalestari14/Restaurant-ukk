from selenium import webdriver
from bs4 import BeautifulSoup
import time 
from pymongo import MongoClient
import certifi
import requests

driver = webdriver.Chrome()
driver.get("https://www.yelp.com/search?cflt=restaurants&find_loc=San+Francisco%2C+CA")

password = 'janganmenyerah'
cxn_str = f'mongodb+srv://vitales1472:{password}@cluster0.l7n9fsb.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(cxn_str)
db = client.dbsparta_plus_week5

url = "https://www.yelp.com/search?cflt=restaurants&amp;find_loc=San+Francisco%2C+CA"

driver.get(url)

req = driver.page_source

soup = BeautifulSoup(req, 'html.parser')
access_token = 'pk.eyJ1IjoiZmFkaGlsbHgiLCJhIjoiY2w4eTloOGM1MDZ0MjN2bGcwY3k5Y3pjeSJ9.X-eiCzScHwEqjoXJUF6AXg'
long = -122.420679
lat = 37.772537

start = 0
seen = {}

restaurants = soup.select('div[class*="arrange-unit__"]')
for restaurant in restaurants:
    business_name = restaurant.select_one('div[class*="businessName__"]')
    if not business_name:
        continue
    name = business_name.text.split('.')[-1].strip()
    
    if name in seen:
        continue

    seen[name] = True
    
    link = business_name.select_one('a')['href']
    link = 'https://www.yelp.com' + link
    
    categories_price_location = restaurant.select_one('div[class*="priceCategory__"]')
    spans = categories_price_location.select('span')
    categories = spans[0].text.strip()
    location = spans[-1].text.strip()
    
    geo_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json?proximity={long},{lat}&access_token={access_token}"
    geo_response = requests.get(geo_url)
    geo_json = geo_response.json()
    center = geo_json['features'][0]['center']    
    print(name, ',', categories, ',', location, ',', center)
    
    doc = {
            'name': name,
            'categories': categories,
            'location': location,
            'link': link,
            'center': center,
        }

    db.restaurants.insert_one(doc)

    start += 10
    driver.get(f'{url}&start={start}')

driver.quit()