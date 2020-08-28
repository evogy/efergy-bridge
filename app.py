import os
from flask import Flask, jsonify, request
from repositories.plant import PlantRepo
from modules.tools import not_found, error

app = Flask(__name__)


@app.route('/plants')
def list_plant():
    plant = PlantRepo(app.logger)
    res = plant.list_plant()
    return jsonify(res)

@app.route('/plants/<string:id>')
def get_plant(id):
    plant = PlantRepo(app.logger)
    item = plant.get_plant(id)
    if not item:
        return not_found()
    
    return jsonify(item)

@app.route('/plants', methods=['POST'])
def create_plant():
    plant = PlantRepo(app.logger)
    res = plant.create_plant(request.json)
    if res:
        return jsonify(res), 201
    else:
        return error(plant.errors)

@app.route('/plants/<string:id>', methods=['PUT'])
def update_plant(id):
    plant = PlantRepo(app.logger)
    res = plant.update_plant(id, request.json)
    if res:
        return jsonify(res), 200
    else:
        return error(plant.errors)

@app.route('/plants/<string:id>', methods=['DELETE'])
def delete_plant(id):
    plant = PlantRepo(app.logger)
    plant.delete_plant(id)
    return jsonify(), 200

