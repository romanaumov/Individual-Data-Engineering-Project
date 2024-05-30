import io
from flask import Flask, request, Response, render_template, render_template_string, jsonify
import pandas as pd
import json
import logging
import os
import time
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

app = Flask(__name__)

# CSV_FILE = 'cycle_lines_new.csv'
# META_FILE = 'cycle_lines_metadata_v.1.0.json'
# API_KEY = "Fish-Sea-Hat-Forest!"
OUT_FIELDS = ['ServiceStatus', 'MajorCyclewayName', 'Type', 'CreateDate', 'LastEditDate', 'Shape__Length', 'GeometryPath']

def message():
    error_message = "The secure api key is not valid!"

    # Create an HTML template with the message
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Message</title>
    </head>
    <body>
        <h1>{error_message}</h1>
    </body>
    </html>
    """
    return render_template_string(html_template)

# http://<IP-ADDRESS>/rna104/cyclewaysapi?key=<YOUR-API-KEY>&data=html
# http://<IP-ADDRESS>/rna104/cyclewaysapi?key=<YOUR-API-KEY>&data=csv
# http://<IP-ADDRESS>/rna104/cyclewaysapi?key=<YOUR-API-KEY>&data=json
@app.route('/rna104/cyclewaysapi', methods=['GET'])
def query():
    api_key = request.args.get('key')
    format = request.args.get('data')
    
    if api_key != API_KEY:
        # logger.warning("Invalid API key attempt")
        print('The secure api key is not valid!')
        logging.info(f"\n{timestamp} The secure api key is not valid!")
        return jsonify({"error": "The secure api key is not valid!"}), 401
    
    # Read the CSV file
    data = pd.read_csv(CSV_PATH)
    
    if data is not None:
        # Select the fields from query
        data = data[OUT_FIELDS]
        
        # Get the headers (column names)
        headers = data.columns.tolist()

        # Get the rows (data) as a list of lists
        rows = data.values.tolist()
        
        if format == 'html':
            logging.info(f"\n{timestamp} Query with HTML format of data.")
            print('Query with HTML format of data.')
            # Render an HTML template with the header and rows
            # return render_template_string(html_template)
            return render_template('csv.html', header=headers, rows=rows)
        
        elif format == 'csv':
            logging.info(f"\n{timestamp} Query with CSV format of data.")
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
            logging.info(f"\n{timestamp} Query with JSON format of data.")
            print('Query with JSON format of data.')
            json_string = data.to_json(orient='records')
            
            # Convert JSON string to Python object
            json_data = json.loads(json_string)
            return json.dumps(json_data, indent=4)
        else:
            logging.info(f"\n{timestamp} Incorrect format of data in query. Use the following types of format - HTML, CSV, JSON only.")
            print('Incorrect format of data in query. Use the following types of format - HTML, CSV, JSON only.')
            return jsonify({"error": "Incorrect format of data in query. Use the following types of format - HTML, CSV, JSON only."}), 400
    else:
        logging.info(f"\n{timestamp} Data from the source in the file is empty. ERROR: Data retrieval failed.")
        print('Data from the source in the file is empty. ERROR: Data retrieval failed.')
        return jsonify({"error": "Data from the source in the file is empty. ERROR: Data retrieval failed."}), 500

# http://<IP-ADDRESS>/rna104/cyclewaysapimeta?key=<YOUR-API-KEY>
@app.route('/rna104/cyclewaysapimeta', methods=['GET'])
def meta():
    api_key = request.args.get('key')
    
    # Open the JSON file for reading
    with open(META_PATH, 'r') as f:
        # Load the JSON data from the file
        data = json.load(f)
        
    if data is not None:
        if api_key != API_KEY:
            logging.info(f"\n{timestamp} The secure api key is not valid!")
            print('The secure api key is not valid!')
            return jsonify({"error": "The secure api key is not valid!"}), 401

        logging.info(f"\n{timestamp} The file format of metadata is JSON.")
        print('The file format of metadata is JSON.')
        return json.dumps(data, indent=4)
    
    else:
        logging.info(f"\n{timestamp} Incorrect format of data in query. Use the following types of format - data = HTML, CSV, or JSON only.")
        print('Incorrect format of data in query. Use the following types of format - data = HTML, CSV, or JSON only.')
        return jsonify({"error": "Incorrect format of data in query. Use the following types of format - data = HTML, CSV, or JSON only."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)