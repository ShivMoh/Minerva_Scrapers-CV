import json
import os
import requests

def read_json(path):
  data = None
  try:
    with open(path, "r") as file:
        data = json.load(file)
  except:
     print("Reading did not work")

  return data

def write_json(data, path):
  try:
    with open(path, "w") as file:
      json.dump(data, file, indent=4)
  except:
     print("Writing did not work")

def clear(path):
  os.remove(path=path)

def send_posts():
    url = "https://minerva-drab.vercel.app/api/reports/submit"
    api_key = "d3deab80460763d8cfaa9159f9f2f64ef8cfac26a650ab97a736f192f4a7e204"
    data = read_json("./data/test.json")

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


send_posts()