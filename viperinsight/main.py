import base64
import json
import logging
import os
import tempfile
import time

import requests
from PIL import ImageGrab

# OpenAI API Key
API_KEY = os.environ.get("OPENAI_API_KEY")


def capture_screen(file_path: str = None):
    """Capture the screen."""
    if file_path:
        ImageGrab.grab().save(file_path)
        return file_path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        temp_file_path = temp_file.name
        ImageGrab.grab().save(temp_file_path)
    return temp_file_path


# Function to encode the image
def encode_image(image_path: str):
    """Encode the image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_response(prompt: str, base64_image: str):
    """Get response from OpenAI API."""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

    payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        "max_tokens": 300,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    return response.json()


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    prompt = (
        "You are good at recognizing applications from screenshots. "
        "You will notice every opened application's window edge to determine the application whether overlapped or not."
        "Based on this you can make out all opened applications and the topmost application where the cursor is "
        "focused. You only to return two lines. First line: List all opened applications according to the screenshot, "
        "separate them with comma. The second line: tell me which application is topmost where the cursor is focused"
        "Don't reply other than these two lines."
    )

    sample_path = f"datasets/sample_{int(time.time())}"
    os.makedirs(sample_path, exist_ok=True)

    # capture screen
    image_path = capture_screen(f"{sample_path}/screenshot.png")
    base64_image = encode_image(image_path)
    logging.info(f"Screenshot recorded at {image_path}")

    # get response
    response_from_openai = get_response(prompt, base64_image)

    print("-" * 30)
    print(response_from_openai)
    print("-" * 30)

    total_tokens = response_from_openai["usage"]["total_tokens"]
    print("Total Tokens: ", total_tokens)
    content = response_from_openai["choices"][0]["message"]["content"]

    print("-" * 30)
    res = content.split("\n")
    print(f"Main Opened Applications: {res[0]}")
    print(f"Cursor Focus on: {res[1]}")
    print("-" * 30)

    response = dict()
    response['openai'] = response_from_openai
    response['focus_cursor'] = res[1]
    # save response to file
    with open(f"{sample_path}/response.json", "w") as f:
        f.write(json.dumps(response, indent=4))


if __name__ == "__main__":
    main()
