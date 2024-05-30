import requests
import json
import csv
import datetime
import pytz
import os
import logging
import time
import sys

config_path = '/home/ubuntu/iCycleWays/config/'
sys.path.append(config_path)
import config

CSV_PATH = config.csv_path
API_URL = config.api_url
LOG_PATH = config.log_path
# API_URL = "https://gis.ccc.govt.nz/server/rest/services/OpenData/Cycle/FeatureServer/1/query?where=1%3D1&outFields=ServiceStatus,MajorCyclewayName,Type,TrafficDirection,CreateDate,LastEditDate,Shape__Length&outSR=4326&f=json"
# CSV_PATH = "cycle_lines_new.csv"

# Configure logging
LOG_FOLDER = "logs"
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
timestamp = time.strftime("%Y%m%d_%H%M%S")
# log_file_name = f"{LOG_FOLDER}/icycleways_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)

# Configure logging
# logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
# # Get today's date
# timestamp = time.strftime("%Y%m%d_%H%M%S")

def get_data_from_api(api_url):
    response = requests.get(api_url)

    if response.status_code == 200:
        logging.info(f"\n{timestamp} Data was loaded from source successfully.")
        return json.loads(response.text)
    else:
        logging.info(f"\n{timestamp} Data was loaded from the source unsuccessfully. Error with status code {response.status_code}")
        print(f"Error with status code {response.status_code}")
        return None

# Get data from source
data = get_data_from_api(API_URL)

# Create a timezone object for NZT timezone
nzt_tz = pytz.timezone('Pacific/Auckland')

if data:
    headers = list(data['features'][0]['attributes'].keys())
    headers.append('GeometryPath')
    
    # writing to csv file
    with open(CSV_PATH, 'a', newline='') as file:
        # creating a csv dict writer object
        writer = csv.DictWriter(file, fieldnames=headers)
    
        # writing headers (field names)
        writer.writeheader()
        logging.info(f"\n{timestamp} The header has been written to {CSV_PATH} successfully.")

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
        
        with open(CSV_PATH, 'a', newline='') as file:
            # creating a csv dict writer object
            writer = csv.DictWriter(file, fieldnames=headers)
        
            # writing data rows
            writer.writerows(dict)

    print(f"Data has been written to {CSV_PATH}")
    logging.info(f"\n{timestamp} Data has been written to {CSV_PATH} successfully.")
else:
    print("Failed to get data from API")
    logging.info(f"\n{timestamp} Data has been written to {CSV_PATH} unsuccessfully. Failed to get data from API")


    
# {
#     'attributes': 
#         {
#             'ServiceStatus': 'In Service', 
#             'MajorCyclewayName': 'South Express Cycleway', 
#             'Type': 'Cycleway', 
#             'CreateDate': 1710188478000, 
#             'LastEditDate': 1710188478000, 
#             'Shape__Length': 318.5999227930278, 
#             'Ownership': 'CCC', 
#             'PublicRelevance': 'Public'
#         }, 
#     'geometry': 
#         {
#             'paths': [[[172.5511221115049, -43.5356679321132], 
#                     [172.55112212094105, -43.53566766112292], 
#                     [172.55104247831542, -43.535693141032205], 
#                     [172.5509408241918, -43.53569702693292], 
#                     [172.55083914012886, -43.53570494471963], 
#                     [172.5507353531418, -43.535747216993435], 
#                     [172.55049419888073, -43.5358749810029], 
#                     [172.55034392922508, -43.53595605397301], 
#                     [172.5498561840983, -43.53545138446587], 
#                     [172.54980854420998, -43.53539742633398], 
#                     [172.54967683020024, -43.53546815360183], 
#                     [172.5489837886041, -43.53474355900613], 
#                     [172.54872522496436, -43.53448040937976], 
#                     [172.54865930104194, -43.53440083809024], 
#                     [172.5486429331808, -43.53436582355185], 
#                     [172.54863767065402, -43.534328163288485], 
#                     [172.54864901311146, -43.53428608807074]]]
#         }
# }