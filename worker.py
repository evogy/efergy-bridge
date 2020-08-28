import boto3
import os
import requests
import json
import pika
from datetime import datetime
from modules.tools import logger
from repositories.plant import PlantRepo
from modules.efergycache import EfergyCache

_LOGGER = logger('efergy')

def get_parameter(param_name):
    """
    Get parameters from the parameter store
    service (AWS SSM)
    """

    ssm = boto3.client('ssm')
    response = ssm.get_parameter(
        Name=param_name,
        WithDecryption=True
    )
    return response['Parameter']['Value']

def build_message(plant):
    """
    Build the json message to send in the Rabbit queue
    """
    API_URL = os.getenv('API_URL')
    API_TOKEN = plant['api_key']
    INSTALLATION_ID = plant['plant_id']

    try:
        r = requests.get(API_URL.format(api_token=API_TOKEN))
        json_req = r.json()

        if 'error' in json_req:
            _LOGGER.info(INSTALLATION_ID)
            _LOGGER.info(json.dumps(json_req))
            return False
        if 'status' in json_req and json_req['status'] == 'error':
            _LOGGER.info(json_req['description'])
            return False

        simon_obj = []
        for j in json_req:
            for key in j['data'][0]:
                pass
            simon_obj.append({
                'device':j['sid'],
                'measurementUnit': "W" if j['cid'] == 'PWER' else j['units'],
                'installation': INSTALLATION_ID,
                'name':j['cid'],
                'value':j['data'][0][key],
                'status':0,
                'timestamp': datetime.utcfromtimestamp(int(key)/1000.0).isoformat()
            })
        _LOGGER.info(simon_obj)
        return json.dumps(simon_obj)
    except requests.exceptions.RequestException as e:
        _LOGGER.error(e)
        return False


def handler(event, context):
    """
    Every time the function is triggered,
    retrieve the info from the Efergy cloud provider,
    build the JSON package send it to the queue
    """

    _LOGGER.info(event)
    if 'key' in event and event['key'] == 'clear_cache':
        _LOGGER.info("Empty cache.....")
        cacher = EfergyCache()
        cacher.clear_cache()
        return "ok"

    QUEUE_NAME = os.getenv('QUEUE_NAME')
    RABBIT_USER = get_parameter(os.getenv('RABBIT_USER'))
    RABBIT_PASS = get_parameter(os.getenv('RABBIT_PASS'))
    RABBIT_HOST = get_parameter(os.getenv('RABBIT_HOST'))

    plant = PlantRepo(_LOGGER)
    plants = plant.list_plant()
    if plants == []:
        return "no plants"
    
    for plant in plants:
        message = build_message(plant)
        if not message:
            continue

        try:
            credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
            parameters = pika.ConnectionParameters(host=RABBIT_HOST, virtual_host=RABBIT_USER, credentials=credentials)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.basic_publish(
                exchange='amq.direct',
                routing_key=QUEUE_NAME,
                body=message
            )
            connection.close()
        except Exception as e:
            _LOGGER.info(e)
    
    return "ok"
