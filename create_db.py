import mysql.connector
import sys
import datetime

# Get today's date
time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

config_path = '/home/ubuntu/iCycleWays/config/'
sys.path.append(config_path)
import config

db_name = config.db_name
db_user = config.db_user
db_password = config.db_password
db_host = config.db_host

try:
    # Connect to individual_db MySQL database
    db_connection = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name
            )
    print(f'{time} The connection to DB was established.')
    cursor = db_connection.cursor()

    # Create a database jarrd_db
    cursor.execute('CREATE DATABASE IF NOT EXISTS individual_db')
    cursor = db_connection.cursor()
        
    # # DROP tables
    # cursor.execute('''
    #     DROP TABLE metadata;
    # ''')
    # if cursor.rowcount == 0:
    #     print("Tables were deleted successfully")
    # else:
    #     print("No tables were deleted")
        

    # Create a table metadata
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            version VARCHAR(255) PRIMARY KEY,
            dataset_name VARCHAR(255) NOT NULL,
            data_source VARCHAR(255) NOT NULL,
            description VARCHAR(255) NOT NULL,
            attributes_ids VARCHAR(255) NOT NULL
        )
    ''')

    # Create a table metadata_attributes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata_attributes (
            attributes_id INT PRIMARY KEY,
            attributes_name VARCHAR(255) NOT NULL,
            attributes_type VARCHAR(255) NOT NULL,
            description VARCHAR(255)
        )
    ''')

    # Create a table fire_predictions_files
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            service_status VARCHAR(255),
            major_cycleway_name VARCHAR(255),
            type VARCHAR(255),
            traffic_direction VARCHAR(255),
            create_date DATE,
            last_edit_date DATE,
            shape_length DOUBLE,
            ownership VARCHAR(255),
            public_relevance VARCHAR(255),
            geometry VARCHAR(255)
        )
    ''')
    
    # geometry GEOMETRY

    print(f'{time} The tables were created')
except mysql.connector.Error as err:
    print(f'{time} The tables were created unsuccessful, error was appeared {err}!')

# Close the database connection
cursor.close()
db_connection.close()
