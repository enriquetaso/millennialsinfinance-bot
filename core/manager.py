import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("DJANGO_USERNAME", "admin")
password = os.getenv("DJANGO_PASSWORD", "admin")
BASE_URL = os.getenv("BASE_URL", "http://localhost/finance/")


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def create_simple_entity(entity: str, name: str, action="POST") -> int:
    """Helper function for creating simple entities.

    Args:
        entity (str): The entity to create.
        name (str): The name of the entity.
        action (str): The action to perform. Defaults to "POST".
    """

    if entity.lower() == "category":
        url = f"{BASE_URL}categories/"
    elif entity.lower() == "tag":
        url = "{BASE_URL}tags/"
    else:
        raise ValueError("Entity not found")

    payload = {"name": name}
    logger.info(f"POST {url} with payload {payload}")

    response = requests.post(url, auth=(username, password), data=payload)
    return response.status_code


def create_transaction(
    date: str, description: str, amount: float, category: str, account: str, tags: list
) -> int:
    """Create a transaction."""
    url = "http://localhost/finance/transactions/"
    payload = {
        "date": "2020-01-01",
        "description": "Test transaction",
        "amount": 100,
        "category": "Test",
        "account": "Test",
        "tags": ["Test"],
    }
    logger.info(f"POST {url} with payload {payload}")
    # response = requests.post(url, auth=(username, password), data=payload)
    # return response.status_code
