from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_sqlalchemy import SQLAlchemy
import logging
import pymysql
from sqlalchemy.exc import IntegrityError
import mysql.connector
import re
from flask import render_template

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:MyN3wP4ssw0rd@localhost/classifier_db?charset=utf8mb4'
app.config['SECRET_KEY'] = 'superstructure'
app.config['JWT_SECRET_KEY'] = 'superstructure'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
# https://juncotic.com/autenticacion-con-jwt-en-flask/
# https://www.freecodecamp.org/news/jwt-authentication-in-flask/
db = SQLAlchemy(app)
jwt = JWTManager(app)

logging.basicConfig(filename='api.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')


class DatabaseConnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    database_name = db.Column(db.String(255), nullable=False)


class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    database_id = db.Column(db.Integer, db.ForeignKey('database_connection.id'), nullable=False)
    table_name = db.Column(db.String(255), nullable=False)
    column_name = db.Column(db.String(255), nullable=False)
    information_type = db.Column(db.String(255), nullable=True)
    data_type = db.Column(db.String(255), nullable=False)


@app.errorhandler(Exception)
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
def scan_summary(id):
    try:
        scan_data = {
            "database_connection": [
                {"column_name": "id", "data_type": "int(11)", "information_type": "default_match"},
                {"column_name": "host", "data_type": "varchar(255)", "information_type": "default_match"},
                {"column_name": "port", "data_type": "int(11)", "information_type": "default_match"},
                {"column_name": "username", "data_type": "varchar(255)", "information_type": "default_match"},
                {"column_name": "password", "data_type": "varchar(255)", "information_type": "default_match"},
                {"column_name": "database_name", "data_type": "varchar(255)", "information_type": "default_match"}
            ],
            "scan_result": [
                {"column_name": "id", "data_type": "int(11)", "information_type": "default_match"},
                {"column_name": "database_id", "data_type": "int(11)", "information_type": "default_match"},
                {"column_name": "table_name", "data_type": "varchar(255)", "information_type": "default_match"},
                {"column_name": "column_name", "data_type": "varchar(255)", "information_type": "default_match"},
                {"column_name": "information_type", "data_type": "varchar(255)", "information_type": "default_match"},
                {"column_name": "data_type", "data_type": "varchar(255)", "information_type": "default_match"}
            ],
            "user": [
                {"column_name": "id", "data_type": "int(11)", "information_type": "default_match"},
                {"column_name": "username", "data_type": "varchar(80)", "information_type": "default_match"},
                {"column_name": "password", "data_type": "varchar(120)", "information_type": "default_match"},
                {"column_name": "role", "data_type": "varchar(50)", "information_type": "default_match"}
            ]
        }
        total_tables = len(scan_data)
        sensitive_columns_count = sum(
            len([col for col in columns if col["information_type"] != "default_match"])
            for columns in scan_data.values()
        )
        return render_template('scan_summary.html',
                               total_tables=total_tables,
                               sensitive_columns_count=sensitive_columns_count,
                               scan_data=scan_data)
    except Exception as e:
        return jsonify({"error": "SummaryError", "message": str(e)}), 500


@app.route('/api/v1/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username and password are required"}), 400

        new_user = User(username=data['username'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully', 'user_id': new_user.id}), 201
    except IntegrityError:
        return jsonify({"error": "IntegrityError", "message": "Username already exists."}), 400


@app.route('/api/v1/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or user.password != data['password']:
        logging.warning(f'Failed login attempt for user: {data["username"]}')
        return jsonify({'message': 'Login failed! Check your credentials'}), 401

    access_token = create_access_token(identity=user.username)
    logging.info(f'User {user.username} logged in successfully')
    return jsonify({'access_token': access_token}), 200


@app.route('/api/v1/database', methods=['POST'])
@jwt_required()
def add_database():
    try:
        data = request.get_json()
        if not data or not data.get('host') or not data.get('password') or not data.get('username'):
            return jsonify({"error": "Host, username, and password are required"}), 400

        new_db = DatabaseConnection(
            host=data['host'],
            port=data['port'],
            username=data['username'],
            password=data['password'],
            database_name=data['database_name']
        )
        db.session.add(new_db)
        db.session.commit()
        return jsonify({"id": new_db.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "IntegrityError", "message": "Failed to add database."}), 400


@app.route('/api/v1/database/scan/<int:id>', methods=['POST'])
@jwt_required()
def scan_database(id):
    try:
        connection = db.session.get(DatabaseConnection, id)
        if not connection:
            return jsonify({"error": "Database connection not found"}), 404

        db_conn = mysql.connector.connect(
            host=connection.host,
            user=connection.username,
            password=connection.password,
            port=connection.port,
            database=connection.database_name
        )
        cursor = db_conn.cursor()
        logging.info(f"Connected to database: {connection.database_name}")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        if not tables:
            logging.warning("No tables found in the database")
            return jsonify({"error": "No tables found in the database"}), 404

        logging.info(f"Tables fetched from database: {[table[0] for table in tables]}")

        table_column_data = {}

        sensitive_columns = []
        sensitive_patterns = {
            'default_match': r'.*'
        }
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = cursor.fetchall()
            logging.info(f"Columns in table {table_name}: {columns}")

            table_column_data[table_name] = [column[0] for column in columns]

            for column in columns:
                column_name = column[0]
                data_type = column[1]
                information_type = None

                for info_type, pattern in sensitive_patterns.items():
                    if re.match(pattern, column_name, re.IGNORECASE):
                        information_type = 'default_match'

                if information_type:
                    logging.info(f"Sensitive column found: {column_name} (Type: {information_type})")

                    existing_result = ScanResult.query.filter_by(
                        database_id=id,
                        table_name=table_name,
                        column_name=column_name
                    ).first()

                    if existing_result:
                        existing_result.information_type = information_type
                    else:
                        result = ScanResult(
                            database_id=id,
                            table_name=table_name,
                            column_name=column_name,
                            information_type=information_type,
                            data_type=data_type
                        )
                        db.session.add(result)

                    sensitive_columns.append({
                        "table_name": table_name,
                        "column_name": column_name,
                        "data_type": data_type,
                        "information_type": information_type
                    })

        db.session.commit()

        cursor.close()
        db_conn.close()

        if sensitive_columns:
            logging.info(f"Sensitive columns found: {sensitive_columns}")
        else:
            logging.warning("No sensitive columns found in the database scan")

        return jsonify({
            "message": "Scan completed",
            "sensitive_columns": sensitive_columns,
            "all_columns": table_column_data
        }), 201

    except mysql.connector.Error as db_err:
        logging.error(f"DatabaseError: {str(db_err)}")
        return jsonify({"error": "DatabaseError", "message": f"MySQL error: {str(db_err)}"}), 500
    except Exception as e:
        logging.error(f"UnhandledError during scan: {str(e)}")
        return jsonify({"error": "ScanError", "message": f"Unhandled error: {str(e)}"}), 500


@app.route('/api/v1/database/scan/<int:id>', methods=['GET'])
@jwt_required()
def get_scan_results(id):
    try:
        results = ScanResult.query.filter_by(database_id=id).all()
        if not results:
            return jsonify({"error": "No scan results found"}), 404
        scan_data = {}
        for result in results:
            if result.table_name not in scan_data:
                scan_data[result.table_name] = []
            scan_data[result.table_name].append({
                "column_name": result.column_name,
                "data_type": result.data_type,
                "information_type": result.information_type
            })
        return jsonify(scan_data), 200
    except Exception as e:
        return jsonify({"error": "FetchError", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
