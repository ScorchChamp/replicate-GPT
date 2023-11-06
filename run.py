import requests
import dotenv, os
import base64
import sys
from PIL import Image
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

if len(sys.argv) < 2:
    logging.error("Please provide an image path")
    exit(1)
image = sys.argv[1]
if not os.path.exists(image):
    logging.error(f"Image {image} does not exist")
    exit(1)

dotenv.load_dotenv()

def encode_image(image_path):
    logging.info(f"Encoding image {image_path}")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

api_key = os.getenv("OPENAI_API_KEY")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Make a highly detailed description of this image so someone else can replicate it."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encode_image(image)}",
                        "detail": "high",
                    }
                },
            ],
        }
    ],
    "max_tokens": 500,	
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

try:
    message = response.json()["choices"][0]["message"]["content"]
    imagePayload = {
        "model": "dall-e-3",
        "prompt": f"{message}",
        "n": 1
    }
    imageResponse = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=imagePayload).json()
    imageUrl = imageResponse["data"][0]["url"]
    imageResponse = requests.get(imageUrl)
    imageDir = os.path.dirname(image)
    imageName = os.path.basename(image)
    imageBaseName = os.path.splitext(imageName)[0]
    outputImage = os.path.join(imageDir, f"{imageBaseName}-replica.png")
    with open(outputImage, "wb") as f: f.write(imageResponse.content)
    im = Image.open(outputImage)
    im.show()

except Exception as e:
    logging.error(f"Error: {e}")