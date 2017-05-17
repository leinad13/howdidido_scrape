## Uses - dominate - https://github.com/Knio/dominate
## Uses - "python-dateutil" - https://pypi.python.org/pypi/python-dateutil
## Uses - "tinydb" - https://pypi.python.org/pypi/tinydb
## Uses - "tinydb-serialization" - https://pypi.python.org/pypi/tinydb-serialization/


import dominate
from dominate.tags import *

from datetime import datetime
from tinydb import TinyDB, Query
from tinydb_serialization import Serializer
from tinydb_serialization import SerializationMiddleware

# Custom Serializer to store datetime object in tinydb
class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime

    def encode(self, obj):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')

    def decode(self, s):
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')

## register the custom serializer
serialization = SerializationMiddleware()
serialization.register_serializer(DateTimeSerializer(), 'TinyDateTime')

### Path to the json databases
db_path = "C:/Users/dan.cook/tmp/howdidido_scrape/hdidido/spiders"
import os
db_list = list()
### Get list of db files
for file in os.listdir(db_path):
    if file.endswith(".json"):
        db_list.append(file)

for db_name in db_list:
    db = TinyDB(db_path+'/'+db_name, storage=serialization) # Create db object
    tables = db.tables() # Get list of tables
    for table in tables:
        print('Table:'+table) # Print each table name
