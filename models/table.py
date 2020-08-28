import os
import boto3
from abc import ABC, abstractmethod

class Table(ABC):

    IS_OFFLINE = os.getenv('IS_OFFLINE')

    def __init__(self, table):
        if self.IS_OFFLINE:
            dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url='http://localhost:8000/'
            )
        else:
            dynamodb = boto3.resource('dynamodb')
        
        self._client = dynamodb.Table(table)
        super().__init__()
    
    @abstractmethod
    def get(self, id):
        pass
    
    @abstractmethod
    def list(self):
        pass
    
    @abstractmethod
    def delete(self, id):
        pass
    
    @abstractmethod
    def create(self, data):
        pass
    
    @abstractmethod
    def update(self, id, data):
        pass