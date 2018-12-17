# Azure Cosmos DB SQL API SDK for Python

Azure Cosmos DB is a multi-model database service that supports document, key-value, wide-column, and graph databases. Several APIs are supported, including SQL, MongoDB, Gremlin, Cassandra, and Azure Table.

The Azure Cosmos DB SQL API SDK for Python enables you to manage database resources like containers (collections of JSON documents) and items (JSON documents), as well as query the documents in your database using familiar SQL-like syntax.

## Prerequisites

### Required

* Azure subscription - [Create a free account][azure_sub]
* Azure [Cosmos DB account][cosmos_account] - SQL API
* [Python 3.6+][python]

## Installation

The installation of the Azure Cosmos DB Python SDK involves installing packages via [pip][pip], optionally within a virtual environment via [venv][venv].

### Configure a virtual environment (optional)

Although not required, we recommend that you install the SDK within a Python virtual environment. By using a virtual environment, you can keep your your base system and Azure SDK environments isolated.

Execute the following commands to configure and then enter a virtual environment with [venv][venv]:

```Bash
python3 -m venv azure-cosmosdb-sdk-environment
source azure-cosmosdb-sdk-environment/bin/activate
```

### Install the SDK

Install the Azure Cosmos DB SDK for Python with [pip][pip]:

```Bash
pip install git+https://github.com/johanste/azure-cosmos-python.git@ux git+https://github.com/binderjoe/cosmos-python-prototype.git@master
```

## Authentication

Interaction with Cosmos DB starts with an instance of the [CosmosClient][ref_cosmosclient] class. To create the [CosmosClient][ref_cosmosclient] object, supply your Cosmos DB account's URI and one of its account keys to the [CosmosClient][ref_cosmosclient] constructor.

### Create Cosmos DB account

If you need a Cosmos DB SQL API account, you can create one in the [Azure portal][cosmos_account_create], or with the following Azure CLI command.

```Bash
az cosmosdb create --resource-group <resource-group-name> --name <cosmos-account-name>
```

### Get credentials

You can get your account URI and account key in several ways, including with the [Azure CLI][azure_cli] and [Azure portal][azure_portal]. The Bash snippet below retrieves the account URI and its primary master key with the Azure CLI, and exports those values as environment variables.

```Bash
RES_GROUP=<resource-group-name>
ACCT_NAME=<cosmos-db-account-name>

export ACCOUNT_URI=$(az cosmosdb show --resource-group $RES_GROUP --name $ACCT_NAME --query documentEndpoint --output tsv)
export ACCOUNT_KEY=$(az cosmosdb list-keys --resource-group $RES_GROUP --name $ACCT_NAME --query primaryMasterKey --output tsv)
```

### Create client

Once you've populated the `ACCOUNT_URI` and `ACCOUNT_KEY` environment variables, you can create the [CosmosClient][ref_cosmosclient].

```Python
from azure.cosmos import HTTPFailure, CosmosClient, Container, Database

import os
url = os.environ['ACCOUNT_URI']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, key)
```

## Usage

Once you've initialized a [CosmosClient][ref_cosmosclient], you can interact with the primary resource types in Cosmos DB:

* [Database][cosmos_database]: Each Cosmos DB account contains one or more databases. When you create the database, you specify the API you'd like to use when interacting with it: SQL, MongoDB, Gremlin, Cassandra, or Azure Table.
* [Container][cosmos_container]: Each database in a Cosmos DB SQL API account houses one or more *containers*. A container is a collection of JSON documents (items), and is labeled a "Collection" in the Azure portal.
* [Item][cosmos_item]: Containers hold one or more *items*. Items are the JSON documents in your containers, and labeled "Documents" in the Azure portal.

For more information on these resources, see [Working with Azure Cosmos databases, containers and items][cosmos_resources].

## Examples

The following sections provide several example code snippets covering some of the most common Cosmos DB tasks, including:

* [Create a database](#create-a-database)
* [Create a container](#create-a-container)
* [Get an existing container](#get-an-existing-container)
* [Insert data](#insert-data)
* [Query the database](#query-the-database)
* [Get database properties](#get-database-properties)
* [Modify container properties](#modify-container-properties)

### Create a database

After authenticating your [CosmosClient][ref_cosmosclient], you can work with any resource in the account. The code snippet below creates a SQL API database, which is the default when no API is specified when [create_database][ref_cosmosclient_create_database] is invoked.

```Python
database_name = 'testDatabase'
database = client.create_database(id=database_name, fail_if_exists=False)
```

### Create a container

This example creates a container with default settings. If a container with the same name already exists in the database (generating a `409 Conflict` error), the existing container is obtained instead.

```Python
container_name = 'products'
try:
    container = database.create_container(id=container_name)
except HTTPFailure as e:
    if e.status_code != 409:
        raise
    container = database.get_container(container_name)
```

The preceding snippet also handles the [HTTPFailure][ref_httpfailure] exception if the container creation failed. For more information on error handling and troubleshooting, see the [Troubleshooting](#troubleshooting) section.

### Get an existing container

Retrieve an existing container from the database:

```Python
database = client.get_database(database_name)
container = database.get_container(container_name)
```

### Insert data

To insert items into a container, pass a dictionary containing your data to [Container.upsert_item][ref_container_upsert_item].

This example inserts several items into the container, each with a unique ID. If you don't include an `id` field in the items you insert, Cosmos DB generates an ID for you in the form of a GUID.

```Python
database = client.get_database(database_name)
container = database.get_container(container_name)

for i in range(1, 10):
    container.upsert_item(dict(
        id=f'item{i}',
        productName='Widget',
        productModel=f'Model {i}'
        )
    )
```

### Delete data

To delete items from a container, use [Container.delete_item][ref_container_delete_item]. The SQL API in Cosmos DB does not support the SQL `DELETE` statement.

```Python
for item in container.query_items(query='SELECT * FROM products p WHERE p.productModel = "DISCONTINUED"'):
    container.delete_item(item)
```

### Query the database

A Cosmos DB SQL API database supports querying the items in a container with [Container.query_items][ref_container_query_items] using SQL-like syntax.

This example queries a container for items with a specific `id`:

```Python
database = client.get_database(database_name)
container = database.get_container(container_name)

# Enumerate the returned items
import json
for item in container.query_items(query='SELECT * FROM mycontainer r WHERE r.id="something"'):
    print(json.dumps(item, indent=True))
```

> NOTE: Although you can specify any value for the container name in the `FROM` clause, we recommend you use the container name for consistency.

Perform parameterized queries by passing a dictionary containing the parameters and their values to [Container.query_items][ref_container_query_items]:

```Python
discontinued_items = container.query_items(
    query='SELECT * FROM products p WHERE p.productModel = @model',
    parameters=[
        dict(name='@model', value='DISCONTINUED')
    ]
)
for item in discontinued_items:
    print(json.dumps(item, indent=True))
```

For more information on querying Cosmos DB databases using the SQL API, see [Query Azure Cosmos DB data with SQL queries][cosmos_sql_queries].

### Get database properties

Get and display the properties of a database:

```Python
database = client.get_database(database_name)
properties = database.properties
print(json.dumps(properties))
```

### Modify container properties

Certain properties of an existing container can be modified. This example sets the default time to live (TTL) for items in the container to 10 seconds:

```Python
database = client.get_database(database_name)
container = database.get_container(container_name)
database.set_container_properties(container, default_ttl=10)

# Display the new TTL setting for the container
container_props = database.get_container(container_name).properties
print(json.dumps(container_props['defaultTtl']))
```

For more information on TTL, see [Time to Live for Azure Cosmos DB data][cosmos_ttl].

## Troubleshooting

### General

When you interact with Cosmos DB using the Python SDK, errors returned by the service correspond to the same HTTP status codes returned for REST API requests:

[HTTP Status Codes for Azure Cosmos DB][cosmos_http_status_codes]

For example, if you try to create a container using an ID (name) that's already in use in your Cosmos DB database, a `409` error is returned, indicating the conflict. In the following snippet, the error is handled gracefully by catching the exception and displaying additional information about the error.

```Python
try:
    database.create_container(id=container_name)
except HTTPFailure as e:
    if e.status_code == 409:
        print("""Error creating container.
HTTP status code 409: The ID (name) provided for the container is already in use.
The container name must be unique within the database.""")
    else:
        raise
```

### Handle transient errors with retries

While working with Cosmos DB, you might encounter transient failures caused by [rate limits][cosmos_request_units] enforced by the service, or other transient problems like network outages. For information about handling these types of failures, see [Retry pattern][azure_pattern_retry] in the Cloud Design Patterns guide, and the related [Circuit Breaker pattern][azure_pattern_circuit_breaker].

## Next steps

### More sample code

Several Cosmos DB Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Cosmos DB:

* [`examples.py`][sample_examples_misc] - Contains the code snippets found in this article.
* [`databasemanagementsample.py`][sample_database_mgmt] - Python code for working with Azure Cosmos DB databases, including:
  * Create database
  * Get database by ID
  * Get database by query
  * List databases in account
  * Delete database
* [`documentmanagementsample.py`][sample_document_mgmt] - Example code for working with Cosmos DB documents, including:
  * Create container
  * Create documents (including those with differing schemas)
  * Get document by ID
  * Get all documents in a container

### Additional documentation

For more extensive documentation on the Cosmos DB service, see the [Azure Cosmos DB documentation][cosmos_docs] on docs.microsoft.com.

<!-- LINKS -->
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_portal]: https://portal.azure.com
[azure_pattern_circuit_breaker]: https://docs.microsoft.com/azure/architecture/patterns/circuit-breaker
[azure_pattern_retry]: https://docs.microsoft.com/azure/architecture/patterns/retry
[azure_sub]: https://azure.microsoft.com/free/
[cloud_shell]: https://docs.microsoft.com/azure/cloud-shell/overview
[cosmos_account]: https://docs.microsoft.com/azure/cosmos-db/account-overview
[cosmos_account_create]: https://docs.microsoft.com/azure/cosmos-db/how-to-manage-database-account
[cosmos_container]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-containers
[cosmos_database]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-databases
[cosmos_docs]: https://docs.microsoft.com/azure/cosmos-db/
[cosmos_http_status_codes]: https://docs.microsoft.com/rest/api/cosmos-db/http-status-codes-for-cosmosdb
[cosmos_item]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-items
[cosmos_resources]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items
[cosmos_request_units]: https://docs.microsoft.com/azure/cosmos-db/request-units
[cosmos_sql_queries]: https://docs.microsoft.com/azure/cosmos-db/how-to-sql-query
[cosmos_ttl]: https://docs.microsoft.com/azure/cosmos-db/time-to-live
[pip]: https://pypi.org/project/pip/
[python]: https://www.python.org/downloads/
[ref_container_upsert_item]: http://cosmosproto.westus.azurecontainer.io/#azure.cosmos.Container.upsert_item
[ref_cosmosclient]: http://cosmosproto.westus.azurecontainer.io/#azure.cosmos.CosmosClient
[ref_cosmosclient_create_database]: http://cosmosproto.westus.azurecontainer.io/#azure.cosmos.CosmosClient.create_database
[ref_httpfailure]: https://docs.microsoft.com/python/api/azure-cosmos/azure.cosmos.errors.httpfailure
[ref_container_query_items]: http://cosmosproto.westus.azurecontainer.io/#azure.cosmos.Container.query_items
[venv]: https://docs.python.org/3/library/venv.html
[virtualenv]: https://virtualenv.pypa.io
[sample_examples_misc]: https://github.com/binderjoe/cosmos-python-prototype/blob/master/examples/examples.py
[sample_database_mgmt]: https://github.com/binderjoe/cosmos-python-prototype/blob/master/examples/databasemanagementsample.py
[sample_document_mgmt]: https://github.com/binderjoe/cosmos-python-prototype/blob/master/examples/documentmanagementsample.py
