import requests
from bs4 import BeautifulSoup
import time

# List of URLs to monitor
urls = [
    'https://www.tarnowiak.pl/ogloszenia/motoryzacja/audi/',
    'https://www.tarnowiak.pl/ogloszenia/motoryzacja/bmw/',
    'https://www.tarnowiak.pl/ogloszenia/motoryzacja/daewoo/',
]

# Dictionary to track already seen entry URLs for each site
seen_entries = {url: set() for url in urls}

# Function to check for new entries on a given URL
def check_new_entries(url):
    global seen_entries

    # Make a GET request to fetch the raw HTML content
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all the boxes with the class 'box_content_plain'
        boxes = soup.find_all('div', class_='box_content_plain')

        # Loop through each box and extract the required information
        for box in boxes:
            # Extract the car name
            car_name = box.find('div', class_='box_content_desc').find('strong').text.strip()

            # Extract the description
            car_desc = box.find('div', class_='box_content_desc').find('p').text.strip()

            # Extract the price
            car_price = box.find('div', class_='box_content_price').find('strong').text.strip()

            # Extract the date
            car_date = box.find('div', style=lambda value: value and 'text-align: right' in value).text.strip()

            # Extract the link (as a unique identifier)
            car_link = box.find('a', class_='more')['href']

            # Check if the date contains "dzisiaj" and if the entry is new
            if "dzisiaj" in car_date and car_link not in seen_entries[url]:
                # Add the entry to the set of seen entries for this URL
                seen_entries[url].add(car_link)

                # Print the extracted information
                print(f"URL: {url}")
                print(f"Car Name: {car_name}")
                print(f"Description: {car_desc}")
                print(f"Price: {car_price}")
                print(f"Date Added: {car_date.replace('Dodane: ', '')}")
                print(f"Link: {car_link}")
                print('-' * 40)
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code} for URL: {url}")

# Listener loop to check for new entries on each URL every X seconds
def listener(interval=60):
    print("Starting listener... Press Ctrl+C to stop.")
    try:
        while True:
            for url in urls:
                check_new_entries(url)
            time.sleep(interval)  # Wait for the specified interval before checking again
    except KeyboardInterrupt:
        print("Listener stopped.")

# Start the listener with a 60-second interval
listener(interval=60)
