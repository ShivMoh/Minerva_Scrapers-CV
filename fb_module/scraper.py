
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, send_file, request, abort
import time
from bs4 import BeautifulSoup
import requests
import json
import os
import mimetypes

import fb_module.utils as utils

app = Flask(__name__)

def download(link, name):
    response = requests.get(link)
    if response.status_code != 200: print("Unable to download")
    print("Downloading...", name)
    try:
        with open(name, 'wb') as f:
            f.write(response.content)
    except:
        print("something went wrong")
import requests

def posts_from_facebook_post():

    group_url = "https://www.facebook.com/groups/1123069989695162"
    group_id = "1123069989695162"
    url = f"https://api.scrapecreators.com/v1/facebook/group/posts?url={group_url}&group_id={group_id}"
    headers = {
        "x-api-key": "cZKgtdBAHLfJ2CO6p8G54Gj5rHJ2"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    return data


def get_fb_group_posts():
    global json_data, history

    data = posts_from_facebook_post()
 
    # data = {'success': True, 'posts': [{'id': '1123072513028243', 'text': 'Something post', 'url': 'https://www.facebook.com/groups/1123069989695162/permalink/1123072513028243/', 'author': {'__typename': 'User', 'name': 'Shivesh Mohamed', 'short_name': 'Shivesh', 'id': 'pfbid02SBqbkwGGmqPB7hVXU1QJL6rqwrrwwisEf1Fzt8desqgr3aVpA25KNSrwSayFjo3Vl'}, 'reactionCount': 0, 'commentCount': 0, 'videoViewCount': None, 'videoDetails': {}, 'topComments': []}, {'id': '1123070636361764', 'text': 'is this a working posting', 'url': 'https://www.facebook.com/groups/1123069989695162/permalink/1123070636361764/', 'author': {'__typename': 'User', 'name': 'Shivesh Mohamed', 'short_name': 'Shivesh', 'id': 'pfbid02SBqbkwGGmqPB7hVXU1QJL6rqwrrwwisEf1Fzt8desqgr3aVpA25KNSrwSayFjo3Vl'}, 'reactionCount': 0, 'commentCount': 0, 'videoViewCount': None, 'videoDetails': {}, 'topComments': []}, {'id': '1123070536361774', 'text': 'will this work', 'url': 'https://www.facebook.com/groups/1123069989695162/permalink/1123070536361774/', 'author': {'__typename': 'User', 'name': 'Shivesh Mohamed', 'short_name': 'Shivesh', 'id': 'pfbid02SBqbkwGGmqPB7hVXU1QJL6rqwrrwwisEf1Fzt8desqgr3aVpA25KNSrwSayFjo3Vl'}, 'reactionCount': 0, 'commentCount': 0, 'videoViewCount': None, 'videoDetails': {}, 'topComments': []}], 'cursor': 'AQHR9YrKzFfJghDLyOoYkZzmBbixwt2ZHPp9aT6Qdv1zp-IVhkAQzubAv0lt2oq3HAKutouTWqgi6G_HA8iQ4eqTgw:eyIwIjoxNzUxNzEzODU3LCIxIjo3NjgyLCIzIjowLCI0IjoxLCI1Ijo0LCI2IjowfQ=='}

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    json_data = []

    for datum in data["posts"]:

        if (is_duplicate(datum["id"])): continue

        url = datum["url"]
        driver.get(url)
        time.sleep(5)  

        soup = BeautifulSoup(driver.page_source, "html.parser")
        description = soup.find_all(name="div", class_="x1vvkbs")[0].text
        images = soup.find_all("img")

        img_paths = []
        if (len(images) > 0):
            for index, image in enumerate(images):
                # print(image.get("src"))
                if "scontent" not in image.get("src"): continue
                image_path = f"./fb_module/facebook/{datum['id']}_image_{index}.png"
                download(image.get("src"), image_path) 
                img_paths.append(image_path)
        
        data_obj = {
            "post_id" : datum["id"],
            "description" : description,
            "image_paths" : img_paths
        }

        json_data.append(data_obj)
        history.append(data_obj)

# this should ideally be a call to the mongdb to search for existing title
# but for now we're gonna do this
def is_duplicate(id):
    global history
    if len(history) == 0: return False
    for data in history:
        if data["post_id"] == id: return True

    return False


def send_posts():
  data = utils.read_json("./scraper/data/latest.json")

  for data_point in data:

    url = "http://localhost:3000/api/fb_scraper/submit"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": "d3deab80460763d8cfaa9159f9f2f64ef8cfac26a650ab97a736f192f4a7e204"
    }

    response = requests.post(url, json=data_point, headers=headers)
    result = response.json()
def run():
    global history, json_data

    print("I am running")
    history = utils.read_json("./fb_module/data/history.json")
    # print(history)
    if history is None: history = []

    get_fb_group_posts()

    utils.write_json(json_data, "./fb_module/data/latest.json")
    utils.write_json(history, "./fb_module/data/history.json")

    # send_posts()

    utils.clear("./fb_module/data/latest.json")




