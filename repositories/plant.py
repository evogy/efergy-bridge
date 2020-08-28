from models.plant import PlantTable
from modules.tools import decimal_to_digit_coverter
from schema import Schema, SchemaError, And, Use

class PlantRepo():

    def __init__(self, logger):
        self._plant_table = PlantTable()
        self.errors = {}
        self._logger = logger
    
    def list_plant(self):
        items = self._plant_table.list()
        return [decimal_to_digit_coverter(item) for item in items]
    
    def get_plant(self, id):
        response = self._plant_table.get(id)
        if response['Items'] == []:
            return False
        else:
            return decimal_to_digit_coverter(response['Items'][0])
    
    def delete_plant(self, id):
        response = self._plant_table.delete(id)
        self._logger.info(response)
    
    def update_plant(self, id, data):
        items = self._plant_table.scan_for_update(id)
        self._validation(data, items)
        if not self.errors:
            item = self._plant_table.update(id, data)
            return decimal_to_digit_coverter(item['Attributes'])
        else:
            return False
    
    def create_plant(self, data):
        items = self._plant_table.list()
        data = self._validation(data, items)
        if not self.errors:
            return self._plant_table.create(data)
        
        return False

    def _schema(self):
        is_empty = lambda l: l != ""
        return {
            'name':And(Use(str), is_empty, error="name cannot be empty"),
            'api_key':And(Use(str), is_empty, error="api_key cannot be empty"),
            'plant_id':And(Use(str), is_empty, error="plant_id cannot be empty")
        }
    
    def _validation(self, data, items):
        self.errors = {}
        try:
            schema = Schema(self._schema(), ignore_extra_keys=True)
            data = schema.validate(data)
            for item in items:
                if data['plant_id'] == item['plant_id']:
                    self.errors['plant_id'] = "plant_id attribute must be unique"
            return data
        except SchemaError as e:
            self.errors['general'] = e.code
