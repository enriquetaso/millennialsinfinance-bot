import os
import json
import logging
import requests
from dotenv import load_dotenv, find_dotenv

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def set_categories_env_variable():
    load_dotenv(find_dotenv())  # load .env file
    
    DJANGO_USERNAME = os.getenv("DJANGO_USERNAME", "admin")
    PASSWORD = os.getenv("PASSWORD", "admin")
    BASE_URL = os.getenv("BASE_URL", "http://localhost/finance/")
    
    url = f"{BASE_URL}categories/"

    # Send GET request
    response = requests.get(url, auth=(DJANGO_USERNAME, PASSWORD))

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"GET /categories/ {response.status_code}")

    # Get the categories from the response
    categories = response.json()

    # Formatting the result into a dictionary
    categories_dict = {category['name']: category['id'] for category in categories}

    # Converting the dictionary to a JSON string
    categories_json_str = json.dumps(categories_dict)

    # Setting the environment variable
    os.environ['CATEGORIES_PK'] = categories_json_str

    # Update .env file
    with open(find_dotenv(), 'a') as f:
        f.write(f'\nCATEGORIES_PK={categories_json_str}\n')
    
    logger.debug(f"Environment variable CATEGORIES_PK set to {categories_json_str}")

    # check if the environment variable was set correctly
    CATEGORIES_TEST = json.loads(os.getenv('CATEGORIES_PK'))
    
    reply_keyboard = []
    aux = []
    c = 0
    for category in CATEGORIES_TEST.keys():
        if c == 5:
            reply_keyboard.append(aux)
            aux = []
            c = 0
        aux.append(category)
        c += 1
    reply_keyboard.append(aux)
    print(reply_keyboard)


    if CATEGORIES_TEST == categories_dict:
        logger.info("Environment variable CATEGORIES_PK set correctly")
    else:
        logger.error("Environment variable CATEGORIES_PK not set correctly")


if __name__ == "__main__":
    set_categories_env_variable()