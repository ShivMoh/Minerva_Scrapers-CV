from flask import Flask, send_file, request, abort, jsonify
import os
import mimetypes
from ultralytics import YOLO
from ultralytics import YOLO
import cv2 as cv
import numpy as np
from flask_cors import CORS
from PIL import Image
import io

app = Flask(__name__)
CORS(app) 

## Adds to existing dataset
## At currrent, does not support separating new data from already used data
## Everything is just kinda dumped into one pile
## The ability to extend classes also currently does not exist so the model can only get better
## At recongizing classes it already has in its dataset
@app.route('/add-to-train-set', methods=['POST'])
def add_to_train_set():

    image_file = request.files.get('image')
    label_file = request.files.get('label')

    image_path = os.path.join("./train/images", image_file.filename)
    image_file.save(image_path)

    label_path = os.path.join("./train/labels", label_file.filename)
    label_file.save(label_path)

    return jsonify({"message": "Image and label successfully added to training set."}), 200

## Updates the model using the data
@app.route("/initiate-update", methods=['GET'])
def initiate_update():
    model = YOLO("yolov8n.pt")
    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/data.yaml")
    model.train(data=full_path, epochs=30, imgsz=997)
    return jsonify({"message" : "The model is updating. The last version will continue to be used until update is finished"})

## Simply gets the number for the latest training iteration
@app.route("/get_latest_version", methods=['GET'])
def get_latest_version():
    directories = os.listdir("./runs/detect")
    return len(directories) - 1

# does not currently work
# can be achieved using upload + inference
# i do not have the mental capacity rn to make this work
# brain cells are slowly evaporating
@app.route("/inference", methods=["POST"])
def inference():
    image_file = request.files.get('image')
    nparr = np.fromstring(image_file, np.uint8)
    input_image = cv.imdecode(nparr, cv.IMREAD_COLOR)
    model = YOLO(f"./runs/detect/train{get_latest_version()}/weights/best.pt")
    
    # Run prediction
    results = model(input_image)

    names = {
        0: "Hardhat",
        1: "Mask",
        2: "NO-Hardhat",
        3: "NO-Mask",
        4: "NO-Safety Vest",
        5: "Person",
        6: "Safety Cone",
        7: "Safety Vest",
        8: "machinery",
        9: "vehicle"
    }

    for result in results:
        boxes = result.boxes.xywh  # center-x, center-y, width, height
        classes = result.boxes.cls  # predicted class indices
        confidences = result.boxes.conf  # confidence scores (optional)

        for i, (box, cls_id, conf) in enumerate(zip(boxes, classes, confidences)):
            x, y, w, h = box[0].item(), box[1].item(), box[2].item(), box[3].item()
            
            top_left = (int(x - w / 2), int(y - h / 2))
            bottom_right = (int(x + w / 2), int(y + h / 2))

            class_id = int(cls_id.item())
            class_name = model.names[class_id]
            label = f"{class_name} {conf.item():.2f}"

            cv.rectangle(input_image, top_left, bottom_right, (0, 255, 0), 2)

            label_size, _ = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            label_top_left = (top_left[0], top_left[1] - 10)
            label_bottom_right = (top_left[0] + label_size[0], top_left[1])
            cv.rectangle(input_image, label_top_left, label_bottom_right, (0, 255, 0), -1)

            cv.putText(input_image, label, (top_left[0], top_left[1] - 2), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    return send_file(input_image)


## Upload a file for inference
@app.route("/upload", methods=["POST"])
def upload():

    file = request.files['file']
   
    filename = file.filename

    if not os.path.exists("./inference"):
        os.makedirs("./inference")
    save_path = os.path.join("./inference", filename)
    file.save(save_path)

    return {
        "success" : True
    }
    
## Returns an annotated image using the latest model
@app.route("/annotate_image", methods=["POST"])
def annotate_image():

    image_path = request.json.get("path")
    full_path = os.path.join("inference", image_path)
    if not os.path.exists(full_path): 
        return {
            "error" : "path does not exist"
        }

    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), full_path)
    input_image = cv.imread(full_path)
   
    if input_image is None:
        return {
            "error" : "An error occurred when reading the image"
        }

    model = YOLO(f"./runs/detect/train{get_latest_version()}/weights/best.pt")
    
    results = model(full_path)

    names = {
        0: "Hardhat",
        1: "Mask",
        2: "NO-Hardhat",
        3: "NO-Mask",
        4: "NO-Safety Vest",
        5: "Person",
        6: "Safety Cone",
        7: "Safety Vest",
        8: "machinery",
        9: "vehicle"
    }

    for result in results:
        boxes = result.boxes.xywh  # center-x, center-y, width, height
        classes = result.boxes.cls  # predicted class indices
        confidences = result.boxes.conf  # confidence scores (optional)
        print("here")
        for i, (box, cls_id, conf) in enumerate(zip(boxes, classes, confidences)):
            x, y, w, h = box[0].item(), box[1].item(), box[2].item(), box[3].item()
            
            top_left = (int(x - w / 2), int(y - h / 2))
            bottom_right = (int(x + w / 2), int(y + h / 2))

            class_id = int(cls_id.item())
            class_name = model.names[class_id]
            label = f"{class_name} {conf.item():.2f}"

            cv.rectangle(input_image, top_left, bottom_right, (0, 255, 0), 2)

            label_size, _ = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            label_top_left = (top_left[0], top_left[1] - 10)
            label_bottom_right = (top_left[0] + label_size[0], top_left[1])
            cv.rectangle(input_image, label_top_left, label_bottom_right, (0, 255, 0), -1)

            cv.putText(input_image, label, (top_left[0], top_left[1] - 2), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    cv.imwrite("output_new.jpg", input_image)
    image = cv.cvtColor(input_image, cv.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image)
    
    file_object = io.BytesIO()

    pil_image.save(file_object, 'PNG')
    
    file_object.seek(0)
    # cv.imwrite("./annotated.jpg", input_image)
    return send_file(file_object,  mimetype="image/PNG")



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)