from flask import Flask, send_file, request, abort
import mimetypes
from PIL import Image
import io

import os

app = Flask(__name__)

@app.route('/get-image', methods=['POST'])
def get_image():
    image_path = request.json.get("path")
    pil_image = Image.open(image_path)
    
    file_object = io.BytesIO()

    pil_image.save(file_object, 'PNG')
    
    file_object.seek(0)
    if not os.path.exists(image_path):
        abort(404, "Image not found")

    mime_type, _ = mimetypes.guess_type(image_path)
    return send_file(image_path, mimetype=mime_type)
   
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
   
