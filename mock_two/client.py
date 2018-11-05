from typing import Any, Iterable, Optional, Dict, cast, Union, Tuple

from azure.cosmos.cosmos_client import CosmosClient as _CosmosClient
from azure.cosmos.errors import HTTPFailure


class Resource(dict):
    pass


class Client:
    def __init__(self, url, key):
        self._context = _CosmosClient(url, dict(masterKey=key))

    def create_database(self, id: "str", fail_if_exists=False) -> "Database":
        try:
            result = self._context.CreateDatabase(database=dict(id=id))
            return Database(self, result)
        except HTTPFailure as e:
            if fail_if_exists and e.status_code == 409:
                raise
        return self.get_database(id)

    def get_database(self, id: "str") -> "Database":
        return Database(
            client=self,
            data=self._context.ReadDatabase(database_link="dbs/{}".format(id)),
        )

    def list_databases(self) -> "Iterable[Database]":
        yield from [
            Database(self, database) for database in self._context.ReadDatabases()
        ]


class Database:
    def __init__(self, client: "Client", data):
        self.client = client
        self._context = client._context
        self.data = data
        self.id = data['id']
        self.database_link = f'/dbs/{self.id}'

    def create_collection(self, id, options=None, **kwargs) -> "Collection":
        """
        Keyword arguments:
        partitionKey, indexingPolicy, defaultTtl, conflictResolutionPolicy
        """
        definition = dict(id=id)
        definition.update(kwargs)
        data = self._context.CreateContainer(
            database_link=self.database_link, collection=definition
        )
        return Collection(self, data)

    def get_collection(self, id):
        collections = self.list_collections(
            query=dict(
                query="SELECT * FROM root r WHERE r.id = @container",
                parameters=[{"name": "@container", "value": id}],
            )
        )
        try:
            return next(collections)
        except StopIteration:
            raise ValueError()

    def list_collections(self, query=None) -> "Iterable[Collection]":
        yield from [
            Collection(self, collection)
            for collection in self._context.ReadContainers(
                database_link=self.data["_self"]
            )
        ]

    def __str__(self):
        return "Database: " + str(dict(link=self.data["_self"], name=self.data["id"]))


class Item(Resource):
    def __init__(self, collection: "Collection", data: "Dict[str, Any]"):
        self.collection = collection
        self._context = collection._context
        self.update(data)


class Collection:
    def __init__(self, database: "Database", data: "Dict[str, Any]"):
        self.database = database
        self._context = client._context
        self.data = data
        self.id = data['id']
        self.collection_link = f'{database.database_link}/colls/{self.id}'

    @staticmethod
    def document_link(item_or_link) -> "str":
        if type(item_or_link) is "str":
            return item_or_link
        else:
            return cast("str", cast("Item", item_or_link)["_self"])

    def get_item(self, id: "str", cls=Item) -> "Item":
        doc_link = f'{self.collection_link}/docs/{id}'
        result = self._context.ReadItem(document_link=doc_link)
        return cls(collection=self, data=result)

    def list_items(self, cls=Item) -> "Iterable[Item]":
        items = self._context.ReadItems(collection_link=self.data["_self"])
        yield from [cls(self, item) for item in items]

    def query_items(self, query: "str", cls=Item):
        items = self._context.QueryItems(
            database_or_Container_link=self.data["_self"], query=query
        )
        yield from [cls(self, item) for item in items]

    def replace_item(self, item: "Union[Item, str]", body: "Dict[str, Any]") -> "Item":
        item_link = Collection.document_link(item)
        data = self._context.ReplaceItem(document_link=item_link, new_document=body)
        return Item(self, data)

    def upsert_item(self, body: "Dict[str, Any]") -> "Item":
        result = self._context.UpsertItem(
            database_or_Container_link=self.data["_self"], document=body
        )
        return Item(self, result)

    def create_item(self, body: "Dict[str,str]") -> "Item":
        result = self._context.CreateItem(
            database_or_Container_link=self.data["_self"], document=body
        )
        return Item(self, result)

    def delete_item(self, item: "Item"):
        document_link = Collection.document_link(item)
        self._context.DeleteItem(document_link=document_link)


# Sample code
import os

AUTH_URL = os.environ.get("ACCOUNT_HOST")
AUTH_KEY = os.environ.get("ACCOUNT_KEY")
client = Client(url=AUTH_URL, key=AUTH_KEY)


def do_basic_stuff():
    for database in client.list_databases():
        print(database)
        for collection in database.list_collections():
            print(collection)
            for item in collection.list_items():
                print(item)


database = client.create_database("swaggers", fail_if_exists=False)
try:
    collection = database.get_collection(
        "publicmaster"
    )  # TODO: Why not have a fail_if_exists on every create?
except ValueError:  # TODO: What is the appropriate exception here?
    collection = database.create_collection("publicmaster")


def upload():
    import glob
    import json

    for file in glob.glob(
        "/users/johanste/repos/azure-rest-api-specs/specification/**/*.json",
        recursive=True,
    ):
        if not "/examples/" in file:
            with open(file, "r", encoding="UTF-8") as f:
                try:
                    data = json.load(f)
                    data["id"] = file.replace("/", ":")
                    print(f"Uploading {file}...")
                    item = collection.upsert_item(body=data)
                except (json.decoder.JSONDecodeError, UnicodeDecodeError):
                    pass


def find_stuff(query):
    items = collection.query_items(query)

    for item in items:
        print(item)
        item = collection.get_item(item['id'])
        print(item)


def clear_stuff():
    for item in collection.list_items():
        id = item.data["id"]
        if ":examples:" in id:
            print(f"deleting {id}")
            collection.delete_item(item)
        else:
            print(f"leaving {id}")


query = """
    SELECT * FROM root s
    WHERE s.info.version = '2017-01-01'
    """

find_stuff(query)
