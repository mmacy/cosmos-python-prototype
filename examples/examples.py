from azure.cosmos import HTTPFailure, CosmosClient, Container

# It all starts with a client instance:
import os
url = os.environ['ACCOUNT_HOST']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, key)

test_database_name = 'testDatabase'
test_container_name = 'testContainer'
#### Create environnment ###
db = client.create_database(id=test_database_name, fail_if_exists=False)
try:
    db.create_container(id=test_container_name)
except HTTPFailure as e:
    if e.status_code != 409:
        raise
    db.get_container(test_container_name)

####

# In order to retreive a container where you know the database name and container name:
container = Container(client.client_context, database=test_database_name, id=test_container_name)
container.upsert_item({
    'id': 'something',
    'value': 'else'
})

# If you want to walk down the hierarchy, you can also get it from the client->databases->containers
database = client.get_database(test_database_name)
container = database.get_container(test_container_name)
container.upsert_item({
    'id': 'something',
    'value': 'new'
})

# Once you have a container, you can query items to your heart's content:
items = list(container.query_items(query='SELECT * FROM root r WHERE r.id="something"'))

# You can enumerate the items:
import json
for item in items:
    print(json.dumps(item, indent=True))

# It should be (almost) free to ask the length of a query
# if len(items) > 4711: # TODO: NYI (should use header to get this info to make it O(1))
#    print('Big number')

# If you want to create things, you can just go ahead and create some dicts
for i in range(1, 10):
    container.upsert_item(dict(
        id=f'item{i}',
        firstName='David',
        lastName='Smith'
        )
    )

database.set_container_properties(container, default_ttl=10)
container = database.get_container(container)
print(container)
# You can also modify one of the existing items
item = items[0]
item['firstName'] = 'Some Other Name'
updated_item = container.upsert_item(item) # ISSUE: do we update the item "in place" for system properties and  headers?

# If you need to get the properties of a database, they are all there...
properties = database.properties
print(json.dumps(properties))

