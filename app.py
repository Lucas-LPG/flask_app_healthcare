# app.py
import time
from flask import Flask, render_template, request, jsonify, session
import paho.mqtt.client as mqtt
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
import flask_login
from controllers import create_app
from db import create_db
from db.connection import db, instance
from db.operations import select_db, insert_db, delete_db
from models import User, Sensor
from controllers.login import login
from controllers.sensors import sensor, sensores
from controllers.actuators import actuator


if __name__ == "__main__":
    app = create_app();
    app.config['TESTING'] = False
    app.config['SECRET_KEY'] = 'senha_forte-Lucas-puCas12'
    app.config['SQLALCHEMY_DATABASE_URI'] = instance
    db.init_app(app)
    create_db(app)
    print(select_db(app, User, (User.name == 'lucas')))
    insert_db(app, User('pucas', 'puhl', 'chefe'))
    insert_db(app, User('pucas', 'afsd', 'asdf'))
    app.register_blueprint(login, url_prefix='/')
    app.register_blueprint(sensor, url_prefix='/')
    app.register_blueprint(actuator, url_prefix='/')
    delete_db(app, Sensor, (Sensor.id == 1))
    app.run(host='0.0.0.0', port=8080, debug=True),
