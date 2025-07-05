from bs4 import BeautifulSoup
import requests
import os
import time
import json
from scraper.utils import write_json, read_json

def download(link, name):
    response = requests.get(link)
    if response.status_code != 200: print("Unable to download")
    print("Downloading...", name)
    try:
        with open(name, 'wb') as f:
            f.write(response.content)
    except:
        print("something went wrong")

def scrape_stabroak():
    global data
    for keyword in keywords:
        search = f"health and safety {keyword}"
       
        query = f"https://www.stabroeknews.com/?s={search}"
        response = requests.get(query)
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = soup.find_all(name='article')
        for article in articles:
    
            link = (article.find(name='h2')).find(name="a")
            link = link.get('href')

            article_page = requests.get(link)
            article_soup_page = BeautifulSoup(article_page.text, 'html.parser')

            other = article_soup_page.find(name="div", class_="most-popular")
            if other:
                other.decompose()

            name = article_soup_page.find(name='h1', class_='article-title')
            date = article_soup_page.find(name="time", class_='article-time').get("datetime")

            if is_duplicate(name.text): continue

            paragraphs = []

            paragraphs_html = article_soup_page.find(name="div", class_="article-content")

            if paragraphs_html == None: continue
            
            paragraphs_html = paragraphs_html.find_all(name="p")

            for para in paragraphs_html:
                paragraphs.append(para.text)

            images = article_soup_page.find_all('img')

            image_paths = []
            
            for index, image in enumerate(images):
                img_src, alt = image.get('src'), image.get('alt')
                if alt == "Stabroek News": continue
                if not os.path.exists("stabroak"): os.makedirs("stabroak")                 
                download(img_src, f"./scraper/stabroak/{name.text}_img_{index}.png")
                image_paths.append(f"./scraper/stabroak/{name.text}_img_{index}.png")

            data_obj = {
                "title": name.text,
                "date": date,
                "paragraphs" : paragraphs,
                "image_paths" : image_paths,
                "url": link
            }

            data.append(data_obj)
            history.append(data_obj)

def scrape_inews():
    global data
    for keyword in keywords:
        search = f"{keyword}"
        query = f"https://inewsguyana.com/?s={search}"
        print(query)
        response = requests.get(query, timeout=10)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = soup.find_all('div', class_="td_module_16")

        time.sleep(5)

        others = soup.find_all('div', class_='td_block_wrap')
        # print(len(others))
        if len(others) > 0: 
            for other in others:
                other.decompose()
        relateds = soup.find_all('div', class_='tdi_3')


        if (len(relateds) > 0):
            for related in relateds:
                related.decompose()
                
        for article in articles:
            if article is None: 
                print(article)
                continue
            
            link = article.find('h3', class_='entry-title')
            if (link == None): continue
            link = link.find('a')
            time.sleep(1)
            article_page = requests.get(link.get('href'))
            article_soup_page = BeautifulSoup(article_page.text, 'html.parser')
            
            name = article_soup_page.find_all(name='h1', class_='entry-title')
            entry_date = article_soup_page.find(name="time", class_="entry-date")
            entry_date = entry_date.get("datetime")

            content = article_soup_page.find(name="div", class_="td-post-content").find_all(name="p")
            paragraphs = []
            # get all paragraphs for article
            for paragraph in content:
                paragraphs.append(paragraph.text)

            if (len(name) == 0): continue

            name = name[0]

            if is_duplicate(name.text): continue 

            images = article_soup_page.find(name='div', class_='td-post-content').find_all(name='img')
            image_paths = []
            
            # get all images for article
            if (len(images) > 0):
                # print(len(images))
                for index, image in enumerate(images):
                    # print(image)
                    img_src, alt = image.get('src'), image.get('alt')
                    if not os.path.exists("inews"): os.makedirs("inews")                 
                    file_name = f"{name.text}_img_{index}.png"
                    path = os.path.join("./scraper/inews", file_name)
                    download(img_src, path)

                    image_paths.append(path)
            

            data_obj = {
                "title": name.text,
                "date": entry_date,
                "paragraphs" : paragraphs,
                "image_paths" : image_paths,
                "url": link.get("href")
            }

            data.append(data_obj)
            history.append(data_obj)

# blocked via bot spam detection whatever
def scrape_demerara():
    global data
    for keyword in keywords:
        search = f"{keyword}"
        query = f"https://demerarawaves.com/?s={search}"
        print(query)
        response = requests.get(query, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = soup.find_all(name='article')
        print(len(articles))
        for article in articles:
            # print(article)
            link = (article.find(name='div', class_="post-thumbnail")).find(name="a")
            link = link.get('href')
            article_page = requests.get(link)
            article_soup_page = BeautifulSoup(article_page.text, 'html.parser')
            # other = article_soup_page.find(name="div", class_="most-popular")
            # if other:
            #    other.decompose()

            name = article_soup_page.find_all(name='span')

            if is_duplicate(name[0].text): continue 

            if (len(name) == 0): continue

            name = name[0]
          
            images = article_soup_page.find_all('img')
            
            if (len(images) > 0):
                print(len(images))
                for index, image in enumerate(images):
                    # print(image)
                    img_src, alt = image.get('src'), image.get('alt')
                    if not os.path.exists("demerara"): os.makedirs("demerara")                 
                    download(img_src, f"./stabroak/{name.text}_img_{index}.png")
            else: print("No images found")

# this should ideally be a call to the mongdb to search for existing title
# but for now we're gonna do this
def is_duplicate(title):
    global history
    if len(history) == 0: return False
    for data in history:
        if data["title"] == title: return True

    return False

def run():
    global keywords, data, history
    data = read_json("./scraper/data/articles_summary.json")
    if data is None: data = []

    history = read_json("./scraper/data/history.json")
    if history is None: 
        history = []
        print("no history currently")

    keywords = [
        "hazard",
        # "risk",
        # "exposure",
        # "near miss",
        # "accident",
        # "injury",
        # "unsafe",
        # "dangerous",
        # "toxic",
        # "fire",
        # "explosion",
        # "spill",
        # "biohazard"
        # "electrocution"
        # "fall",
        # "trip",
        # "slip"
        # "sharp object"
        # "chemical"
    ]
    
    scrape_stabroak()
    # scrape_inews()

    print("Data", len(data), len(history))
    write_json(data, "./scraper/data/articles_summary.json")
    write_json(history, "./scraper/data/history.json")

