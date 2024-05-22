import io
from flask import Flask, request, Response, render_template, render_template_string, jsonify
import pandas as pd
import json
# import requests

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace this with your own secret key

def message():
    error_message = "The secure key is not valid!"

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

@app.route('/rna104/cyclewaysapi', methods=['GET'])
def query():
    print('Have got a query...')
    key = request.args.get('key')
    # out_fields = request.args.get('fields').split(',')
    format = request.args.get('data')
    
    key_phrase = "Fish-Sea-Hat-Forest!"
    if key != key_phrase:
        print('The secure key is not valid!')
        return message()
    
    csv_file = 'cycle_lines.csv'
    
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # ServiceStatus,MajorCyclewayName,Type,CreateDate,LastEditDate,Shape__Length,GeometryPath&f=html
    out_fields = ['ServiceStatus', 'MajorCyclewayName', 'Type', 'CreateDate', 'LastEditDate', 'Shape__Length', 'GeometryPath']

    # Select the fields from query
    df = df[out_fields]
    
    # Get the headers (column names)
    headers = df.columns.tolist()

    # Get the rows (data) as a list of lists
    rows = df.values.tolist()

    # Convert the DataFrame to HTML
    # html_table = df.to_html(index=False, justify='center')

    # Create an HTML template with the table
    # html_template = f"""
    # <!DOCTYPE html>
    # <html lang="en">
    # <head>
    #     <meta charset="UTF-8">
    #     <title>API Response</title>
    #     <style>
    #         table {{
    #             width: 50%;
    #             margin-left: auto;
    #             margin-right: auto;
    #             border-collapse: collapse;
    #         }}
    #         th, td {{
    #             border: 1px solid black;
    #             padding: 8px;
    #             text-align: center;
    #         }}
    #         th {{
    #             background-color: #f2f2f2;
    #         }}
    #     </style>
    # </head>
    # <body>
    #     {html_table}
    # </body>
    # </html>
    # """

    if format == 'html':
            print('The file format is HTML.')
            # Render an HTML template with the header and rows
            # return render_template_string(html_template)
            return render_template('csv.html', header=headers, rows=rows)
    elif format == 'csv':
        print('The file format is CSV.')
        # Convert the DataFrame to CSV
        csv_data = df.to_csv(index=False)

        # Create an in-memory file-like object
        output = io.StringIO()

        # Write the CSV string to the file-like object
        output.write(csv_data)

        # Create a response object with the CSV string
        response = Response(output.getvalue(), mimetype='text/csv')

        # Set the Content-Disposition header to include the filename
        response.headers['Content-Disposition'] = f'attachment; filename={csv_file}'
        return response
    else:
        json_string = df.to_json(orient='records')
        # Convert JSON string to Python object
        json_data = json.loads(json_string)

        return json.dumps(json_data, indent=4)

# Set the upload endpoint URL
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     # Get the request data
#     data = request.data

#     # Set the path to save the CSV file
#     save_path = './model_files/csv/file.csv'

#     # Save the CSV file to the filesystem
#     with open(save_path, 'wb') as csv_file:
#         csv_file.write(data)

#     # Return a success response
#     return 'CSV file uploaded successfully', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)