from .table import Table
import os
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import uuid
from modules.efergycache import get_cached_items, delete_items, clear_worker_cache

class PlantTable(Table):

    def __init__(self):
        super().__init__(os.getenv("PLANTS_TABLE"))
    

    @get_cached_items()
    def get(self, id):
        item = self._client.query(
            KeyConditionExpression=Key("id").eq(id)
        )
        return item

    @get_cached_items(key='plants')
    def list(self):
        items = self._client.scan()
        return items['Items']
    
    @delete_items
    @clear_worker_cache
    def delete(self, id):
        response = self._client.delete_item(
            Key = {
                'id':id
            }
        )
        return response
    
    @delete_items
    @clear_worker_cache
    def create(self, data):
        data['added_at'] = datetime.now().isoformat()
        data['id'] = str(uuid.uuid4())
        self._client.put_item(
            Item=data
        )
        return data
    
    def scan_for_update(self, id):
        items = self._client.scan(
            FilterExpression=Attr('id').ne(id)
        )
        return items['Items']
    
    @delete_items
    @clear_worker_cache
    def update(self, id, data):
        response = self._client.update_item(
            Key={
                'id':id
            },
            UpdateExpression='set #name=:n, api_key=:at, plant_id=:pi',
            ExpressionAttributeValues={
                ':n': data['name'],
                ':at': data['api_key'],
                ':pi': data['plant_id']
            },
            ExpressionAttributeNames={
                "#name":"name"
            },
            ReturnValues="ALL_NEW"
        )
        return response
    
