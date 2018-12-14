"""
Create, read, update, and delete databases, containers, and items in Azure Cosmos DB SQL API databases.
"""

__all__ = ["CosmosClient", "Database", "Container", "Item"]


from internal.cosmos.errors import HTTPFailure
from .query_iterator import QueryResultIterator

from typing import (
    Any,
    List,
    Iterable,
    Iterator,
    Optional,
    Dict,
    Union,
    Tuple,
    cast,
    overload,
    Sequence,
)

DatabaseId = Union["Database", Dict[str, Any], str]
ContainerId = Union["Container", Dict[str, Any], str]

from internal.cosmos.cosmos_client import CosmosClient as _CosmosClient
from internal.cosmos.errors import HTTPFailure


class ClientContext(_CosmosClient):
    pass


class User:
    pass


class PartitionKey(dict):
    """ Key used to partition a container into logical partitions.

    See https://docs.microsoft.com/en-us/azure/cosmos-db/partitioning-overview#choose-partitionkey for more information
    on how to choose partition keys.

    :ivar path: The path of the partition key
    :ivar kind: What kind of partition key is being defined
    """

    def __init__(self, path: "str", kind: "str" = "Hash"):
        self.path = path
        self.kind = kind

    @property
    def kind(self):
        return self["kind"]

    @kind.setter
    def kind(self, value):
        self["kind"] = value

    @property
    def path(self) -> "str":
        return self["paths"][0]

    @path.setter
    def path(self, value: "str"):
        self["paths"] = [value]


class AccessCondition(dict):
    pass


class ResponseMetadata(dict):
    pass


class CosmosClient:
    """
    Provides a client-side logical representation of an Azure Cosmos DB account.
    Use this client to configure and execute requests to the Azure Cosmos DB service.
    """

    def __init__(
        self, url: "str", key, consistency_level="Session", connection_policy=None
    ):
        """ Instantiate a new CosmosClient.


        :param url: The URL of the Cosmos DB account.
        :param consistency_level: Consistency level to use for the session.

        **Example**: Create a new client instance.

        .. code-block:: python

            import os
            ACCOUNT_KEY = os.environ['ACCOUNT_KEY']
            ACCOUNT_URI = os.environ['ACCOUNT_URI']
            client = CosmosClient(url=ACCOUNT_URI, key=ACCOUNT_KEY)

        """
        self.client_context = ClientContext(
            url,
            dict(masterKey=key),
            consistency_level=consistency_level,
            connection_policy=connection_policy,
        )

    @staticmethod
    def _get_database_link(database_or_id: DatabaseId) -> "str":
        if isinstance(database_or_id, str):
            return f"dbs/{database_or_id}"
        try:
            return cast("Database", database_or_id).database_link
        except AttributeError:
            pass

        if isinstance(database_or_id, str):
            database_id = database_or_id
        else:
            database_id = cast("Dict[str, str]", database_or_id)["id"]
        return f"dbs/{database_id}"

    def create_database(
        self,
        id: "str",
        *,
        consistency_level=None,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        access_condition: "Optional[AccessCondition]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ) -> "Database":
        """Create a new database with the given ID (name).

        :param id: ID (name) of the database to create.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :returns: A :class:`Database` instance representing the new database.
        :raises `HTTPFailure`: If `fail_if_exists` is set to True and a database with the given ID already exists.

        **Example**: Create a new database.

        .. code-block:: python

            import os
            ACCOUNT_KEY = os.environ['ACCOUNT_KEY']
            ACCOUNT_URI = os.environ['ACCOUNT_URI']
            client = CosmosClient(url=ACCOUNT_URI, key=ACCOUNT_KEY)
            database = client.create_database('nameofdatabase')

        """
        result = self.client_context.CreateDatabase(database=dict(id=id))
        return Database(self.client_context, id=result["id"], properties=result)

    def get_database(
        self,
        database: DatabaseId,
        *,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ) -> "Database":
        """
        Retrieve an existing database with the ID (name) `id`.

        :param id: ID of the new :class:`Database`.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :raise `HTTPFailure`: If the given database couldn't be retrieved.
        """
        database_link = CosmosClient._get_database_link(database)
        request_options: "Dict[str, Any]" = {}
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        properties = self.client_context.ReadDatabase(
            database_link, options=request_options
        )
        return Database(
            self.client_context,
            properties["id"],
            properties=properties,
            response_metadata=ResponseMetadata(
                self.client_context.last_response_headers
            ),
        )

    def list_databases(
        self,
        *,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        enable_cross_partition_query: "Optional[bool]" = None,
        max_degree_parallelism: "Optional[int]" = None,
        max_item_count: "Optional[int]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ) -> "Iterable[Database]":
        """
        List the databases in a Cosmos DB SQL database account.

        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        """
        request_options: "Dict[str, Any]" = {}
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if enable_cross_partition_query is not None:
            request_options["enableCrossPartitionQuery"] = enable_cross_partition_query
        if max_degree_parallelism is not None:
            request_options["maxDegreeOfParallelism"] = max_degree_parallelism
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        yield from [
            Database(self.client_context, properties["id"], properties=properties)
            for properties in self.client_context.ReadDatabases(options=request_options)
        ]

    def list_database_properties(
        self,
        query: "Optional[str]" = None,
        parameters: "Optional[str]" = None,
        *,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        enable_cross_partition_query: "Optional[bool]" = None,
        max_degree_parallelism: "Optional[int]" = None,
        max_item_count: "Optional[int]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ) -> "Iterable[Union[Dict, Any], Any]":

        request_options: "Dict[str, Any]" = {}
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if enable_cross_partition_query is not None:
            request_options["enableCrossPartitionQuery"] = enable_cross_partition_query
        if max_degree_parallelism is not None:
            request_options["maxDegreeOfParallelism"] = max_degree_parallelism
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        if query:
            # This is currently eagerly evaluated in order to capture the headers
            # from the call.
            # (just returning a generator did not initiate the first network call, so
            # the headers were misleading)
            # This needs to change for "real" implementation
            results = iter(
                list(self.client_context.QueryDatabases(query, options=request_options))
            )
        else:
            results = iter(
                list(self.client_context.ReadDatabases(options=request_options))
            )
        self.session_token = self.client_context.last_response_headers.get(
            "x-ms-session-token"
        )
        return QueryResultIterator(
            results,
            metadata=ResponseMetadata(self.client_context.last_response_headers),
        )

    def delete_database(
        self,
        database: DatabaseId,
        *,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        max_degree_parallelism: "Optional[int]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        access_condition: "Optional[AccessCondition]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ):
        """
        Delete the database with the given ID (name).

        :param database: The ID (name) or :class:`Database` instance of the database to delete.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :raise HTTPFailure: If the database couldn't be deleted.
        """

        request_options: "Dict[str, Any]" = {}
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if max_degree_parallelism is not None:
            request_options["maxDegreeOfParallelism"] = max_degree_parallelism
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        database_link = CosmosClient._get_database_link(database)
        self.client_context.DeleteDatabase(database_link, options=request_options)


class Database:
    """ Represents an Azure Cosmos DB SQL API database.

    A database contains one or more containers, each of which can contain items,
    stored procedures, triggers, and user-defined functions.

    A database also has associated users, each with a set of permissions to access various
    other containers, stored procedures, triggers, user defined functions, or items

    :ivar id: The ID (name) of the database.
    :ivar properties: A dictionary of system-generated properties for this database. See below for the list of keys.

    An Azure Cosmos DB SQL API database has the following system-generated properties; these properties are read-only:

    * `_rid`:   The resource ID.
    * `_ts`:    Specifies the last updated timestamp of the resource. The value is a timestamp.
    * `_self`:	The unique addressable URI for the resource.
    * `_etag`:	The resource etag required for optimistic concurrency control.
    * `_colls`:	The addressable path of the collections resource.
    * `_users`:	The addressable path of the users resource.
    """

    def __init__(
        self,
        client_context: "ClientContext",
        id: "str",
        *,
        properties: "Optional[Dict[str, Any]]" = None,
        response_metadata: "Optional[ResponseMetadata]" = None,
    ):
        """
        :param ClientSession client_context: Client from which this database was retrieved.
        :param str id: ID (name) of the database.
        """
        self.client_context = client_context
        self.id = id
        self.properties = properties
        self.response_metadata = response_metadata
        self.database_link = CosmosClient._get_database_link(id)

    def _get_container_link(self, container_or_id: ContainerId) -> "str":
        if isinstance(container_or_id, str):
            return f"{self.database_link}/colls/{container_or_id}"
        try:
            return cast("Container", container_or_id).collection_link
        except AttributeError:
            pass
        container_id = cast("Dict[str, str]", container_or_id)["id"]
        return f"{self.database_link}/colls/{container_id}"

    def create_container(
        self,
        id: str,
        *,
        partition_key: "Optional[PartitionKey]" = None,
        indexing_policy: "Optional[Dict[str, Any]]" = None,
        default_ttl: "int" = None,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        access_condition: "Optional[AccessCondition]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ) -> "Container":
        """
        Create a new container with the given ID (name).

        If a container with the given ID already exists, an HTTPFailure with status_code 409 is raised.

        :param id: ID of container to create.
        :param partition_key: The partition key to use for the container.
        :param indexing_policy: The indexing policy to apply to the container.
        :param default_ttl: Default TTL (time to live) for the container.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.

        :raise HTTPFailure: The container creation failed.

        **Example:** Create a container name 'mycontainer' with default settings:

        .. code-block:: python

            container = database.create_container('mycontainer')

        **Example:** Create a container named 'containerwithspecificsettings' with a custom partition key.

        .. code-block:: python

            container = database.create_container(
                id='containerwithspecificsettings',
                partition_key=PartitionKey(path='/AccountNumber')
            )

        """
        definition: "Dict[str, Any]" = dict(id=id)
        if partition_key:
            definition["partitionKey"] = partition_key
        if indexing_policy:
            definition["indexingPolicy"] = indexing_policy
        if default_ttl:
            definition["defaultTtl"] = default_ttl

        request_options: "Dict[str, Any]" = {}
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        data = self.client_context.CreateContainer(
            database_link=self.database_link,
            collection=definition,
            options=request_options,
        )
        return Container(self.client_context, self, data["id"], properties=data)

    def delete_container(
        self,
        container: ContainerId,
        *,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        max_degree_parallelism: "Optional[int]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        access_condition: "Optional[AccessCondition]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ):
        """ Delete the container

        :param container: The ID (name) of the container to delete. You can either pass in the ID of the container to delete, or :class:`Container` instance.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        """
        request_options: "Dict[str, Any]" = {}
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if max_degree_parallelism is not None:
            request_options["maxDegreeOfParallelism"] = max_degree_parallelism
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        collection_link = self._get_container_link(container)
        self.client_context.DeleteContainer(collection_link, options=request_options)

    def get_container(
        self,
        container: ContainerId,
        *,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ) -> "Container":
        """ Get the container with the ID (name) `container`.

        :param container: The ID (name) of the container, or a :class:`Container` instance.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :raise `HTTPFailure`: Raised if the container couldn't be retrieved. This includes if the container does not exist.
        :returns: :class:`Container`, if present in the container.

        .. code-block:: python

            database = client.get_database('fabrikamdb')
            try:
                container = database.get_container('customers')
            except HTTPFailure as failure:
                if failure.status_code == 404:
                    print('Container does not exist.')
                else:
                    print(f'Failed to retrieve container. Status code:{failure.status_code}')
        """
        request_options: "Dict[str, Any]" = {}
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        collection_link = self._get_container_link(container)
        container_properties = self.client_context.ReadContainer(
            collection_link, options=request_options
        )
        return Container(
            self.client_context,
            self,
            container_properties["id"],
            properties=container_properties,
        )

    def list_containers(
        self,
        *,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        max_degree_parallelism: "Optional[int]" = None,
        max_item_count: "Optional[int]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ) -> "Iterable[Container]":
        """ List the containers in this database.

        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.

        **Example**: List all containers in a database.

        .. code-block:: python

            database.list_containers()

        """
        request_options: "Dict[str, Any]" = {}
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if max_degree_parallelism is not None:
            request_options["maxDegreeOfParallelism"] = max_degree_parallelism
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        yield from [
            Container(self.client_context, self, container["id"], container)
            for container in self.client_context.ReadContainers(
                database_link=self.database_link, options=request_options
            )
        ]

    def list_container_properties(
        self,
        *,
        query: "str" = None,
        parameters: "str" = None,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        max_degree_parallelism: "Optional[int]" = None,
        max_item_count: "Optional[int]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ):
        """List properties for containers in the current database

        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.

    """
        request_options: "Dict[str, Any]" = {}
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        result = iter(
            list(
                self.client_context.QueryContainers(
                    database_link=self.database_link,
                    query=query
                    if parameters is None
                    else dict(query=query, parameters=parameters),
                    options=request_options,
                )
            )
        )

        return QueryResultIterator(
            result, metadata=ResponseMetadata(self.client_context.last_response_headers)
        )

    def set_container_properties(
        self,
        container: "Union[str, Container]",
        *,
        partition_key: "Optional[PartitionKey]" = None,
        indexing_policy=None,
        default_ttl=None,
        conflict_resolution_policy=None,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        access_condition: "Optional[AccessCondition]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ):
        """ Update the properties of the container. Property changes are persisted immediately.

        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        """
        container_id = getattr(container, "id", container)

        request_options: "Dict[str, Any]" = {}
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        parameters = {
            key: value
            for key, value in {
                "id": container_id,
                "partitionKey": partition_key,
                "indexingPolicy": indexing_policy,
                "defaultTtl": int(default_ttl),
                "conflictResolutionPolicy": conflict_resolution_policy,
            }.items()
            if value is not None
        }
        collection_link = f"{self.database_link}/colls/{container_id}"
        self.client_context.ReplaceContainer(
            collection_link, collection=parameters, options=request_options
        )

    def get_user_link(self, id_or_user: "Union[User, str]") -> "str":
        user_link = getattr(
            id_or_user, "user_link", f"{self.database_link}/users/{id_or_user}"
        )
        return user_link

    def create_user(self, user, options=None):
        """ Create a new user in the database.

        :param user: A dict-like object with an `id` key and value.

        The user ID must be unique within the database, and consist of no more than 255 characters.

        .. code-block:: python

            database.create_user(dict(
                id='Walter Harp'
                ))

        """
        database = cast("Database", self)
        return database.client_context.CreateUser(database.database_link, user, options)

    def get_user(self, id):
        """ Get the specified user from the database.

        :param id: The ID of the user to retrieve.
        """
        database = cast("Database", self)
        return database.client_context.ReadUser(self.get_user_link(id))

    def list_users(self):
        """ Get all database users.
        """
        database = cast("Database", self)
        yield from [User(user) for user in database.client_context.ReadUsers()]

    def list_user_properties(self, query: "str" = None, parameters=None):
        pass

    def delete_user(self, user):
        """ Delete the specified user from the database.
        """
        database = cast("Database", self)
        database.client_context.DeleteUser(self.get_user_link(user))


class Item(dict):
    """ Represents a document in an Azure Cosmos DB SQL API container.

    To create, read, update, and delete Items, use the associated methods on the :class:`Container`.
    """

    def __init__(self, headers: "Dict[str, Any]", data: "Dict[str, Any]"):
        super().__init__()
        self.response_headers = headers
        self.update(data)


class Container:
    """ An Azure Cosmos DB container.

    A container in an Azure Cosmos DB SQL API database is a collection of documents, each of which represented as an :class:`Item`.

    :ivar str id: ID (name) of the container
    :ivar str session_token: The session token for the container.
    """

    def __init__(
        self,
        client_context: "ClientContext",
        database: "Union[Database, str]",
        id: "str",
        properties: "Optional[Dict[str, Any]]" = None,
    ):
        self.client_context = client_context
        self.session_token = None
        self.id = id
        self.properties = properties
        database_link = CosmosClient._get_database_link(database)
        self.collection_link = f"{database_link}/colls/{self.id}"

    def _get_document_link(
        self, item_or_link: "Union[str, Dict[str, Any], Item]"
    ) -> "str":
        if isinstance(item_or_link, str):
            return f"{self.collection_link}/docs/{item_or_link}"
        return cast("str", cast("Item", item_or_link)["_self"])

    def get_item(
        self,
        id: "str",
        *,
        partition_key: "Optional[str]" = None,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ) -> "Item":
        """
        Get the item identified by `id`.

        :param id: ID of item to retrieve.
        :param partition_key: Partition key for the item to retrieve.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :returns: :class:`Item`, if present in the container.
        """
        doc_link = self._get_document_link(id)

        request_options: "Dict[str, Any]" = {}
        if partition_key:
            request_options["partitionKey"] = partition_key
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        result = self.client_context.ReadItem(
            document_link=doc_link, options=request_options
        )
        headers = self.client_context.last_response_headers
        self.session_token = headers.get("x-ms-session-token", self.session_token)
        return Item(headers=headers, data=result)

    def list_items(
        self,
        *,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        enable_cross_partition_query: "Optional[bool]" = None,
        max_degree_parallelism: "Optional[int]" = None,
        max_item_count: "Optional[int]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ) -> "Iterable[Item]":
        """ List all items in the container.

        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param enable_cross_partition_query: Allow scan on the queries which couldn't be served as indexing was opted out on the requested paths.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        """
        request_options: "Dict[str, Any]" = {}
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if enable_cross_partition_query is not None:
            request_options["enableCrossPartitionQuery"] = enable_cross_partition_query
        if max_degree_parallelism is not None:
            request_options["maxDegreeOfParallelism"] = max_degree_parallelism
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        items = self.client_context.ReadItems(
            collection_link=self.collection_link, feed_options=request_options
        )
        headers = self.client_context.last_response_headers
        yield from [Item(headers=headers, data=item) for item in items]

    def query_items_change_feed(self, options=None):
        """ Get a sorted list of items that were changed, in the order in which they were modified.
        """
        items = self.client_context.QueryItemsChangeFeed(
            self.collection_link, options=options
        )
        headers = self.client_context.last_response_headers
        yield from [Item(headers, item) for item in items]

    def query_items(
        self,
        query: "str",
        parameters: "Optional[List]" = None,
        *,
        partition_key: "Optional[str]" = None,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        enable_cross_partition_query: "Optional[bool]" = None,
        max_degree_parallelism: "Optional[int]" = None,
        max_item_count: "Optional[int]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ) -> "QueryResultIterator":
        """Return all results matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param partition_key: Specifies the partition key value for the item.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param enable_cross_partition_query: Allow scan on the queries which couldn't be served as indexing was opted out on the requested paths.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :returns: An `Iterator` containing each result returned by the query, if any.

        **Example:** Find all families in the state of NY.

        .. code-block:: python

            items = container.query_items(
                query='SELECT * FROM Families f WHERE f.address.state = "NY"'
            )

        **Example:** Parameterized query to find all families in the state of NY.

        .. code-block:: python

            items = container.query_items(
                query='SELECT * FROM Families f WHERE f.address.state = @addressState',
                parameters=[
                    dict(name='@addressState', value='NY')
                ]
            )

        """
        request_options: "Dict[str, Any]" = {}
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if enable_cross_partition_query is not None:
            request_options["enableCrossPartitionQuery"] = enable_cross_partition_query
        if max_degree_parallelism is not None:
            request_options["maxDegreeOfParallelism"] = max_degree_parallelism
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        items = self.client_context.QueryItems(
            database_or_Container_link=self.collection_link,
            query=query
            if parameters is None
            else dict(query=query, parameters=parameters),
            options=request_options,
            partition_key=partition_key,
        )
        headers = self.client_context.last_response_headers
        self.session_token = headers["x-ms-session-token"]
        items_iterator = iter(items)
        return QueryResultIterator(items_iterator, metadata=ResponseMetadata(headers))

    def replace_item(
        self,
        item: "Union[Item, str]",
        body: "Dict[str, Any]",
        *,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        access_condition: "Optional[AccessCondition]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ) -> "Item":
        """ Replaces the specified item if it exists in the container.

        :param body: A dict-like object or string representing the item to replace.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :raises `HTTPFailure`:
        """
        item_link = self._get_document_link(item)
        request_options: "Dict[str, Any]" = {}
        request_options["disableIdGeneration"] = True
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics
        data = self.client_context.ReplaceItem(
            document_link=item_link, new_document=body, options=request_options
        )
        return Item(headers=self.client_context.last_response_headers, data=data)

    def upsert_item(
        self,
        body: "Dict[str, Any]",
        *,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        access_condition: "Optional[AccessCondition]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ) -> "Item":
        """ Insert or update the specified item.

        :param body: A dict-like object or string representing the item to update or insert.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :raises `HTTPFailure`:

        If the item already exists in the container, it is replaced. If it does not, it is inserted.
        """
        request_options: "Dict[str, Any]" = {}
        request_options["disableIdGeneration"] = True
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        result = self.client_context.UpsertItem(
            database_or_Container_link=self.collection_link, document=body
        )
        return Item(headers=self.client_context.last_response_headers, data=result)

    def create_item(
        self,
        body: "Dict[str, Any]",
        *,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        access_condition: "Optional[AccessCondition]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ) -> "Item":
        """ Create an item in the container.

        :param body: A dict-like object or string representing the item to create.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :returns: The :class:`Item` inserted into the container.
        :raises `HTTPFailure`:

        To update or replace an existing item, use the :func:`Container.upsert_item` method.

        """
        request_options: "Dict[str, Any]" = {}
        request_options["disableIdGeneration"] = True
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        result = self.client_context.CreateItem(
            database_or_Container_link=self.collection_link,
            document=body,
            options=request_options,
        )
        return Item(headers=self.client_context.last_response_headers, data=result)

    def delete_item(
        self,
        item: "Union[Item, Dict[str, Any], str]",
        *,
        partition_key: "Optional[str]" = None,
        disable_ru_per_minute_usage: "Optional[bool]" = None,
        max_degree_parallelism: "Optional[int]" = None,
        session_token: "Optional[str]" = None,
        initial_headers: "Optional[Dict[str, Any]]" = None,
        access_condition: "Optional[AccessCondition]" = None,
        populate_query_metrics: "Optional[bool]" = None,
    ) -> "None":
        """ Delete the specified item from the container.

        :param item: The :class:`Item` to delete from the container.
        :param partition_key: Specifies the partition key value for the item.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :raises `HTTPFailure`: The item wasn't deleted successfully. If the item does not exist in the container, a `404` error is returned.

        """
        request_options: "Dict[str, Any]" = {}
        if partition_key:
            request_options["partitionKey"] = partition_key
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if max_degree_parallelism is not None:
            request_options["maxDegreeOfParallelism"] = max_degree_parallelism
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        document_link = self._get_document_link(item)
        self.client_context.DeleteItem(
            document_link=document_link, options=request_options or None
        )

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
