import yaml

web_server_path = '/home/ubuntu/iCycleWays'
CONFIG = f'{web_server_path}/config/config.yaml'

with open(CONFIG, 'r') as file:
    data = yaml.safe_load(file)

# urls
# db:
db_name = data['db']['db_name']
db_user = data['db']['db_user']
db_password = data['db']['db_password']
db_host = data['db']['db_host']
    
# path:
csv_path = f"{web_server_path}/{data['path']['csv_path']}"
meta_path = f"{web_server_path}/{data['path']['meta_path']}"
log_path = f"{web_server_path}/{data['path']['log']}"
    
# api:
api_key = data['api']['api_key']
api_url = data['api']['api_url']