import os
import logging
import requests
from dotenv import load_dotenv

from core.constraints import CATEGORIES_PK, TAGS_PK, ACCOUNTS_PK


load_dotenv()

DJANGO_USERNAME = os.getenv("DJANGO_USERNAME", "admin")
PASSWORD = os.getenv("PASSWORD", "admin")
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
        url = f"{BASE_URL}tags/"
    else:
        raise ValueError("Entity not found")

    payload = {"name": name}
    response = requests.post(url, auth=(DJANGO_USERNAME, PASSWORD), data=payload)

    if response.status_code == 201:
        logger.info(f"Entity {entity} created")
    else:
        logger.error(f"Entity {entity} not created")
    return response.status_code


def create_transaction(
    date: str, amount: float, category: str, account: str, place: str, tag: str = None
) -> int:
    """Create a transaction."""
    url = f"{BASE_URL}transactions/"

    logger.info(
        f"Creating transaction with date {date}, amount {amount}, category {category}, account {account}, place {place}, tag {tag}"
    )

    account_pk = ACCOUNTS_PK.get(account, None)
    if not account_pk:
        raise ValueError("Account not found")

    category_pk = CATEGORIES_PK.get(category.lower(), None)
    if not category_pk:
        raise ValueError("Category not found")

    tag_pk = TAGS_PK.get(tag, None)

    payload = {
        "date": date,
        "description": "Operation sent by Bot",
        "place": place,
        "amount": amount,
        "category": {"name": category, "id": category_pk},
        "account": account_pk,
        "tags": [],
    }
    if tag_pk:
        payload["tags"] = [tag]

    logger.info(f"POST {url} with payload {payload}")
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        url, auth=(DJANGO_USERNAME, PASSWORD), json=payload, headers=headers
    )

    if response.status_code == 201:
        logger.info("Transaction created")
    else:
        logger.error("Transaction not created")
    return response.status_code
