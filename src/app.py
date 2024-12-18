import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from models import db
from routes import api

load_dotenv()

PATH = os.path.abspath('instance')

app = Flask(__name__, instance_path=PATH)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db.init_app(app)
Migrate(app, db)
jwt = JWTManager(app)
CORS(app)

app.register_blueprint(api, url_prefix='/api')

@app.errorhandler(400)
def page_not_found(e):
    return jsonify({ "error": "Page not found (404)", "details": e.message}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({ "error": "Internal Server Error (500)", "details": e}), 500


@app.route('/')
def main():
    return jsonify({ "status": "Server running successfully"}), 200


if __name__ == '__main__':
    app.run()