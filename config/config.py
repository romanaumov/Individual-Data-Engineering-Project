import yaml

web_server_path = '/home/ubuntu/iCycleWays'
CONFIG = f'{web_server_path}/config/config.yaml'

with open(CONFIG, 'r') as file:
    data = yaml.safe_load(file)

# urls
db_name = data['db_name']
db_user = data['db_user']
db_password = data['db_password']
db_host = data['db_host']
api_key = data['api_key']
csv_path = data['csv_path']
meta_path = data['meta_path']
api_url = data['api_url']
log_path = f"{web_server_path}/{data['log']}"

