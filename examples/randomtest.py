# Sample code
import os

from azure.cosmos import CosmosClient, HTTPFailure, PartitionKey

AUTH_URI = os.environ["ACCOUNT_URI"]
AUTH_KEY = os.environ["ACCOUNT_KEY"]
client = CosmosClient(url=AUTH_URI, key=AUTH_KEY)

def do_basic_stuff():
    for database in client.list_databases():
        print(database)
        for container in database.list_containers():
            print(container)
            for item in container.list_items():
                print(item)

try:
    database = client.create_database("swaggers")
except HTTPFailure:
    database = client.get_database("swaggers")

try:
    database.delete_container('publicmaster')
except:
    pass
    
try:
    container = database.get_container(
        "publicmaster"
    )  # TODO: Why not have a fail_if_exists on every create?
except HTTPFailure:  # TODO: What is the appropriate exception here?
    container = database.create_container("publicmaster", partition_key=PartitionKey('/info/version'))

import time

database.reset_container_properties(container, partition_key=PartitionKey('/info/version'), default_ttl=time.time() + 60 * 60)

try:
    database.delete_container('containerwithspecificsettings')
except HTTPFailure:
    pass

container = database.create_container(
    id='containerwithspecificsettings',
    partition_key={
        "paths": [
        "/info/version"
        ],
        "kind": "Hash"
    }
)

print(container)

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
    items = container.query_items(query, enable_cross_partition_query=True)

    for item in items:
        item = container.get_item(item["id"], partition_key=item['info']['version'])
        print(str(item)[0:50])

def clear_stuff(query):
    for item in container.query_items(query):
        print(f"deleting {item['id']}")
        container.delete_item(item, partition_key=item['info']['version'])

query = """
    SELECT * FROM root s
    WHERE s.info.version = '2018-06-01'
    """

do_basic_stuff()
upload()
clear_stuff(query)
find_stuff(query)


