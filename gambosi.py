import argparse
import requests
import re
import os
from bs4 import BeautifulSoup
from jsbeautifier import beautify
from urllib.parse import urljoin
from rich import print

def extract_js_urls(page_url):
    js_urls = set()
    try:
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tags = soup.find_all('script', src=True)
        
        for script_tag in script_tags:
            js_url = script_tag['src']
            full_js_url = urljoin(page_url, js_url)

            if page_url in full_js_url:
                js_urls.add(full_js_url)
            
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la página: {e}")
    
    return js_urls

def extract_endpoints(js_url):
    endpoints = set()
    urls = set()

    try:
        js_response = requests.get(js_url)
        js_code = js_response.text
        lines = js_code.split('\n')  # Divide el código en líneas

        for line_number, line in enumerate(lines, start=1):
            url_matches = re.findall(r'(?:(?:https?://|www\.)[^\s/$.?#].[^\s]*)', line)
            endpoint_matches = re.findall(r'["\'](/[^"\']{5,})["\']', line)

            for url in url_matches:
                urls.add(url)

            for endpoint in endpoint_matches:
                if len(endpoint) > 4:
                    endpoints.add(endpoint)

        if urls:
            for url in urls:
                print(f"[yellow3][-][dark_olive_green1] URL found in [white]{js_url}[dark_olive_green1] [Line {line_number}]: [red1]{url}")

        if endpoints:
            for endpoint in endpoints:
                print(f"[yellow3][-][dark_olive_green1] Endpoint found in [white]{js_url}[dark_olive_green1] [Line {line_number}]: [red1]{endpoint}")

    except requests.exceptions.RequestException as e:
        print(f"[red]Error getting JavaScript file: {e}")

def has_basic_auth(js_url):
    try:
        js_response = requests.get(js_url)
        js_code = js_response.text
        lines = js_code.split('\n')  # Divide el código en líneas

        for line_number, line in enumerate(lines, start=1):
            if "basic" in line.lower():
                base64_matches = re.findall(r'["\'](Y[A-Za-z0-9+/=]+)["\']', line)
                for base64_match in base64_matches:
                    try:
                        decoded_data = base64.b64decode(base64_match)
                        if decoded_data:
                            print(f"[yellow3][-][dark_olive_green1] AUTHORIZATION BASIC found in [white]{js_url}[dark_olive_green1] [Line {line_number}]: [red1]{decoded_data.decode('utf-8')}")
                    except:
                        pass
    
    except requests.exceptions.RequestException as e:
        print(f"[red]Error getting JavaScript file: {e}")

def find_api_keys(js_url):
    api_keys_file_path = os.path.join("data", "api_keys.txt")
    api_key_patterns = {}

    try:
        with open(api_keys_file_path, "r") as api_keys_file:
            api_key_data = api_keys_file.read()
            api_key_patterns = eval(api_key_data)
    
    except Exception as e:
        print(f"[red]Error reading API key file: {e}")
        return

    try:
        js_response = requests.get(js_url)
        js_code = js_response.text

        lines = js_code.split('\n')  # Divide el código en líneas
        for line_number, line in enumerate(lines, start=1):
            for api_name, regex_pattern in api_key_patterns.items():
                matches = re.search(regex_pattern, line)
                if matches:
                    print(f"[yellow3][-][dark_olive_green1] Posible [white]{api_name}[dark_olive_green1] found in [white]{js_url}[dark_olive_green1] [Line {line_number}]: [red1]{matches.group(0)}")
    
    except requests.exceptions.RequestException as e:
        print(f"[red]Error getting JavaScript file: {e}")

def find_users_in_js(js_url):
    users_file_path = os.path.join("data", "users.txt")
    users_list = []

    try:
        with open(users_file_path, "r") as users_file:
            users_list = [line.strip() for line in users_file.readlines()]

    except Exception as e:
        print(f"[red]Error reading user file: {e}")
        return

    try:
        js_response = requests.get(js_url)
        js_code = js_response.text

        lines = js_code.split('\n')  # Divide el código en líneas
        for line_number, line in enumerate(lines, start=1):
            for username in users_list:
                if username in line:
                    print(f"[yellow3][-][dark_olive_green1] Posible username or password found in [white]{js_url}[dark_olive_green1] [Line {line_number}]: [red1]{username}")

    except requests.exceptions.RequestException as e:
        print(f"[red]Error getting JavaScript file: {e}")
        
def find_interesting_words_in_js(js_url):
    interesting_words = ["user", "pass", "password", "key", "api"]  
    try:
        js_response = requests.get(js_url)
        js_code = js_response.text

        lines = js_code.split('\n') 
        for line_number, line in enumerate(lines, start=1):
            for word in interesting_words:
                if word in line:
                    print(f"[yellow3][-][dark_olive_green1] Possible interesting word found in [white]{js_url}[dark_olive_green1] [Line {line_number}]: [red1]{word}")

    except requests.exceptions.RequestException as e:
        print(f"[red]Error getting JavaScript file: {e}")

def beautify_js(js_code):
    try:
        return beautify(js_code)
    except Exception as e:
        print(f"[red]Error beautifying JavaScript code: {e}")
        return js_codess

def main():
    parser = argparse.ArgumentParser(description="Crawlea archivos JavaScript en una página web y muestra los endpoints.")
    parser.add_argument("-u", "--url", required=True, help="URL de la página web")
    args = parser.parse_args()
    
    print(f"""[bold magenta3]
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@           @@@@@@@@
@@@@@@@@@@@             @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@              @@@@@@@@@
@@@@@@@@@@@              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@              @@@@@@@@@@
@@@@@@@@@@@@                @@@@@@@@@@@@@@@@@@@@@@@@@@             @@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@&@@&@&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&&&@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    """)
    
    print(f"[bold yellow3][*][bold green3][bold magenta3] gambosi v1.0 | by @robotshelld [bold yellow3][*][bold green3]\n")
    page_url = args.url

    js_urls = extract_js_urls(page_url)

    if js_urls:
        print(f"[bold yellow3][*][bold green3] Number of JavaScript files found in [bold white] {page_url}: [bold yellow3]{len(js_urls)}")
        print(f"[bold yellow3][+][bold green3] JavaScript files found:")

        for js_url in js_urls:
            print(f"[white]{js_url}")

        print("\n[bold yellow3][+][bold green3] Analyzing JavaScript files\n")

        for js_url in js_urls:
            js_response = requests.get(js_url)
            js_code = js_response.text
            # Formatear el código JavaScript
            formatted_js_code = beautify_js(js_code)  
            
            endpoints = extract_endpoints(js_url)
            has_basic_auth(js_url)
            find_users_in_js(js_url)      
            find_api_keys(js_url)
            find_interesting_words_in_js(js_url)

    else:
        print(f"[bold red]No JavaScript files found in [bold white]{page_url}")

if __name__ == "__main__":
    main()
