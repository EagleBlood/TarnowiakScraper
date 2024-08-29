import random
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed

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
            'https://www.otomoto.pl/osobowe/tarnow?search%5Bdist%5D=50&search%5Border%5D=created_at_first%3Adesc',
        ],
        'scrape_function': 'scrape_otomoto'
    },
    {
        'name': 'OLX',
        'urls': [
            'https://www.olx.pl/motoryzacja/samochody/tarnow/?search%5Bdist%5D=50&search%5Border%5D=created_at:desc',
        ],
        'scrape_function': 'scrape_olx'
    }
]

seen_entries = {site['name']: {url: set() for url in site['urls']} for site in sites}

# Define a list of colors
colors = [
    Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE,
    Fore.LIGHTBLACK_EX, Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTBLUE_EX,
    Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTWHITE_EX
]

# Create a dictionary to map each URL to a specific color
url_colors = {url: colors[i % len(colors)] for site in sites for i, url in enumerate(site['urls'])}

def scrape_tarnowiak(url, site_name):
    global seen_entries

    try:
        response = requests.get(url, timeout=10)  # Set a timeout of 10 seconds
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the webpage. Error: {e} for URL: {url}")
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

            # Get the color for the current URL
            color = url_colors[url]

            # Print the extracted information with the URL in color
            print(f"{color}URL: {url}")
            print(f"Site Name: {site_name}")
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
        response = requests.get(url, timeout=10)  # Set a timeout of 10 seconds
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the webpage. Error: {e} for URL: {url}")
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

            # Get the color for the current URL
            color = url_colors.get(url, Fore.WHITE)

            # Print the extracted information with the URL in color
            print(f"{color}URL: {url}")
            print(f"Site Name: {site_name}")
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
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the webpage. Error: {e} for URL: {url}")
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

            # Get the color for the current URL
            color = url_colors.get(url, Fore.WHITE)

            # Print the extracted information with the URL in color
            print(f"{color}URL: {url}")
            print(f"Site Name: {site_name}")
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
# url = 'https://www.otomoto.pl/osobowe/tarnow?search%5Bdist%5D=50&search%5Border%5D=created_at_first%3Adesc'
# site_name = 'Otomoto'
# scrape_another_site(url, site_name)