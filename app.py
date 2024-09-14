from flask import Flask

app = Flask(__name__)

@app.errorhandler(Exception)
def handle_global_error():


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
