import json
import datetime
import pytz
import os
import logging
import datetime
import sys
import mysql.connector
import glob

config_path = '/home/ubuntu/iCycleWays/config/'
# config_path = './config/'
sys.path.append(config_path)
import config

db_name = config.db_name
db_user = config.db_user
db_password = config.db_password
db_host = config.db_host
CSV_PATH = config.csv_path
API_URL = config.api_url
LOG_PATH = config.log_path
META_PATH = config.meta_path
FULL_METADATA = f'{META_PATH}/cycle_lines_metadata_v.2.2.json'

# Get a NZT timezone 
nzt_tz = pytz.timezone('Pacific/Auckland')
time_utc = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
time_utc_str = datetime.datetime.strptime(time_utc, '%Y-%m-%d %H:%M:%S')
time_NZT = time_utc_str.astimezone(nzt_tz)

# Configure logging
LOG_FOLDER = "logs"
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)

# Insert all possible attributes into table metadata_attributes
def insert_attributes_into_db():
    try:
        # Connect to individual_db MySQL database
        db_connection = mysql.connector.connect(
                    host=db_host,
                    user=db_user,
                    password=db_password,
                    database=db_name
                )
        logging.info(f"\n{time_NZT} The connection to DB was established.")
    except mysql.connector.Error as err:
        logging.error(f"\n{time_NZT} The connection to DB was not established, error was appeared {err}!")
        return
    
    try:
        cursor = db_connection.cursor()

        # Insert user metadata attributes into the database
        # Open the JSON file and load the data
        with open(FULL_METADATA, 'r') as f:
            data = json.load(f)

        # Extract the attributes from the JSON data
        attributes = data['Attributes']

        # Loop through the attributes and insert them into the table
        for attribute in attributes:
            cursor.execute('''
                            SELECT 1 FROM metadata_attributes WHERE 
                            attributes_id = %s AND
                            attributes_name = %s AND
                            attributes_type = %s AND
                            description = %s
                            ''',
                            (attribute['id'], 
                             attribute['field'], 
                             attribute['type'], 
                             attribute['description'])
                            )
            # check for duplicates
            if cursor.fetchone():
                logging.info(f"\n{time_NZT} Found duplicate of attribute {attribute['id']}.")
            else:
                cursor.execute('''
                            INSERT INTO metadata_attributes (
                                attributes_id, 
                                attributes_name, 
                                attributes_type, 
                                description)
                            VALUES (%s, %s, %s, %s)
                            ''',
                            (attribute['id'], 
                             attribute['field'], 
                             attribute['type'], 
                             attribute['description'])
                            )
        db_connection.commit()

        # Close the database connection
        cursor.close()
        db_connection.close()
        logging.info(f"\n{time_NZT} The metadata attributes was inserted into table successfully!")
        
    except mysql.connector.Error as err:
        logging.error(f"\n{time_NZT} The metadata attributes was inserted into table unsuccessful, error was appeared {err}!")
        db_connection.rollback()    
    return

# Insert defined versions of metadata 
def insert_metadata_into_db(metafile):
    try:
        # Connect to individual_db MySQL database
        db_connection = mysql.connector.connect(
                    host=db_host,
                    user=db_user,
                    password=db_password,
                    database=db_name
                )
        logging.info(f"\n{time_NZT} The connection to DB was established.")
    except mysql.connector.Error as err:
        logging.error(f"\n{time_NZT} The connection to DB was not established, error was appeared {err}!")
        return
    
    try:
        cursor = db_connection.cursor()

        # Insert user metadata attributes into the database
        # Open the JSON file and load the data
        with open(metafile, 'r') as f:
            data = json.load(f)

        # Extract the attributes from the JSON data
        dataset_name = data['Dataset Name']
        data_source = data['Data Source']
        description = data['Description']
        version = data['Version']
        attributes_list = [attr['id'] for attr in data['Attributes']]
        # Convert the list to a JSON-formatted string
        attributes_list_json = json.dumps(attributes_list)
        
        cursor.execute('''
                        SELECT 1 FROM metadata WHERE 
                        version = %s AND
                        dataset_name = %s AND
                        data_source = %s AND
                        description = %s AND
                        attributes_ids = %s
                        ''',
                        (version,
                         dataset_name, 
                         data_source, 
                         description,
                         attributes_list_json)
                        )
        # check for duplicates
        if cursor.fetchone():
            logging.info(f"\n{time_NZT} Found duplicate of metadata {version} version.")
        else:
            cursor.execute('''
                        INSERT INTO metadata (
                            dataset_name, 
                            data_source, 
                            description, 
                            version,
                            attributes_ids)
                        VALUES (%s, %s, %s, %s, %s)
                        ''',
                        (dataset_name, 
                         data_source, 
                         description, 
                         version,
                         attributes_list_json)
                        )
        db_connection.commit()

        # Close the database connection
        cursor.close()
        db_connection.close()
        logging.info(f"\n{time_NZT} The metadata was inserted into table successfully!")
        
    except mysql.connector.Error as err:
        logging.error(f"\n{time_NZT} The metadata was inserted into table unsuccessful, error was appeared {err}!")
        db_connection.rollback()    
    return

insert_attributes_into_db()

# Search all metadata files in directory
# Define the pattern for the file names
file_pattern = 'cycle_lines_metadata_v*.json'

# Use glob to find all the files that match the pattern
files = glob.glob(os.path.join(META_PATH, file_pattern))

# sort files by ascending
files = sorted(files)
for file in files:
    insert_metadata_into_db(file)