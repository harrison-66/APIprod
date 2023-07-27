import os
import requests
import configparser
import secrets
from datetime import datetime, timedelta
import base64
from cryptography.fernet import Fernet


from flask import redirect, render_template, request, session
from functools import wraps

def apology(message):
    return render_template("apology.html", message)


def osu_user_info(username):
    api_key = os.environ.get("API_KEY_OSU")
    endpoint = "https://osu.ppy.sh/api/get_user"
    params = {
        "u": username,
        "type": "string",
        "k": api_key
    }
    response = requests.post(endpoint, params = params)
    responsedata = response.json()
    return responsedata

def osu_recently_ranked():
    api_key = os.environ.get("API_KEY_OSU")
    today = datetime.utcnow().date()
    seven_days_ago = today - timedelta(days = 7)
    formatted_date = seven_days_ago.strftime('%Y-%m-%d')
    endpoint = "https://osu.ppy.sh/api/get_beatmaps"
    params = {
        "since": formatted_date,
        "m": 0,
        "limit": 50,
        "k": api_key
    }
    response = requests.post(endpoint, params = params)
    responsedata = response.json()
    return responsedata

def generate_image(prompt):
    api_key = os.environ.get("API_KEY")
    model_engine = "image-alpha-001"
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    data = """
    {
        """
    data += f'"model": "{model_engine}",'
    data += f'"prompt": "{prompt}",'
    data += """
        "num_images":1,
        "size":"1024x1024",
        "response_format":"url"
    }
    """
    response = requests.post("https://api.openai.com/v1/images/generations", headers = headers, data = data)

    responsetxt = response.json()
    print(responsetxt)
    imageurl = responsetxt['data'][0]['url']
    return imageurl

def generate_response(prompt, api_key):
    endpoint = "https://api.openai.com/v1/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "text-davinci-003",
        "prompt": prompt,
        "max_tokens": 700,
        "n": 1,
        "stop": None,
        "temperature": 0.7
    }
    response = requests.post(endpoint, headers=headers, json=data)
    response_text = response.json()["choices"][0]["text"]
    response_text = response_text.replace("\n", "")
    return response_text


def generate_text(endpoint, api_key, prompt):
    headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    }
    data = {
    'model': 'text-davinci-003',
    'prompt': prompt,
    'max_tokens': 240,
    'temperature': 0.7,
    }
    response=requests.post(endpoint, headers=headers, json=data)
    print(response)
    if response.status_code == 200:
        completions = response.json()['choices'][0]['text']
        return completions
    else:
        raise Exception('Failure to Request Data from API')

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function




def set_secret_key_for_user(username):
    # Generate a random secret key for the user
    secret_key = secrets.token_hex(16)

    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Add a section for the user to the configuration file
    config[username] = {'secret_key': secret_key}

    # Write the configuration file to disk
    with open('config.ini', 'a') as config_file:
        config.write(config_file)

def get_secret_key_for_user(username):
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config[username]['secret_key']


def encrypt(api_key, secret_key):
    api_key_bytes = api_key.encode()
    secret_key_bytes = base64.b64encode(secret_key.encode())
    fernet = Fernet(secret_key_bytes)
    encrypted_api_key = fernet.encrypt(api_key_bytes)
    return encrypted_api_key.decode()

def decrypt(encrypted_api_key, secret_key):
    encrypted_api_key_bytes = encrypted_api_key.encode()
    secret_key_bytes = base64.b64encode(secret_key.encode())
    fernet = Fernet(secret_key_bytes)
    api_key = fernet.decrypt(encrypted_api_key_bytes).decode()
    return api_key