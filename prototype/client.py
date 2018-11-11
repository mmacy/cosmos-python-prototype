"""
Cosmos client Pythonidae
"""
from typing import Any, Iterable, Optional, Dict, Union, Tuple, cast


from azure.cosmos.cosmos_client import CosmosClient as _CosmosClient
from azure.cosmos.errors import HTTPFailure


class ClientSession(_CosmosClient):
    pass


class UsersManagementMixin:
    def create_user(self, user):
        pass

    def get_user(self, id):
        pass

    def list_users(self):
        pass

    def delete_user(self):
        pass


class StoredProceduresMixin:
    def list_stored_procedures(self, query):
        pass

    def get_stored_procedure(self, id):
        pass

    def create_stored_procedure(self):
        pass

    def upsert_stored_procedure(self, trigger):
        pass

    def delete_stored_procedure(self):
        pass


class TriggersMixin:
    def list_triggers(self, query):
        pass

    def get_trigger(self, id):
        pass

    def create_trigger(self):
        pass

    def upsert_trigger(self, trigger):
        pass

    def delete_trigger(self):
        pass


class UserDefinedFunctionsMixin:
    def list_user_defined_functions(self, query):
        pass

    def get_user_defined_function(self, id):
        pass

    def create_user_defined_function(self):
        pass

    def upsert_user_defined_function(self, trigger):
        pass

    def delete_user_defined_function(self):
        pass


class ContainersManagementMixin:
    """
    Manage (create/list/query/get/delete) containers. 
    [Design note] Currently isolated into a mixin class to make it easier to move the functionality around
    in the object model. 
    """

    def create_container(
        self, id, options=None, **kwargs
    ) -> "Container":
        """
        :param str id: Id of container to create

        Keyword arguments:
        partitionKey, indexingPolicy, defaultTtl, conflictResolutionPolicy
        """
        definition = dict(id=id)
        definition.update(kwargs)
        database = cast("Database", self)
        data = database.client_session.CreateContainer(
            database_link=database.database_link,
            collection=definition,
            options=options,
        )
        return Container(
            cast("Database", self).client_session, database, data["id"]
        )

    def delete_container(self, container_or_id):
        database = cast("Database", self)
        if isinstance(container_or_id, str):
            container = Container(database, container_or_id)
        else:
            container = container_or_id
        database._context.DeleteContainer(container.collection_link)

    def get_container(self, id):
        containers = self.list_containers(
            query=dict(
                query="SELECT * FROM root r WHERE r.id = @container",
                parameters=[{"name": "@container", "value": id}],
            )
        )
        try:
            return next(containers)
        except StopIteration:
            raise ValueError()

    def list_containers(self, query=None) -> "Iterable[Container]":
        database = cast("Database", self)

        if query:
            yield from [
                Container(database.client_session, database, container["id"])
                for container in database.client_session.ReadContainers(
                    database_link=database.database_link
                )
            ]
        else:
            yield from [
                Container(database.client_session, database, container["id"])
                for container in database.client_session.ReadContainers(
                    database_link=database.database_link
                )
            ]

    def set_container_properties(
        self,
        container: "Union[str, Container]",
        *,
        partition_key=None,
        indexing_policy=None,
        default_ttl=None,
        conflict_resolution_policy=None,
    ):
        """
        Update the properties of the container. Change will be persisted immediately.
        """
        id = getattr(container, "id", container)
        parameters = {
            key: value
            for key, value in {
                "id": id,
                "partitionKey": partition_key,
                "indexingPolicy": indexing_policy,
                "defaultTtl": int(default_ttl),
                "conflictResolutionPolicy": conflict_resolution_policy,
            }.items()
            if value
            is not None  # TODO: Questionable use - should use kwargs instead. Need to figure out best documentation for kwargs...
        }
        database = cast("Database", self)
        collection_link = f"{database.database_link}/colls/{id}"
        database.client_session.ReplaceContainer(collection_link, collection=parameters)

    def get_container_properties(self, container):
        """
        Get properties for of container. TODO: implement properly
        """
        pass


class ItemsManagementMixin:
    pass


class DatabasesManagementMixin:
    def create_database(self, id: "str", fail_if_exists=False) -> "Database":
        """
        Create a new database
        :param str id: Id of the database to crate.
        :param bool fail_if_exists: If set to True and a database with the given `id` 
        already exists, fail raise a `HTTPFailure`/status code 409. If a database with
        the given id exists, and `fail_if_exists` is False, return the existing database.
        """
        try:
            client_session = cast("Client", self).client_session
            result = client_session.CreateDatabase(database=dict(id=id))
            return Database(client_session, id=result["id"], properties=result)
        except HTTPFailure as e:
            if fail_if_exists and e.status_code == 409:
                raise
        return self.get_database(id)

    def get_database(self, id: "str") -> "Database":
        """
        Return the existing database with the id `id. 
        :param str id: Id of the new database.
        """
        client_session = cast("Client", self).client_session
        properties = client_session.ReadDatabase(database_link=f"dbs/{id}")
        database = Database(client_session, id, properties)
        return database

    def get_database_properties(self, id: "str"):
        client_session = cast("Client", self).client_session
        properties = client_session.ReadDatabase(id)
        return properties

    def list_databases(self, query: "Optional[str]" = None) -> "Iterable[Database]":
        """
        Return an iterable of all existing databases.
        :param str query: Cosmos DB SQL query. If omitted, all databases will be listed.
        """
        client_session = cast("Client", self).client_session
        if query:
            yield from [
                Database(client_session, properties["id"], properties)
                for properties in client_session.QueryDatabases(query)
            ]
        else:
            yield from [
                Database(client_session, properties["id"], properties)
                for properties in client_session.ReadDatabases()
            ]

    def delete_database(self, id: "str"):
        """
        Delete the database with the given id. Raises a HTTPError if 
        the delete fails. 
        :param str id: The database to delete. 
        """
        client_session = cast("Client", self).client_session
        client_session.DeleteDatabase(database_link=f"dbs/{id}")


class Client(DatabasesManagementMixin):
    """
    CosmosDB SQL Client. This is the main entry point to the Cosmos DB object model.

    >>> import os
    >>> ACCOUNT_KEY = os.environ['ACCOUNT_KEY']
    >>> ACCOUNT_HOST = os.environ['ACCOUNT_HOST']
    >>> client = Client(url=ACCOUNT_HOST, key=ACCOUNT_KEY)
    ...
    """

    def __init__(self, url, key):
        self.client_session = ClientSession(url, dict(masterKey=key))


class Database(ContainersManagementMixin, UsersManagementMixin):
    """
    Azure Cosmos DB SQL Database
    """

    def __init__(
        self, client_session: "ClientSession", id: "str", properties: "Dict[str, Any]"
    ):
        """
        :param ClientSession client_session: Client from which this database was retreived.
        :param str id: Id of the database
        """
        self.client_session = client_session
        self.id = id
        self.properties = properties
        self.database_link = f"/dbs/{self.id}"


class Item(dict):
    def __init__(self, headers: "Dict[str, Any]", data: "Dict[str, Any]"):
        super().__init__()
        self.response_headers = headers
        self.update(data)


class Container(UserDefinedFunctionsMixin, TriggersMixin, StoredProceduresMixin):
    def __init__(
        self,
        client_session: "ClientSession",
        database: "Union[Database, str]",
        id: "str",
    ):
        self.client_session = client_session
        self.session_token = None
        self.id = id
        database_link = getattr(database, "database_link", f'dbs/{database}')
        self.collection_link = f"{database_link}/colls/{self.id}"

    @staticmethod
    def _document_link(item_or_link) -> "str":
        if isinstance(item_or_link, str):
            return item_or_link
        return cast("str", cast("Item", item_or_link)["_self"])

    def get_item(self, id: "str") -> "Item":
        """
        Get the item identified by `id`
        :param str id: Id of item to retreive
        :param callable metadata_handler: Optional method that will, if provided, receive an instance
        of `CosmosCallMetadata` representing metadata about the operation (RSU cost etc.)
        :returns: Item if present.
        """
        doc_link = f"{self.collection_link}/docs/{id}"
        result = self.client_session.ReadItem(document_link=doc_link)
        headers = self.client_session.last_response_headers
        self.session_token = headers.get("x-ms-session-token", self.session_token)
        return Item(headers=headers, data=result)

    def list_items(self, options=None) -> "Iterable[Item]":
        options = options or {}
        items = self.client_session.ReadItems(
            collection_link=self.collection_link, feed_options=options
        )
        headers = self.client_session.last_response_headers
        yield from [Item(headers=headers, data=item) for item in items]

    def query_items(
        self, query: "str", options=None, partition_key: "Optional[str]" = None
    ):
        items = self.client_session.QueryItems(
            database_or_Container_link=self.collection_link,
            query=query,
            options=options,
            partition_key=partition_key,
        )
        headers = self.client_session.last_response_headers
        yield from [Item(headers, item) for item in items]

    def replace_item(self, item: "Union[Item, str]", body: "Dict[str, Any]") -> "Item":
        item_link = Container._document_link(item)
        data = self.client_session.ReplaceItem(
            document_link=item_link, new_document=body
        )
        return Item(headers=self.client_session.last_response_headers, data=data)

    def upsert_item(self, body: "Dict[str, Any]") -> "Item":
        result = self.client_session.UpsertItem(
            database_or_Container_link=self.collection_link, document=body
        )
        return Item(headers=self.client_session.last_response_headers, data=result)

    def create_item(self, body: "Dict[str, Any]") -> "Item":
        result = self.client_session.CreateItem(
            database_or_Container_link=self.collection_link, document=body
        )
        return Item(headers=self.client_session.last_response_headers, data=result)

    def delete_item(self, item: "Item"):
        document_link = Container._document_link(item)
        self.client_session.DeleteItem(document_link=document_link)

