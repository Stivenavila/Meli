from flask import Flask, jsonify
from flask_jwt_extended import jwt_required
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:MyN3wP4ssw0rd@localhost/classifier_db?charset=utf8mb4'

db = SQLAlchemy(app)
class DatabaseConnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    database_name = db.Column(db.String(255), nullable=False)

@app.errorhandler(Exception)
# https://flask.palletsprojects.com/en/2.3.x/errorhandling/
def handle_global_error(error):
    code = 500
    if isinstance(error, IntegrityError):
        code = 400
        db.session.rollback()
        return jsonify({"error": "IntegrityError", "message": str(error.orig)}), code
    if isinstance(error, KeyError):
        code = 400
        return jsonify({"error": "KeyError", "message": str(error)}), code
    return jsonify({"error": "ServerError", "message": str(error)}), code


@app.route('/api/v1/database/scan/<int:id>/summary', methods=['GET'])
@jwt_required()
def scan_summary():


@app.route('/api/v1/register', methods=['POST'])
def register():


@app.route('/api/v1/login', methods=['POST'])
def login():


@app.route('/api/v1/database', methods=['POST'])
@jwt_required()
def add_database():


@app.route('/api/v1/database/scan/<int:id>', methods=['POST'])
@jwt_required()
def scan_database(id):


@app.route('/api/v1/database/scan/<int:id>', methods=['GET'])
@jwt_required()
def get_scan_results():


if __name__ == '__main__':
    app.run(debug=True)
