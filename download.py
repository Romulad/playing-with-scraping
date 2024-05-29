import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

from parsel import Selector
import requests

base_url = 'https://www.cometchat.com/docs/react-uikit/overview'

def get_random_user_agent():
    # you can also import SoftwareEngine, HardwareType, SoftwareType, Popularity from random_user_agent.params
    # you can also set number of user agents required by providing `limit` as parameter
    software_names = [SoftwareName.FIREFOX.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
    user_agent_rotator = UserAgent(
        software_names=software_names, operating_systems=operating_systems, limit=100
    )

    # Get Random User Agent String.
    return user_agent_rotator.get_random_user_agent()


def get_browser():
    options = options = webdriver.FirefoxOptions()
    # options.add_argument('--headless')
    options.add_argument(f'--lang=en')
    # options.add_argument('--proxy-server=%s' % TOR_PROXIES['https'])
    options.add_argument(f"user-agent={get_random_user_agent()}")
    browser = webdriver.Firefox(options=options)
    return browser

def get_content(url:str):
    # add support for relative path
    end_url = url # if url.startswith('http') else f"{base_url}{url}"
    try:
        resp = requests.get(end_url)
    except:
        return None

    if resp.status_code == 200:
        return {
            "text" : resp.text,
            "content": resp.content,
        }
    else:
        # Error has occured
        pass
    
    return resp.status_code


browser = get_browser()
browser.get(base_url)

WebDriverWait(browser, 50).until(
    EC.presence_of_element_located((By.TAG_NAME, 'app-main'))
)

time.sleep(10)

# browser.save_screenshot(f"{base_dir_name}/downloading_page.png")

page_source = browser.page_source

browser.quit()

# page_source = ""
# with open("test.html", "r") as init_f:
#     page_source = init_f.read()

base_dir_name = base_url.split('/')[-1]
os.makedirs(base_dir_name, exist_ok=True)

# write the source html to a local file
index_page_path = f"{base_dir_name}.html"
with open(index_page_path, 'w', encoding="utf-8") as index_f:
    index_f.write(page_source)

css_to_replace = {}
icon_link_to_replace = {}
js_to_replace = {}
link_to_replace = []

# ToDO: change this logique and add image downloading
with open(index_page_path, "r", encoding="utf-8") as f:
    init_content = f.read()
    selector = Selector(text=init_content)

    # get all `js` files, download the content 
    js_link_el = selector.xpath('//script[@src]')
    js_links = [link.attrib['src'] for link in js_link_el]
    name = "script"
    js_start = 0
    for js_link in js_links:
        print(f'downloading and writing js content for {js_link}')
        resul = get_content(js_link)
        if isinstance(resul, dict):
            script_name = f'{name}-{js_start}.js'
            script_path = f'{base_dir_name}/{script_name}'
            with open(script_path, "w", encoding="utf-8") as js_f:
                js_f.write(resul.get('text'))
            
            # script_path_ = script_path.split("/")[-1]
            js_to_replace[js_link] = f"./{script_path}"
        else:
            print(f'probleme when getting js content for {js_link}')
        js_start += 1

    link_to_replace.append(js_to_replace)

    # get all `stylesheet` css file, download the content
    css_link_el = selector.xpath('//link[@rel="stylesheet"]')
    css_links = [link.attrib['href'] for link in css_link_el]
    name = "sheet"
    start = 0
    for css_link in css_links:
        print(f'downloading and writing css content for {css_link}')
        resul = get_content(css_link)
        if isinstance(resul, dict):
            sheet_name = f'{name}-{start}.css'
            sheet_path = f'{base_dir_name}/{sheet_name}'
            with open(sheet_path, "w", encoding="utf-8") as cc_f:
                cc_f.write(resul.get('text'))
            
            # sheet_path_ = sheet_path.split("/")[-1]
            css_to_replace[css_link] = f"./{sheet_path}"
        else:
            print(f'probleme when getting css content for {css_link}')
        start += 1
    
    link_to_replace.append(css_to_replace)

    # get `icon` file, download the content, put it in a file  
    icon_link = selector.xpath('//link[@rel="icon"]').attrib["href"]
    icon_name = icon_link.split('/')[-1]
    print('downloading icon image')
    resul = get_content(icon_link)
    if isinstance(resul, dict):
        icon_path = f'{base_dir_name}/{icon_name}'
        with open(icon_path, "wb") as ic_f:
            ic_f.write(resul.get('content'))
        
        # icon_path_ = icon_path.split("/")[-1]
        icon_link_to_replace[icon_link] = f"./{icon_path}"
    else:
        print(f'probleme when getting icon image content {icon_link}')
    
    link_to_replace.append(icon_link_to_replace)


print('replacing links to match local path')
# change the content download link to match local path
with open(index_page_path, "r", encoding="utf-8") as f1:
    init_def = f1.read()
    end_content = ""
    for obj in link_to_replace:
        for ol_link, new_path in obj.items():
            end_content = init_def.replace(ol_link, new_path)
            init_def = end_content
    
    with open(index_page_path, "w", encoding="utf-8") as write_f:
        write_f.write(end_content)
    

