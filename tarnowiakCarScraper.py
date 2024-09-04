import random
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

# Initialize colorama
init(autoreset=True)

# Configuration for each site
sites = [
    {
        'name': 'Tarnowiak',
        'urls': [
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/audi/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/bmw/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/deawoo/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/fiat/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/ford/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/honda/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/mazda/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/mercedes/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/nissan/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/opel/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/peugeot/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/renault/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/seat/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/skoda/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/toyota/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/volkswagen/',
            'https://www.tarnowiak.pl/ogloszenia/motoryzacja/inne-marki/'
        ],
        'scrape_function': 'scrape_tarnowiak'
    },
    {
        'name': 'Otomoto',
        'urls': [
            'https://www.otomoto.pl/osobowe/tarnow?search%5Bdist%5D=120&search%5Border%5D=created_at_first%3Adesc',
            'https://www.otomoto.pl/osobowe/honda/prelude?search%5Border%5D=created_at_first%3Adesc',
            # 'https://www.otomoto.pl/osobowe/honda/integra?search%5Border%5D=created_at_first%3Adesc',
        ],
        'scrape_function': 'scrape_otomoto'
    },
    {
        'name': 'OLX',
        'urls': [
            'https://www.olx.pl/motoryzacja/samochody/tarnow/?search%5Bdist%5D=120&search%5Border%5D=created_at:desc',
            'https://www.olx.pl/motoryzacja/samochody/q-honda-prelude-iv/?search%5Border%5D=created_at:desc',
            # 'https://www.olx.pl/motoryzacja/samochody/q-honda-integra/?search%5Border%5D=created_at:desc',
        ],
        'scrape_function': 'scrape_olx'
    },
    {
        'name': 'Sprzedajemy',
        'urls': [
            'https://sprzedajemy.pl/tarnow/motoryzacja/samochody-osobowe?inp_distance=120'
            'https://sprzedajemy.pl/szukaj?inp_category_id=2&inp_category_id=6&inp_category_id=583&inp_category_id=802&catCode=6bea9f&inp_location_id=1&inp_location_id=0&inp_seller_type_id=&inp_condition_id=&inp_price%5Bfrom%5D=&inp_price%5Bto%5D=&inp_last_days=&inp_attribute_1600%5Bfrom%5D=&inp_attribute_1600%5Bto%5D=&inp_attribute_1605=&inp_attribute_466%5Bfrom%5D=&inp_attribute_466%5Bto%5D=&inp_attribute_471%5Bto%5D=&inp_attribute_222=&inp_attribute_476%5Bfrom%5D=&inp_attribute_476%5Bto%5D=&inp_attribute_456%5Bfrom%5D=&inp_attribute_456%5Bto%5D=&inp_attribute_461=&inp_attribute_491=&inp_category_id=802&inp_location_id=1&sort=inp_srt_date_d&items_per_page=30',
        ],
        'scrape_function': 'scrape_sprzedajemy'
    }
]

seen_entries = {site['name']: {url: set() for url in site['urls']} for site in sites}

# Define a list of colors for the sites
site_colors = [Fore.RED, Fore.GREEN, Fore.BLUE, Fore.YELLOW]

# Create a dictionary to map each site name to a specific color
site_name_to_color = {site['name']: site_colors[i % len(site_colors)] for i, site in enumerate(sites)}

# Define headers with a User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def scrape_tarnowiak(url, site_name):
    global seen_entries

    try:
        response = requests.get(url, headers=headers, timeout=10)  # Set a timeout of 10 seconds
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        # print(f"Successfully retrieved the webpage for URL: {url}")
    except requests.exceptions.RequestException as e:
        # print(f"Failed to retrieve the webpage. Error: {e} for URL: {url}")
        return

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all the boxes with the class 'box_content_plain'
    boxes = soup.find_all('div', class_='box_content_plain')

    # Loop through each box and extract the required information
    for box in boxes:
        # Extract the car name
        car_name_tag = box.find('div', class_='box_content_desc').find_all('strong')
        if len(car_name_tag) > 1:
            car_name = car_name_tag[1].text.strip()
        else:
            car_name = "Unknown"

        # Extract the price
        car_price_tag = box.find('div', class_='box_content_price').find('strong')
        if car_price_tag:
            car_price = car_price_tag.text.strip()
        else:
            car_price = "Unknown"

        # Extract the description
        car_desc = box.find('div', class_='box_content_desc').find('p').text.strip()
        
        # Extract the date
        car_date = box.find('div', style=lambda value: value and 'text-align: right' in value).text.strip()

        # Extract the link (as a unique identifier)
        car_link = box.find('a', class_='more')['href']
        full_link = urljoin(url, car_link)

        # Extract the image link
        img_tag = box.find('div', class_='box_content_photo').find('img')
        if img_tag:
            img_src = img_tag['src']
            full_img_link = urljoin('https://www.tarnowiak.pl/', img_src)
        else:
            full_img_link = "Unknown"

        # Check if the date contains "dzisiaj" and if the entry is new
        if "dzisiaj" in car_date and car_link not in seen_entries[site_name][url]:
            # Add the entry to the set of seen entries for this URL
            seen_entries[site_name][url].add(car_link)

            # Get the color for the current site
            color = site_name_to_color[site_name]

            # Print the extracted information with the site name in color
            print(f"{color}Site Name: {site_name}")
            print(f"URL: {url}")
            print(f"Car Name: {car_name}")
            print(f"Description: {car_desc}")
            print(f"Price: {car_price}")
            print(f"Date Added: {car_date.replace('Dodane: ', '')}")
            print(f"Link: {full_link}")
            print(f"Image Link: {full_img_link}")
            print('-' * 40)

            # Send the data to the Node.js server
            data = {
                'url': url,
                'site_name': site_name,
                'car_name': car_name,
                'description': car_desc,
                'price': car_price,
                'date_added': car_date.replace('Dodane: ', ''),
                'link': full_link,
                'imgLink': full_img_link
            }
            try:
                response = requests.post('http://localhost:4000/api/carData', json=data)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Failed to send data to the server. Error: {e}")

def scrape_otomoto(url, site_name):
    global seen_entries

    try:
        response = requests.get(url, headers=headers, timeout=10)  # Set a timeout of 10 seconds
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        # print(f"Successfully retrieved the webpage for URL: {url}")
    except requests.exceptions.RequestException as e:
        # print(f"Failed to retrieve the webpage. Error: {e} for URL: {url}")
        return

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all articles with the specified class
    articles = soup.find_all('article', class_='ooa-yca59n efpuxbr0')

    # Loop through each article and extract the required information
    for article in articles:
        # Extract the car name
        car_name_tag = article.find('h1', class_='efpuxbr9 ooa-1ed90th er34gjf0')
        car_name = car_name_tag.text.strip() if car_name_tag else "Unknown"

        # Extract the price
        car_price_tag = article.find('h3', class_='efpuxbr16 ooa-1n2paoq er34gjf0')
        car_price = car_price_tag.text.strip() if car_price_tag else "Unknown"

        # Extract the description
        car_desc_tag = article.find('p', class_='efpuxbr10 ooa-1tku07r er34gjf0')
        car_desc = car_desc_tag.text.strip() if car_desc_tag else "Unknown"

        # Extract the link (as a unique identifier)
        car_link_tag = article.find('a', href=True)
        car_link = car_link_tag['href'] if car_link_tag else "Unknown"
        full_link = urljoin(url, car_link)

        # Extract the image link
        img_tag = article.find('img', class_='e17vhtca4 ooa-2zzg2s')
        if not img_tag:
            img_tag = article.find('img', class_='e9xldqm4 ooa-2zzg2s')
        full_img_link = img_tag['src'] if img_tag else "Unknown"

        # Check if the entry is new
        if car_link not in seen_entries[site_name][url]:
            # Add the entry to the set of seen entries for this site and URL
            seen_entries[site_name][url].add(car_link)

            # Get the color for the current site
            color = site_name_to_color[site_name]

            # Print the extracted information with the site name in color
            print(f"{color}Site Name: {site_name}")
            print(f"URL: {url}")
            print(f"Car Name: {car_name}")
            print(f"Description: {car_desc}")
            print(f"Price: {car_price}")
            print(f"Link: {full_link}")
            print(f"Image Link: {full_img_link}")
            print('-' * 40)

            # Send the data to the Node.js server
            data = {
                'url': url,
                'site_name': site_name,
                'car_name': car_name,
                'description': car_desc,
                'price': car_price,
                'link': full_link,
                'imgLink': full_img_link
            }
            try:
                response = requests.post('http://localhost:4000/api/carData', json=data)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Failed to send data to the server. Error: {e}")

def scrape_olx(url, site_name):
    global seen_entries

    try:
        response = requests.get(url, timeout=10)  # Set a timeout of 10 seconds
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        # print(f"Successfully retrieved the webpage for URL: {url}")
    except requests.exceptions.RequestException as e:
        # print(f"Failed to retrieve the webpage. Error: {e} for URL: {url}")
        return

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all cards with the specified data-cy attribute
    cards = soup.find_all('div', {'data-cy': 'l-card'})

    for card in cards[:5]:
        # Skip the card if it has a "Wyróżnione" tag
        if card.find('span', text='Wyróżnione'):
            continue

        # Extract the car name
        car_name_tag = card.find('h6', class_='css-1wxaaza')
        car_name = car_name_tag.text.strip() if car_name_tag else "Unknown"

        # Extract the price
        car_price_tag = card.find('p', {'data-testid': 'ad-price'})
        car_price = car_price_tag.text.strip() if car_price_tag else "Unknown"
        # Remove "do negocjacji" if present
        if "do negocjacji" in car_price:
            car_price = car_price.replace("do negocjacji", "").strip()

        # Extract the description (if available)
        car_desc = "Description not available"

        # Extract the link (as a unique identifier)
        car_link_tag = card.find('a', href=True)
        car_link = car_link_tag['href'] if car_link_tag else "Unknown"
        full_link = urljoin(url, car_link)

        # Extract the location and date
        location_date_tag = card.find('p', {'data-testid': 'location-date'})
        if location_date_tag:
            location_date_text = location_date_tag.text.strip()
            # Split the text to isolate the location and date
            location_date_parts = location_date_text.split(' - ')
            # Concatenate the location and date to form a single string
            location_date = ' - '.join(location_date_parts) if len(location_date_parts) > 1 else location_date_text

            # Adjust the time if it contains "Dzisiaj o"
            if "Dzisiaj o" in location_date:
                time_part = location_date.split('Dzisiaj o ')[1]
                time_obj = datetime.strptime(time_part, '%H:%M')
                adjusted_time = (time_obj + timedelta(hours=2)).strftime('%H:%M')
                location_date = location_date.replace(time_part, adjusted_time)
        else:
            location_date = "Unknown"

        # Check if the date is "Dzisiaj o yy:yy"
        if "Dzisiaj o" not in location_date:
            continue

        # Extract the image link
        img_tag = card.find('img')
        img_link = img_tag['src'] if img_tag else "Unknown"

        # Check if the entry is new
        if car_link not in seen_entries.get(site_name, {}).get(url, set()):
            # Add the entry to the set of seen entries for this site and URL
            seen_entries.setdefault(site_name, {}).setdefault(url, set()).add(car_link)

            # Get the color for the current site
            color = site_name_to_color[site_name]

            # Print the extracted information with the site name in color
            print(f"{color}Site Name: {site_name}")
            print(f"URL: {url}")
            print(f"Car Name: {car_name}")
            print(f"Description: {car_desc}")
            print(f"Price: {car_price}")
            print(f"Link: {full_link}")
            print(f"Image Link: {img_link}")
            print(f"Location and Date: {location_date}")
            print('-' * 40)

            # Send the data to the Node.js server
            data = {
                'url': url,
                'site_name': site_name,
                'car_name': car_name,
                'description': car_desc,
                'price': car_price,
                'date_added': location_date,
                'link': full_link,
                'imgLink': img_link,
            }
            try:
                response = requests.post('http://localhost:4000/api/carData', json=data)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Failed to send data to the server. Error: {e}")

def scrape_sprzedajemy(url, site_name):
    global seen_entries

    try:
        response = requests.get(url, headers=headers, timeout=10)  # Set a timeout of 10 seconds
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the webpage. Error: {e} for URL: {url}")
        return

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all articles with the class 'element'
    articles = soup.find_all('article', class_='element')

    # Loop through each article and extract the required information
    for article in articles:
        # Extract the car name
        car_name_tag = article.find('h2', class_='title').find('a')
        car_name = car_name_tag.text.strip() if car_name_tag else "Unknown"

        # Extract the price
        car_price_tag = article.find('span', class_='price')
        car_price = car_price_tag.text.strip() if car_price_tag else "Unknown"

        # Extract the link (as a unique identifier)
        car_link_tag = article.find('a', class_='offerLink', href=True)
        car_link = car_link_tag['href'] if car_link_tag else "Unknown"
        full_link = urljoin(url, car_link)

        # Extract the image link
        img_tag = article.find('img')
        img_link = img_tag['src'] if img_tag else "Unknown"

        # Extract the date and time
        car_date_tag = article.find('time', class_='time')
        car_date = car_date_tag['datetime'] if car_date_tag else "Unknown"

        # Extract the location
        location_tag = article.find('strong', class_='city')
        location = location_tag.text.strip() if location_tag else "Unknown"

        # Format the date and time
        if car_date != "Unknown":
            date_obj = datetime.strptime(car_date, "%Y-%m-%d %H:%M:%S")
            formatted_date = date_obj.strftime("%m-%d %H:%M")
        else:
            formatted_date = "Unknown"

        # Combine location with formatted date and time
        location_date = f"{location} - {formatted_date}"

        # Check if the entry is new
        if car_link not in seen_entries[site_name][url]:
            # Add the entry to the set of seen entries for this URL
            seen_entries[site_name][url].add(car_link)

            # Get the color for the current site
            color = site_name_to_color[site_name]

            # Print the extracted information with the site name in color
            print(f"{color}Site Name: {site_name}")
            print(f"URL: {url}")
            print(f"Car Name: {car_name}")
            print(f"Price: {car_price}")
            print(f"Date Added: {location_date}")
            print(f"Link: {full_link}")
            print(f"Image Link: {img_link}")
            print('-' * 40)

            # Send the data to the Node.js server
            data = {
                'url': url,
                'site_name': site_name,
                'car_name': car_name,
                'price': car_price,
                'date_added': location_date,
                'location': location,
                'link': full_link,
                'imgLink': img_link
            }
            try:
                response = requests.post('http://localhost:4000/api/carData', json=data)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Failed to send data to the server. Error: {e}")

def scrape_site(site):
    for url in site['urls']:
        scrape_function = globals()[site['scrape_function']]
        scrape_function(url, site['name'])

def listener():
    print("Starting listener... Press Ctrl+C to stop.")
    try:
        while True:
            with ThreadPoolExecutor(max_workers=len(sites)) as executor:
                futures = [executor.submit(scrape_site, site) for site in sites]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Error occurred: {e}")
            interval = random.randint(45, 95)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Listener stopped.")

listener()