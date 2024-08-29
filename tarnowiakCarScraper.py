import random
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

urls = [
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
]

seen_entries = {url: set() for url in urls}

# Define a list of colors
colors = [
    Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE,
    Fore.LIGHTBLACK_EX, Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTBLUE_EX,
    Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTWHITE_EX
]

# Create a dictionary to map each URL to a specific color
url_colors = {url: colors[i % len(colors)] for i, url in enumerate(urls)}

def check_new_entries(url):
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
        if "dzisiaj" in car_date and car_link not in seen_entries[url]:
            # Add the entry to the set of seen entries for this URL
            seen_entries[url].add(car_link)

            # Get the color for the current URL
            color = url_colors[url]

            # Print the extracted information with the URL in color
            print(f"{color}URL: {url}")
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

def listener():
    print("Starting listener... Press Ctrl+C to stop.")
    try:
        while True:
            for url in urls:
                check_new_entries(url)
            interval = random.randint(45, 95)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Listener stopped.")

listener()