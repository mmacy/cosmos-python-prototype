# Sample code
import os

from azure.cosmos import CosmosClient

AUTH_URL = os.environ.get("ACCOUNT_HOST")
AUTH_KEY = os.environ.get("ACCOUNT_KEY")
client = CosmosClient(url=AUTH_URL, key=AUTH_KEY)

def do_basic_stuff():
    for database in client.list_databases():
        print(database)
        for container in database.list_containers():
            print(container)
            for item in container.list_items():
                print(item)

database = client.create_database("swaggers", fail_if_exists=False)
try:
    container = database.get_container(
        "publicmaster"
    )  # TODO: Why not have a fail_if_exists on every create?
except ValueError:  # TODO: What is the appropriate exception here?
    container = database.create_container("publicmaster")

import time


database.set_container_properties(container, default_ttl=time.time() + 60 * 60)

def upload():
    import glob
    import json

    for file in glob.glob(
        "/users/johanste/repos/azure-rest-api-specs/specification/Compute/**/*.json",
        recursive=True,
    ):
        if not "/examples/" in file:
            with open(file, "r", encoding="UTF-8") as f:
                try:
                    data = json.load(f)
                    data["id"] = file.replace("/", ":")
                    print(f"Uploading {file}...")
                    item = container.upsert_item(body=data)
                except (json.decoder.JSONDecodeError, UnicodeDecodeError):
                    pass

def find_stuff(query):
    items = container.query_items(query)

    for item in items:
        item = container.get_item(item["id"])
        print(str(item)[0:50])

def clear_stuff():
    for item in container.list_items():
        id = item["id"]
        if ":examples:" in id:
            print(f"deleting {id}")
            container.delete_item(item)
        else:
            print(f"leaving {id}")

query = """
    SELECT * FROM root s
    WHERE s.info.version = '2018-01-01'
    """

do_basic_stuff()
upload()
clear_stuff()
find_stuff(query)
