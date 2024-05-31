import requests
import json
import csv
import datetime
import pytz
import os
import logging
import datetime
import sys
import mysql.connector

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

# # Get a NZT timezone 
nzt_tz = pytz.timezone('Pacific/Auckland')
time_utc = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
time_utc_str = datetime.datetime.strptime(time_utc, '%Y-%m-%d %H:%M:%S')
time_NZT = time_utc_str.astimezone(nzt_tz)

# Configure logging
LOG_FOLDER = "logs"
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
# timestamp = time.strftime("%Y%m%d_%H%M%S")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)

def insert_data_into_db(dict, time_NZT):
    try:
        # Connect to individual_db MySQL database
        db_connection = mysql.connector.connect(
                    host=db_host,
                    user=db_user,
                    password=db_password,
                    database=db_name
                )
    except mysql.connector.Error as err:
        logging.info(f"\n{time_NZT} The connection to DB was not established, error was appeared {err}!")
        
        return
    
    try:
        cursor = db_connection.cursor()
        
        # Insert user data into the database
        cursor.execute('''
                    INSERT INTO data (
                        timestamp,
                        service_status,
                        major_cycleway_name,
                        type,
                        traffic_direction,
                        create_date,
                        last_edit_date,
                        shape_length,
                        ownership,
                        public_relevance,
                        geometry
                        ) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''',
                        (time_NZT,
                        dict[0]['ServiceStatus'],
                        dict[0]['MajorCyclewayName'],
                        dict[0]['Type'],
                        dict[0]['TrafficDirection'],
                        dict[0]['CreateDate'],
                        dict[0]['LastEditDate'],
                        dict[0]['Shape__Length'],
                        dict[0]['Ownership'],
                        dict[0]['PublicRelevance'],
                        str(dict[0]['GeometryPath']))
        )
        
        db_connection.commit()

        # Close the database connection
        cursor.close()
        db_connection.close()
        
    except mysql.connector.Error as err:
        logging.info(f"\n{time_NZT} The data was inserted into tables unsuccessful, error was appeared {err}!")
        db_connection.rollback()    
    return

def get_data_from_api(api_url):
    response = requests.get(api_url)

    if response.status_code == 200:
        logging.info(f"\n{time_NZT} Data was loaded from source successfully.")
        return json.loads(response.text)
    else:
        logging.error(f"\n{time_NZT} Data was loaded from the source unsuccessfully. Error with status code {response.status_code}")
        print(f"Error with status code {response.status_code}")
        return None

# Get data from source
data = get_data_from_api(API_URL)

if data:
    headers = list(data['features'][0]['attributes'].keys())
    headers.append('GeometryPath')
    
    # writing to csv file
    with open(CSV_PATH, 'w', newline='') as file:
        # creating a csv dict writer object
        writer = csv.DictWriter(file, fieldnames=headers)
    
        # writing headers (field names)
        writer.writeheader()
        logging.info(f"\n{time_NZT} The header has been written to {CSV_PATH} successfully.")

    logging.info(f"\n{time_NZT} Parse data from the source and save into file and DB tables ....")
    
    # Parse data from the source and save into file with necessary fields.
    for i in range (0, len(data['features'])):
        
        timestamp_utc_create = data['features'][i]['attributes']['CreateDate']
        create_date_utc = datetime.datetime.fromtimestamp(timestamp_utc_create / 1000)
        
        # Convert the datetime object to NZT timezone
        CreateDate_NZT = create_date_utc.replace(tzinfo=pytz.utc).astimezone(nzt_tz)
        
        timestamp_utc_edit = data['features'][i]['attributes']['LastEditDate']
        edit_date_utc = datetime.datetime.fromtimestamp(timestamp_utc_edit / 1000)
        
        # Convert the datetime object to NZT timezone
        LastEditDate_NZT = edit_date_utc.replace(tzinfo=pytz.utc).astimezone(nzt_tz)
        
        dict = [{
                    'ServiceStatus': data['features'][i]['attributes']['ServiceStatus'], 
                    'MajorCyclewayName': data['features'][i]['attributes']['MajorCyclewayName'], 
                    'Type': data['features'][i]['attributes']['Type'], 
                    'TrafficDirection': data['features'][i]['attributes']['TrafficDirection'],
                    'CreateDate': CreateDate_NZT,
                    'LastEditDate': LastEditDate_NZT,
                    'Shape__Length': round(data['features'][i]['attributes']['Shape__Length'], 2) ,
                    'Ownership': data['features'][i]['attributes']['Ownership'],
                    'PublicRelevance': data['features'][i]['attributes']['PublicRelevance'],
                    'GeometryPath': data['features'][i]['geometry']['paths'],
                }]
        
        insert_data_into_db(dict, time_NZT)
        
        with open(CSV_PATH, 'a', newline='') as file:
            # creating a csv dict writer object
            writer = csv.DictWriter(file, fieldnames=headers)
        
            # writing data rows
            writer.writerows(dict)

    logging.info(f"\n{time_NZT} Data has been written to {CSV_PATH} and Database successfully.")
    
else:
    logging.info(f"\n{time_NZT} Data has been written to {CSV_PATH} unsuccessfully. Failed to get data from API")
