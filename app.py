from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_expects_json import expects_json
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(
    user='root', password='reto', server='localhost', database='reto')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Location(db.Model):
    __tablename__ = 'location'
    locationId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    capacity = db.Column(db.Integer, nullable=False)
    size = db.Column(db.Integer, nullable=False)

    def __init__(self, name, capacity, size):
        self.name = name
        self.capacity = capacity
        self.size = size


class Parameter(db.Model):
    __tablename__ = 'parameter'
    parameterId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    unit = db.Column(db.String(15), nullable=False)
    min = db.Column(db.Float, nullable=False)
    max = db.Column(db.Float, nullable=False)

    def __init__(self, name, unit, min, max):
        self.name = name
        self.unit = unit
        self.min = min
        self.max = max


class Model(db.Model):
    __tablename__ = 'model'
    modelId = db.Column(db.Integer, primary_key=True)
    modelName = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, modelName):
        self.modelName = modelName


class ModelParameter(db.Model):
    __tablename__ = 'model_parameters'
    id = db.Column(db.Integer, primary_key=True)
    modelId = db.Column(db.Integer, db.ForeignKey(
        'model.modelId'), nullable=False)
    parameterId = db.Column(db.Integer, db.ForeignKey(
        'parameter.parameterId'), nullable=False)
    parameters = db.relationship(
        'Parameter', backref=db.backref('parameters', lazy=True))

    def __init__(self, modelId, parameterId):
        self.modelId = modelId
        self.parameterId = parameterId


class Device(db.Model):
    __tablename__ = 'device'
    deviceId = db.Column(db.Integer, primary_key=True)
    # 0 = not available, 1 = available, 2 = error, 3 = alert
    status = db.Column(db.Integer, nullable=False)
    mac = db.Column(db.String(17), nullable=False, unique=True)
    locationId = db.Column(db.Integer, db.ForeignKey(
        'location.locationId'), nullable=False)
    modelId = db.Column(db.Integer, db.ForeignKey(
        'model.modelId'), nullable=False)

    def __init__(self, status, mac, locationId, modelId):
        self.status = status
        self.mac = mac
        self.locationId = locationId
        self.modelId = modelId


class Measurement(db.Model):
    __tablename__ = 'measurement'
    measurementId = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    parameterId = db.Column(db.Integer, db.ForeignKey(
        'parameter.parameterId'), nullable=False)
    deviceId = db.Column(db.Integer, db.ForeignKey(
        'device.deviceId'), nullable=False)

    def __init__(self, value, timestamp, parameterId, deviceId):
        self.value = value
        self.timestamp = timestamp
        self.parameterId = parameterId
        self.deviceId = deviceId


createLocationSchema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'capacity': {'type': 'number'},
        'size': {'type': 'number'},
    },
    'required': ['name', 'capacity', 'size']
}

updateLocationSchema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'capacity': {'type': 'number'},
        'size': {'type': 'number'},
    },
    'required': []
}


@app.route('/locations', methods=['POST'])
@expects_json(createLocationSchema)
def create_location():
    data = request.json
    location = Location(name=data['name'],
                        capacity=data['capacity'], size=data['size'])
    db.session.add(location)
    db.session.commit()
    response = jsonify({'message': 'ok'})
    response.status_code = 201
    return response


@app.route('/locations/<int:id>', methods=['PUT'])
@expects_json(updateLocationSchema)
def update_location(id):
    data = request.json
    location = Location.query.get(id)
    if location is None:
        response = jsonify({'message': 'not found'})
        response.status_code = 404
        return response
    if ('capacity' in data and data['capacity'] is not None):
        location.capacity = data['capacity']
    if ('size' in data and data['size'] is not None):
        location.size = data['size']
    if ('name' in data and data['name'] is not None):
        location.name = data['name']
    db.session.commit()
    response = jsonify({'message': 'ok'})
    response.status_code = 200
    return response


@app.route('/locations', methods=['DELETE'])
def delete_location():
    data = request.json
    location = Location.query.get(data['locationId'])
    db.session.delete(location)
    db.session.commit()
    response = jsonify({'message': 'ok'})
    response.status_code = 200
    return response


@app.route('/locations/<int:id>', methods=['GET'])
def get_location(id):
    location = Location.query.get(id)
    if location is None:
        response = jsonify({'message': 'not found'})
        response.status_code = 404
        return response
    response = jsonify(
        {'name': location.name, 'capacity': location.capacity, 'size': location.size})
    response.status_code = 200
    return response


@app.route('/locations/<string:name>', methods=['GET'])
def search_location(name):
    locations = Location.query.filter(
        Location.name.like('%' + name + '%'))

    response = jsonify(
        [{'id': location.locationId, 'name': location.name, 'capacity': location.capacity, 'size': location.size} for location in locations])
    response.status_code = 200
    return response


@app.route('/locations', methods=['GET'])
def get_locations():
    locations = Location.query.all()
    response = jsonify([{"id": location.locationId, "name": location.name,
                       "capacity": location.capacity, "size": location.size} for location in locations])
    response.status_code = 200
    return response


@app.route('/models', methods=['GET'])
def get_models():
    models = Model.query.all()
    response = jsonify(
        [{"id": model.modelId, "modelName": model.modelName} for model in models])
    response.status_code = 200
    return response


@app.route('/models/<int:id>', methods=['GET'])
def get_model(id):
    model = Model.query.get(id)
    if model is None:
        response = jsonify({'message': 'not found'})
        response.status_code = 404
        return response
    response = jsonify({'modelName': model.modelName})
    response.status_code = 200
    return response


@app.route('/models/<string:name>', methods=['GET'])
def search_model(name):
    models = Model.query.filter(
        Model.modelName.like('%' + name + '%'))

    response = jsonify(
        [{'id': model.modelId, 'modelName': model.modelName} for model in models])
    response.status_code = 200
    return response


createModelSchema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
    },
    'required': ['name']
}

updateModelSchema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
    },
    'required': []
}


@app.route('/models', methods=['POST'])
@expects_json(createModelSchema)
def create_model():
    data = request.json
    model = Model(modelName=data['name'])
    db.session.add(model)
    db.session.commit()
    response = jsonify({'message': 'ok'})
    response.status_code = 201
    return response


@app.route('/models/<int:id>', methods=['PUT'])
@expects_json(updateModelSchema)
def update_model(id):
    data = request.json
    model = Model.query.get(id)
    if model is None:
        response = jsonify({'message': 'not found'})
        response.status_code = 404
        return response
    if ('name' in data and data['name'] is not None):
        model.modelName = data['name']
        db.session.commit()
    response = jsonify({'message': 'ok'})
    response.status_code = 200
    return response


@app.route('/models/<int:id>', methods=['DELETE'])
def delete_model(id):
    model = Model.query.get(id)
    if model is None:
        response = jsonify({'message': 'not found'})
        response.status_code = 404
        return response
    db.session.delete(model)
    db.session.commit()
    response = jsonify({'message': 'ok'})
    response.status_code = 200
    return response


@app.route('/parameters', methods=['GET'])
def get_parameters():
    parameters = Parameter.query.all()
    response = jsonify(
        [{"id": parameter.parameterId, "name": parameter.name, "unit": parameter.unit, "min": parameter.min, "max": parameter.max} for parameter in parameters])
    response.status_code = 200
    return response


@app.route('/parameters/<int:id>', methods=['GET'])
def get_parameter(id):
    parameter = Parameter.query.get(id)
    if parameter is None:
        response = jsonify({'message': 'not found'})
        response.status_code = 404
        return response
    response = jsonify({'name': parameter.name, 'unit': parameter.unit,
                       'min': parameter.min, 'max': parameter.max})
    response.status_code = 200
    return response


@app.route('/parameters/<string:name>', methods=['GET'])
def search_parameter(name):
    parameters = Parameter.query.filter(
        Parameter.name.like('%' + name + '%'))

    response = jsonify(
        [{'id': parameter.parameterId, 'name': parameter.name, 'unit': parameter.unit, 'min': parameter.min, 'max': parameter.max} for parameter in parameters])
    response.status_code = 200
    return response


createParameterSchema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'unit': {'type': 'string'},
        'min': {'type': 'number'},
        'max': {'type': 'number'},
    },
    'required': ['name', 'unit', 'min', 'max']
}

updateParameterSchema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'unit': {'type': 'string'},
        'min': {'type': 'number'},
        'max': {'type': 'number'},
    },
    'required': ['name', 'unit', 'min', 'max']
}


@app.route('/parameters', methods=['POST'])
@expects_json(createParameterSchema)
def create_parameter():
    data = request.json
    parameter = Parameter(
        name=data['name'], unit=data['unit'], min=data['min'], max=data['max'])
    db.session.add(parameter)
    db.session.commit()
    response = jsonify({'message': 'ok'})
    response.status_code = 201
    return response


@app.route('/parameters/<int:id>', methods=['PUT'])
@expects_json(updateParameterSchema)
def update_parameter(id):
    data = request.json
    parameter = Parameter.query.get(id)
    if parameter is None:
        response = jsonify({'message': 'not found'})
        response.status_code = 404
        return response
    if ('name' in data and data['name'] is not None):
        parameter.name = data['name']
    if ('unit' in data and data['unit'] is not None):
        parameter.unit = data['unit']
    if ('min' in data and data['min'] is not None):
        parameter.min = data['min']
    if ('max' in data and data['max'] is not None):
        parameter.max = data['max']
    db.session.commit()
    response = jsonify({'message': 'ok'})
    response.status_code = 200
    return response


@app.route('/parameters/<int:id>', methods=['DELETE'])
def delete_parameter(id):
    parameter = Parameter.query.get(id)
    if parameter is None:
        response = jsonify({'message': 'not found'})
        response.status_code = 404
        return response
    db.session.delete(parameter)
    db.session.commit()
    response = jsonify({'message': 'ok'})
    response.status_code = 200
    return response


@app.route('/model/<int:id>/parameters', methods=['GET'])
def get_model_parameters(id):
    query = f"""
    SELECT *
    FROM model_parameters
    INNER JOIN parameter ON parameter.parameterId = model_parameters.parameterId
    AND model_parameters.modelId = {id};
    """
    parameters = db.engine.execute(query)

    response = jsonify([{"id": parameter.parameterId, "name": parameter.name, "unit": parameter.unit,
                         "min": parameter.min, "max": parameter.max} for parameter in parameters])
    response.status_code = 200
    return response


createModelParameterSchema = {
    'type': 'object',
    'properties': {
        'parameterId': {'type': 'number'},
    },
    'required': ['parameterId']
}


@app.route('/model/<int:id>/parameters', methods=['POST'])
@expects_json(createModelParameterSchema)
def add_parameter_to_model(id):
    data = request.json
    model_parameter = ModelParameter(
        modelId=id, parameterId=data['parameterId'])
    db.session.add(model_parameter)
    db.session.commit()
    response = jsonify({'message': 'ok'})
    response.status_code = 201
    return response


@app.route('/model/<int:modelId>/parameters/<int:parameterId>', methods=['DELETE'])
def delete_parameter_from_model(modelId, parameterId):
    model_parameter = ModelParameter.query.filter(
        ModelParameter.modelId == modelId, ModelParameter.parameterId == parameterId).first()
    if model_parameter is None:
        response = jsonify({'message': 'not found'})
        response.status_code = 404
        return response
    db.session.delete(model_parameter)
    db.session.commit()
    response = jsonify({'message': 'ok'})
    response.status_code = 200
    return response


@app.route('/devices', methods=['GET'])
def get_devices():
    query = """
    SELECT *,
        model.modelName,
        location.name AS locationName
    FROM device
        LEFT JOIN model ON device.modelId = model.modelId
        LEFT JOIN location ON device.locationId = location.locationId;
    """
    devices = db.engine.execute(query)
    response = jsonify([{"id": device.deviceId, "status": device.status, "mac": device.mac, "modelId": device.modelId,
                       "locationId": device.locationId, "modelName": device.modelName, "locationName": device.locationName} for device in devices])
    response.status_code = 200
    return response


@app.route('/devices/<int:id>', methods=['GET'])
def get_device(id):
    query = f"""
    SELECT *,
        model.modelName,
        location.name AS locationName
    FROM device
        LEFT JOIN model ON device.modelId = model.modelId
        LEFT JOIN location ON device.locationId = location.locationId
    WHERE device.deviceId = {id};
    """
    device = db.engine.execute(query).first()
    if device is None:
        response = jsonify({'message': 'not found'})
        response.status_code = 404
        return response
    response = jsonify({"id": device.deviceId, "status": device.status, "mac": device.mac, "modelId": device.modelId,
                       "locationId": device.locationId, "modelName": device.modelName, "locationName": device.locationName})
    response.status_code = 200
    return response


@app.route('/devicesfull/<int:id>', methods=['GET'])
def get_device_full(id):
    query = f"""
    SELECT *, model.modelName
    FROM device
        LEFT JOIN model ON device.modelId = model.modelId
        LEFT JOIN location ON device.locationId = location.locationId
    WHERE device.deviceId = {id};
    """
    device = db.engine.execute(query).first()
    if device is None:
        response = jsonify({'message': 'not found'})
        response.status_code = 404
        return response
    response = jsonify({"id": device.deviceId, "status": device.status, "mac": device.mac, "modelId": device.modelId,
                       "locationId": device.locationId, "modelName": device.modelName, "locationName": device.name, "locationSize": device.size, "locationCapacity": device.capacity})
    response.status_code = 200
    return response

# Prepend MAC address with 'm', so that it can be differentiated from deviceId


@app.route('/devices/<string:mac>', methods=['GET'])
def get_device_by_mac(mac):
    query = f"""
    SELECT *,
        model.modelName,
        location.name AS locationName
    FROM device
        LEFT JOIN model ON device.modelId = model.modelId
        LEFT JOIN location ON device.locationId = location.locationId
    WHERE device.mac = '{mac[1:]}';
    """
    device = db.engine.execute(query).first()
    if device is None:
        response = jsonify({'message': 'not found'})
        response.status_code = 404
        return response
    response = jsonify({"id": device.deviceId, "status": device.status, "mac": device.mac, "modelId": device.modelId,
                       "locationId": device.locationId, "modelName": device.modelName, "locationName": device.locationName})
    response.status_code = 200
    return response


createDeviceSchema = {
    'type': 'object',
    'properties': {
        # status is excluded becuase it is set by the device
        'mac': {'type': 'string'},
        'locationId': {'type': 'number'},
        'modelId': {'type': 'number'},
    },
    'required': ['mac', 'locationId', 'modelId']
}

updateDeviceSchema = {
    'type': 'object',
    'properties': {
        'locationId': {'type': 'number'},
        'status': {'type': 'number'},
    },
    'required': []
}


@app.route('/devices', methods=['POST'])
@expects_json(createDeviceSchema)
def create_device():
    data = request.json
    device = Device(
        mac=data['mac'], locationId=data['locationId'], modelId=data['modelId'], status=0)
    db.session.add(device)
    db.session.commit()
    response = jsonify({'message': 'ok'})
    response.status_code = 201
    return response


@app.route('/devices/<int:id>', methods=['PUT'])
@expects_json(updateDeviceSchema)
def update_device(id):
    data = request.json
    device = Device.query.get(id)
    if device is None:
        response = jsonify({'message': 'not found'})
        response.status_code = 404
        return response
    if 'locationId' in data:
        device.locationId = data['locationId']
    if 'status' in data:
        device.status = data['status']
    db.session.commit()
    response = jsonify({'message': 'ok'})
    response.status_code = 200
    return response


@app.route('/devices/<int:id>', methods=['DELETE'])
def delete_device(id):
    device = Device.query.get(id)
    if device is None:
        response = jsonify({'message': 'not found'})
        response.status_code = 404
        return response
    db.session.delete(device)
    db.session.commit()
    response = jsonify({'message': 'ok'})
    response.status_code = 200
    return response


createLogSchema = {
    'type': 'object',
    'properties': {
        'value': {'type': 'number'},
        # ts generated on server
        'parameterId': {'type': 'number'},
        'deviceId': {'type': 'number'},
    },
    'required': []
}


@app.route('/logs', methods=['POST'])
@expects_json(createLogSchema)
def create_log():
    data = request.json
    log = Measurement(value=data['value'], parameterId=data['parameterId'],
                      deviceId=data['deviceId'], timestamp=datetime.utcnow())
    db.session.add(log)
    db.session.commit()
    response = jsonify({'message': 'ok'})
    response.status_code = 201
    return response
