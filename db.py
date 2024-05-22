import mysql.connector
# import requests

# Connect to MySQL database
db_config = {
    'user': 'admin',
    'password': 'yeaWYdvmiGhJpjmFh0d4',
    'host': 'data472-rna104-db.cyi9p9kw8doa.ap-southeast-2.rds.amazonaws.com',
    # 'database': 'data472-rna104-db'
}
db_connection = mysql.connector.connect(**db_config)
cursor = db_connection.cursor()

# Create a new database
cursor.execute('CREATE DATABASE IF NOT EXISTS individual_db')
db_config['database'] = 'individual_db'
db_connection = mysql.connector.connect(**db_config)
cursor = db_connection.cursor()

# Create a new table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS temp_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        value INT NOT NULL
    )
''')
name = 'Roman'
value = 300

cursor.execute('INSERT INTO temp_table (name, value) VALUES (%s, %s)', (name, value))
db_connection.commit()
print('The data was inserted')

# Insert data from EC2 web server query
# ec2_url = 'http://your_ec2_web_server_url'
# response = requests.get(ec2_url)
# data = response.json()
# for item in data:
#     cursor.execute('INSERT INTO my_table (name, value) VALUES (%s, %s)', (item['name'], item['value']))
# db_connection.commit()

# Close the database connection
cursor.close()
db_connection.close()