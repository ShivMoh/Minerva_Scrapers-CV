import torch
from transformers import AutoTokenizer, BitsAndBytesConfig, AutoModelForCausalLM
import os
import time
import psutil
import GPUtil
import torch
import csv
import gc
import time
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
from threading import Thread
import subprocess
import os
import argparse
from transformers import AutoTokenizer
import json
from scraper.utils import read_json, write_json, clear
import requests
import cv2 as cv
import requests
import json
from pymongo import MongoClient
from datetime import datetime
import uuid

LLAMA_2_7 = "meta-llama/Llama-2-7b-chat-hf"
LLAMA_2_7_AWQ = "TheBloke/Llama-2-7B-Chat-AWQ"
LLAMA_2_7_GPTQ = "TheBloke/Llama-2-7b-chat-GPTQ"
MISTRAL = "mistralai/Mistral-7B-Instruct-v0.3"

def load_model(enabled_flash_attention = False, model_name = MISTRAL):

    model = None
    bnb_config = BitsAndBytesConfig(
      load_in_4bit=True,
      bnb_4bit_compute_dtype=torch.bfloat16,
      bnb_4bit_quant_type="nf4",
    )

    if enabled_flash_attention:
      model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map={"": 0},
        attn_implementation="flash_attention_2",
    )
    else:
      model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map={"": 0}
      )
    return model

def format_responses():
  model = load_model(False, MISTRAL).to('cuda')
  data = read_json("./scraper/data/articles_summary.json")

  new_data = []

  for datum in data:
    string = ""
    for paragraph in datum["paragraphs"]:
      string += paragraph

    prompt = f"""
        <|system|>
        You are a helpful assistant that summarizes incidents and classifies them as health and safety violations.
        <|user|>
        You are given a description of an incident.

      
        1. Determine whether the incident qualifies as a health and safety violation. Respond only with `Maybe` or `False`.
        2. Respond only in the provided format
    

        Text:
        {string}

        Respond in the following format:  
        Violation: <Maybe/False>
        <|assistant|>
    """

    tokenizer = AutoTokenizer.from_pretrained(MISTRAL)
    
    inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
    attention_mask = inputs["attention_mask"]

    outputs = model.generate(
            inputs.input_ids,
            attention_mask=attention_mask,
            do_sample=False,
            max_new_tokens=1000
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    violation = ""
    if "maybe" in (response.split(">")[-1]).lower():
      violation = "maybe"
    else:
      violation = "false"

    prompt = f"""
      <|system|>
      You are summariser bot that summarises articles
      <|user|>
      You are given a description of an incident, follow the provided rules:

      1. Provide a summary in 2-3 lines
      2. Do not give single lined respones

      Text:
      {string}

      Respond in the following format:  
      Summary: <summary>
      <|assistant|>
    """

    tokenizer = AutoTokenizer.from_pretrained(MISTRAL)

    inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
    attention_mask = inputs["attention_mask"]
    outputs = model.generate(
            inputs.input_ids,
            attention_mask=attention_mask,
            max_new_tokens=1000,
            do_sample=False
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    summary = response.split(">")[-1]

    data_obj = {
                "title": datum["title"],
                "date": datum["date"],
                "summary" : summary,
                "image_paths" : datum["image_paths"],
                "is_health_safety" : violation,
                "url" : datum["url"]
            }
    
    new_data.append(data_obj)

  write_json(new_data, "./scraper/data/request.json")

  # we clear articles summary data after we've formmated it
  clear("./scraper/data/articles_summary.json")

def is_data_available():
  data = read_json("./scraper/data/articles_summary.json")
  if data is not None and len(data) > 0: return True
  return False

def is_formatted_data_available():
  if read_json("./scraper/data/request.json") is not None: return True
  return False


def send_responses():
  data = read_json("./scraper/data/request.json")
  client = MongoClient("mongodb+srv://admin:iPPgoPwwcqo472xN@cf-test.gfnjq.mongodb.net/hsse-hackathon?retryWrites=true&w=majority&appName=hsse-hackathon")
  db = client["hsse-hackathon"]
  reports = db["reports"]
            # print(report)

  for data_point in data:
    now = datetime.now()

    if len(data_point["image_paths"]) > 0:
      report = {
        "publicId" : uuid.uuid4().hex[:24],
        # "title": data_point["post_id"],
        "title" : data_point["title"],
        "date": data_point["date"],
        "description": data_point["summary"],
        "metadata": {
            "imagePaths" : data_point["image_paths"]
        },
        "postUrl" : data_point["url"],
        "source" : "news",
        "createdAt": str(now),
      }

      result = reports.insert_one(report)

  # we clear request json data after we've sent it
  clear("./scraper/data/request.json")

def send_responses_2():
  data = read_json("./scraper/data/request.json")

  for data_point in data:
    url = "http://localhost:3000/api/scraper/submit"

    headers = {
      "Content-Type": "application/json",
      "x-api-key": "d3deab80460763d8cfaa9159f9f2f64ef8cfac26a650ab97a736f192f4a7e204"
    }
    
    encoded_images = []
    for image_path in data_point["image_paths"]:
      image = cv.imread(image_path)
      _, img_encoded = cv.imencode('.jpg', img=image)

      encoded_images.append(img_encoded)

    new_data_point = {
      "title": data_point["title"],
      "date": data_point["date"],
      "paragraphs": data_point["paragraphs"],
      "images" : encoded_images,
      "url" : data_point["url"]
    }

    response = requests.post(url, json=new_data_point, headers=headers)
    result = response.json()

  # we clear request json data after we've sent it
  clear("./scraper/data/request.json")