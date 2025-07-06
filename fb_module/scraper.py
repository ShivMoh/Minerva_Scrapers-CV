
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
import cv2 as cv
from pymongo import MongoClient
from datetime import datetime
import uuid



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
        "x-api-key": "11Km5rTUSoejAxdLnfTkwM7Zcj82"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    return data


def get_fb_group_posts():
    global json_data, history

    data = posts_from_facebook_post()
 
    # data = {'success': True, 'posts': [{'id': '1123012513028229', 'text': 'Something post', 'url': 'https://www.facebook.com/groups/1123069989695162/permalink/1123072513028243/', 'author': {'__typename': 'User', 'name': 'Shivesh Mohamed', 'short_name': 'Shivesh', 'id': 'pfbid02SBqbkwGGmqPB7hVXU1QJL6rqwrrwwisEf1Fzt8desqgr3aVpA25KNSrwSayFjo3Vl'}, 'reactionCount': 0, 'commentCount': 0, 'videoViewCount': None, 'videoDetails': {}, 'topComments': []}, {'id': '1123070636361764', 'text': 'is this a working posting', 'url': 'https://www.facebook.com/groups/1123069989695162/permalink/1123070636361764/', 'author': {'__typename': 'User', 'name': 'Shivesh Mohamed', 'short_name': 'Shivesh', 'id': 'pfbid02SBqbkwGGmqPB7hVXU1QJL6rqwrrwwisEf1Fzt8desqgr3aVpA25KNSrwSayFjo3Vl'}, 'reactionCount': 0, 'commentCount': 0, 'videoViewCount': None, 'videoDetails': {}, 'topComments': []}, {'id': '1123070536361774', 'text': 'will this work', 'url': 'https://www.facebook.com/groups/1123069989695162/permalink/1123070536361774/', 'author': {'__typename': 'User', 'name': 'Shivesh Mohamed', 'short_name': 'Shivesh', 'id': 'pfbid02SBqbkwGGmqPB7hVXU1QJL6rqwrrwwisEf1Fzt8desqgr3aVpA25KNSrwSayFjo3Vl'}, 'reactionCount': 0, 'commentCount': 0, 'videoViewCount': None, 'videoDetails': {}, 'topComments': []}], 'cursor': 'AQHR9YrKzFfJghDLyOoYkZzmBbixwt2ZHPp9aT6Qdv1zp-IVhkAQzubAv0lt2oq3HAKutouTWqgi6G_HA8iQ4eqTgw:eyIwIjoxNzUxNzEzODU3LCIxIjo3NjgyLCIzIjowLCI0IjoxLCI1Ijo0LCI2IjowfQ=='}

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    for datum in data["posts"]:

        if (is_duplicate(datum["id"])): continue

        url = datum["url"]
        driver.get(url)

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
            "image_paths" : img_paths,
            "url" : url
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


# def send_posts():
#   data = utils.read_json("./scraper/data/latest.json")

#   for data_point in data:   
#     url = "http://localhost:3000/api/fb_scraper/submit"
#     headers = {
#         "Content-Type": "application/json",
#         "x-api-key": "d3deab80460763d8cfaa9159f9f2f64ef8cfac26a650ab97a736f192f4a7e204"
#     }

#     encoded_images = []

#     if len(data_point["image_paths"]) > 0:
#         for image_path in data_point["image_paths"]:
#             image = cv.imread(image_path)
#             _, img_encoded = cv.imencode('.jpg', img=image)

#             encoded_images.append(img_encoded)

#     new_data_point = {
#         "post_id" : data_point["post_id"],
#         "description" : data_point["description"],
#         "images" : encoded_images
#     }

#     response = requests.post(url, json=new_data_point, headers=headers)
#     result = response.json()

def send_posts():
    url = "https://minerva-drab.vercel.app/api/reports/submit"
    api_key = "d3deab80460763d8cfaa9159f9f2f64ef8cfac26a650ab97a736f192f4a7e204"
    data = utils.read_json("./fb_module/scraper/data/latest.json")

    for data_point in data:   
        from datetime import datetime

        now = datetime.now()

        new_data_point = {
            "description" : data_point["description"],
            "location" : "N/A",
            "date" :  str(now)
        }

        if len(data_point["image_paths"]) > 0:
            with open(data_point["image_paths"][0], "rb") as img_file:
                specific_image_type = data_point["image_paths"][0].split('.')[-1]

                if not specific_image_type in ["jpg", "jpeg", "png"]: continue

                files = {
                    "data": (None, json.dumps(new_data_point), "application/json"),
                    "image": (data_point["image_paths"][0], img_file, f"image/{specific_image_type}")
                }

                headers = {
                    "x-api-key": api_key
                }

                # Send the POST request
                response = requests.post(url, files=files, headers=headers)


                if response.status_code == 200:
                    print("Success!")
                else:
                    print(f"Failed with status code {response.status_code}")
                    print(response.text)  # Show server error message if any
        else:
            headers = {
                "x-api-key": api_key
            }
            
            files = {
                "data": (None, json.dumps(new_data_point), "application/json")
            }

            # Send the POST request
            response = requests.post(url, files=files, headers=headers)

            if response.status_code == 200:
                print("Success!")
            else:
                print(f"Failed with status code {response.status_code}")
                print(response.text)  # Show server error message if any

def send_data_posts():
    data = utils.read_json("./fb_module/data/latest.json")
    print("latest data", data)
    client = MongoClient("mongodb+srv://admin:iPPgoPwwcqo472xN@cf-test.gfnjq.mongodb.net/hsse-hackathon?retryWrites=true&w=majority&appName=hsse-hackathon")
    db = client["hsse-hackathon"]
    reports = db["reports"]

    for data_point in data:   
        from datetime import datetime

        now = datetime.now()

        if len(data_point["image_paths"]) > 0:

            report = {
                "publicId" : uuid.uuid4().hex[:24],
                # "title": data_point["post_id"],
                "description": data_point["description"],
                # "location": "N/A", 
                
                "metadata": {
                    "imagePaths" : data_point["image_paths"]
                },
                "postUrl" : data_point["url"],
                "source" : "facebook",
                "createdAt": str(now),
            }

            # print(report)

            result = reports.insert_one(report)
            return result.inserted_id

        else:
            report = {
                "publicId" : uuid.uuid4().hex[:24],
                # "title": data_point["post_id"],
                "description": data_point["description"],
                "postUrl" : data_point["url"],
                "source" : "facebook",
                # "location": "N/A", 
                "createdAt": str(now)
            }
       

            print(report)

            result = reports.insert_one(report)
            return result.inserted_id




def run():
    global history, json_data

    print("I am running")
    history = utils.read_json("./fb_module/data/history.json")
    json_data = utils.read_json("./fb_module/data/latest.json")

    # print(history)
    if history is None: history = []
    if json_data is None: json_data = []

    get_fb_group_posts()

    utils.write_json(json_data, "./fb_module/data/latest.json")
    utils.write_json(history, "./fb_module/data/history.json")

    # turn this on to interface with backend
    send_data_posts()
    # send_posts()

    utils.clear("./fb_module/data/latest.json")
    utils.write_json([], "./fb_module/data/latest.json")



