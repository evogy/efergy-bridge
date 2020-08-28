from .table import Table
import os
from modules.efergycache import get_cached_items

class UserTable(Table):

    def __init__(self):
        super().__init__(os.getenv("AUTH_TABLE_NAME"))
    
    @get_cached_items(key='users')
    def list(self):
        items = self._client.scan()
        return items['Items']
    
    def delete(self, id):
        pass
    
    def get(self, id):
        pass
    
    def create(self, data):
        pass
    
    def update(self, id, data):
        pass