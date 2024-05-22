import requests
import json
import csv
import datetime
import pytz
import math

def get_data_from_api(api_url):
    response = requests.get(api_url)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(f"Error with status code {response.status_code}")
        return None

# Use the function
api_url = "https://gis.ccc.govt.nz/server/rest/services/OpenData/Cycle/FeatureServer/1/query?where=1%3D1&outFields=ServiceStatus,MajorCyclewayName,Type,CreateDate,LastEditDate,Shape__Length,Ownership,PublicRelevance&geometry=&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outSR=4326&f=json"
# api_url = "https://gis.ccc.govt.nz/server/rest/services/OpenData/Cycle/FeatureServer/1/query?outFields=*&where=1%3D1&f=geojson"

data = get_data_from_api(api_url)

# filename_orig = "cycle_lines_orig.csv"
# # Extract the keys from the dictionary
# headers_orig = data.keys()

# # Since data is a dictionary, not a list, we write it as a single row
# with open(filename_orig, 'w', newline='') as f_output:
#     csv_writer = csv.writer(f_output)
#     csv_writer.writerow(headers_orig)
#     csv_writer.writerow([json.dumps(data[col]) for col in headers_orig])

# print("Data has been written to cycle_lines_orig.csv")


# OUTPUT_FILES = "./output/" # change the output folder
# write the results of classification for every frame into csv file
# filename = f"{OUTPUT_FILES}cycle_lines.csv"
filename = "/home/ubuntu/cycle_lines.csv"

# The timestamp, in milliseconds
# timestamp = 1616412806000

# Convert the timestamp to a datetime object
# dt_object = datetime.datetime.fromtimestamp(timestamp / 1000)

# print(dt_object)

# Create a timezone object for NZT timezone
nzt_tz = pytz.timezone('Pacific/Auckland')

# The radius of the Earth, in meters
R = 6371e3

if data:
    headers = list(data['features'][0]['attributes'].keys())
    headers.append('GeometryPath')
    
    # writing to csv file
    with open(filename, 'a', newline='') as file:
        # creating a csv dict writer object
        writer = csv.DictWriter(file, fieldnames=headers)
    
        # writing headers (field names)
        writer.writeheader()

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
                    'CreateDate': CreateDate_NZT,
                    'LastEditDate': LastEditDate_NZT,
                    # 'Shape__Length': data['features'][i]['attributes']['Shape__Length'],
                    'Shape__Length': round(data['features'][i]['attributes']['Shape__Length'], 2) ,
                    'Ownership': data['features'][i]['attributes']['Ownership'],
                    'PublicRelevance': data['features'][i]['attributes']['PublicRelevance'],
                    'GeometryPath': data['features'][i]['geometry']['paths'],
                }]
        
        with open(filename, 'a', newline='') as file:
            # creating a csv dict writer object
            writer = csv.DictWriter(file, fieldnames=headers)
        
            # writing data rows
            writer.writerows(dict)

    print("Data has been written to cycle_lines.csv")
else:
    print("Failed to get data from API")


    
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