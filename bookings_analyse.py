## Uses - dominate - https://github.com/Knio/dominate
## Uses - "python-dateutil" - https://pypi.python.org/pypi/python-dateutil
## Uses - "tinydb" - https://pypi.python.org/pypi/tinydb
## Uses - "tinydb-serialization" - https://pypi.python.org/pypi/tinydb-serialization/

import dominate
from dominate.tags import *

from datetime import datetime
from dateutil.parser import parse
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

    comp_dates = list() # New list to store the datetime objects

    print('')
    for table in tables:
        if table != "_default":
            print('Table name : '+table)
            comp_date = parse(table.replace("_","")) # Parse the string date into a datetime object
            comp_dates.append(comp_date)

    comp_dates.sort() # Sort the date tables
    for comp_date in comp_dates:
        print ('Date Table : '+comp_date.strftime('%Y_%m_%dT%H_%M_%S'))
        db_table = db.table(table)
        print ('Rows : '+str(len(db_table)))
