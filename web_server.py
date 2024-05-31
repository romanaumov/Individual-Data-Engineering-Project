import io
from flask import Flask, request, Response, render_template, render_template_string, jsonify
import pandas as pd
import json
import logging
import os
import glob
import datetime
import pytz
import sys

config_path = '/home/ubuntu/iCycleWays/config/'
sys.path.append(config_path)
import config

db_name = config.db_name
db_user = config.db_user
db_password = config.db_password
db_host = config.db_host
API_KEY = config.api_key
CSV_PATH = config.csv_path
META_PATH = config.meta_path
LOG_PATH = config.log_path


# Get a NZT time
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

app = Flask(__name__)

def get_metadata(version):
    file = get_version_metafile(version)
    # Open the JSON file for reading
    with open(file, 'r') as f:
        # Load the JSON data from the file
        data = json.load(f)
    return data

# Now exists 4 versions of meatadata: 1.0, 1.1, 2.1, 2.2
def get_version_metafile(version):
    
    # Define the latest version firstly (by default)
    
    # Define the pattern for the file names
    file_pattern = 'cycle_lines_metadata_v*.json'
    
    # Use glob to find all the files that match the pattern
    files = glob.glob(os.path.join(META_PATH, file_pattern))
    
    # sort files by descending
    files = sorted(files, reverse=True)
    
    # take the maximum version
    version_file = files[0]
    logging.info(f"\n{time_NZT} The latest version of metadata was found is following: {version_file}")
    
    if version is not None:
        # Define the pattern for the file name with the version number
        file_pattern = f'cycle_lines_metadata_v.{version}.json'
        logging.info(f"\n{time_NZT} The metadata file in query is following: {file_pattern}")

        # Use glob to find all the files that match the pattern
        files = glob.glob(os.path.join(META_PATH, file_pattern))

        if files:
            version_file = files[0]
            logging.info(f"\n{time_NZT} The file of the v.{version} version found.")
        else:
            # if nothing found, return the latest version of the file
            logging.info(f"\n{time_NZT} No file with version v.{version} found.")

    logging.info(f"\n{time_NZT} The version of metadata was found is following: {version_file}")
    return version_file

# http://<IP-ADDRESS>/rna104/cyclewaysapi?key=<YOUR-API-KEY>&data=html&version=<YOUR-VERSION>
# http://<IP-ADDRESS>/rna104/cyclewaysapi?key=<YOUR-API-KEY>&data=csv&version=<YOUR-VERSION>
# http://<IP-ADDRESS>/rna104/cyclewaysapi?key=<YOUR-API-KEY>&data=json&version=<YOUR-VERSION>

# http://<IP-ADDRESS>/rna104/cyclewaysapi?key=<YOUR-API-KEY> - return the data according to the latest version of metadata in JSON format
@app.route('/rna104/cyclewaysapi', methods=['GET'])
def query():
    api_key = request.args.get('key')
    format = request.args.get('data')
    version = request.args.get('version')
    
    # format = 'json' by default
    if format is None:
        logging.error(f"Error to get format attribute of a query. Default format is json.")
        format = 'json'
    
    # latest version by default
    if version is None:
        logging.error(f"Error to get version attribute of a query. Default version is the latest.")
        
    if api_key != API_KEY:
        logging.info(f"\n{time_NZT} The secure api key is not valid!")
        return jsonify({"error": "The secure api key is not valid!"}), 401
    
    # Read the CSV file
    data = pd.read_csv(CSV_PATH)
    
    if data is not None:
        
        # get metadata according to the version
        metadata = get_metadata(version)
        attributes = [attr['field'] for attr in metadata['Attributes']]
        logging.info(f"\n{time_NZT} The attributes of metadata is following: {attributes}")
        
        # Select the fields from metadata according with the version
        data = data[attributes]
        
        # Get the headers (column names)
        headers = data.columns.tolist()

        # Get the rows (data) as a list of lists
        rows = data.values.tolist()
        
        if format == 'html':
            logging.info(f"\n{time_NZT} Query with HTML format of data.")
            # Render an HTML template with the header and rows
            return render_template('csv.html', header=headers, rows=rows)
        
        elif format == 'csv':
            logging.info(f"\n{time_NZT} Query with CSV format of data.")
            print('Query with CSV format of data.')
            # Convert the DataFrame to CSV
            csv_data = data.to_csv(index=False)

            # Create an in-memory file-like object
            output = io.StringIO()

            # Write the CSV string to the file-like object
            output.write(csv_data)

            # Create a response object with the CSV string
            response = Response(output.getvalue(), mimetype='text/csv')

            # Set the Content-Disposition header to include the filename
            response.headers['Content-Disposition'] = f'attachment; filename={CSV_PATH}'
            return response
        
        elif format == 'json':
            logging.info(f"\n{time_NZT} Query with JSON format of data.")
            json_string = data.to_json(orient='records')
            
            # Convert JSON string to Python object
            json_data = json.loads(json_string)
            return json.dumps(json_data, indent=4)
        else:
            logging.info(f"\n{time_NZT} Incorrect format of data in query. Use the following types of format - HTML, CSV, JSON only.")
            return jsonify({"error": "Incorrect format of data in query. Use the following types of format - HTML, CSV, JSON only."}), 400
    else:
        logging.info(f"\n{time_NZT} Data from the source in the file is empty. ERROR: Data retrieval failed.")
        return jsonify({"error": "Data from the source in the file is empty. ERROR: Data retrieval failed."}), 500

# http://<IP-ADDRESS>/rna104/cyclewaysapimeta?key=<YOUR-API-KEY>&version=<YOUR-VERSION>
# http://<IP-ADDRESS>/rna104/cyclewaysapimeta?key=<YOUR-API-KEY> - return the latest version of metadata in JSON format
@app.route('/rna104/cyclewaysapimeta', methods=['GET'])
def meta():
    api_key = request.args.get('key')
    version = request.args.get('version')
    
    # get metadata according to the version
    data = get_metadata(version)
        
    if data is not None:
        if api_key != API_KEY:
            logging.info(f"\n{time_NZT} The secure api key is not valid!")
            return jsonify({"error": "The secure api key is not valid!"}), 401

        logging.info(f"\n{time_NZT} The file format of metadata is JSON.")
        return json.dumps(data, indent=4)
    
    else:
        logging.info(f"\n{time_NZT} Incorrect format of data in query. Use the following types of format - data = HTML, CSV, or JSON only.")
        return jsonify({"error": "Incorrect format of data in query. Use the following types of format - data = HTML, CSV, or JSON only."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)