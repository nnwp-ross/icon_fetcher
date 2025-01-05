import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from requests.exceptions import RequestException
import time

def ensure_http_scheme(url):
    if not urlparse(url).scheme:
        return f'http://{url}'
    return url

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def fetch_favicon(url, retries=3, delay=5):
    url = ensure_http_scheme(url)
    
    if not is_valid_url(url):
        raise ValueError(f"Invalid URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.206.25.107 Safari/537.36',
        'Referer': url
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            break
        except requests.HTTPError as e:
            if response.status_code == 403:
                raise Exception(f"Access forbidden: {e}")
            else:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    raise Exception(f"Failed to fetch website: {e}")
        except RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise Exception(f"Failed to fetch website: {e}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Look for the favicon link tag
    icon_link = soup.find('link', rel=lambda value: value and 'icon' in value.lower())
    shortcut_icon = soup.find('link', rel=lambda value: value and 'shortcut icon' in value.lower())
    apple_touch_icon = soup.find('link', rel=lambda value: value and 'apple-touch-icon' in value.lower())


    if icon_link:
        icon_url = icon_link['href']
    elif shortcut_icon:
        icon_url = shortcut_icon['href']
    elif apple_touch_icon:
        icon_url = apple_touch_icon['href']
    else:
        # Handle relative URLs
        icon_url = '/favicon.ico'

    return urljoin(url, icon_url)

def download_favicon(icon_url, save_path):
    try:
        # Download the favicon
        response = requests.get(icon_url)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Favicon saved to {save_path}")
    except RequestException as e:
        raise Exception(f"Failed to download favicon: {e}")

#download_favicon('http://fortnite.com/favicon.ico', 'fn.ico')

if __name__ == '__main__':
    website_url = input("Input url (https://example.com): ")  # Replace with the target website
    output = input("Output: ")
    try:
        favicon_url = fetch_favicon(website_url)
        print(f"Favicon URL: {favicon_url}")
        download_favicon(favicon_url, f'icon/{output}.ico')
    except ValueError as ve:
        print(f"URL is not valid: {ve}")
    except Exception as e:
        print(f"Error: {e}")