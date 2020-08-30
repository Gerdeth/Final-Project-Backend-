"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User,Portfolio
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def get_all_user():
    users_query = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users_query))

    return jsonify({
        "message": "These are all the available users",
        "users": all_users
    }),200
@app.route('/login', methods=['POST'])
def handle_login():
    request_data=request.get_json()
    users_query = User.query.filter_by(email=request_data["email"]).first()
    if users_query != None :
        return jsonify(users_query.serialize()), 200 
    return  jsonify({"Message":"User not found"})

@app.route('/register_user', methods=['POST'])
def handle_register_user():
    request_data= request.get_json()
    user=User.query.filter_by(username=request_data['username']).first()
    if user:
        return jsonify({'message': 'username already exists'}), 409
    new_user = User(
        username=request_data["username"],
        email=request_data["email"], 
        password=request_data["password"],
        is_active=True
        )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        "msg": "User was created "
    }),200
    

@app.route('/portfolio/<user_id>', methods=['GET'])
def get_portfolio():
    user_portfolio= Portfolio.query.filter_by(id=id).first()
    if user_portfolio != None:
        return jsonify(user_portfolio.serialize())
    return jsonify({"message": "Add stocks to your portfolio"})
        

@app.route('/portfolio/<user_id>', methods=['POST'])
def post_portfolio(user_id):
    request_data= request.get_json()
    stock_added={
        "symbol":request_data["symbol"],
        "companyName":request_data["companyName"],
        "price": request_data["price"],
        "shares": request_data["shares"],
        "totalReturn":request_data["totalReturn"]
       
        }
    db.session.add(stock_added)
    db.session.commit()
    response_body = {
        "msg": "Stock Added "
    }

    return jsonify(response_body), 200

@app.route('/portfolio/<user_id>', methods=['DELETE'])
def handle_portfolio(id):
    stock_sold= Portfolio.query.filter_by(id=id).first()
    if stock_sold != None:
        db.session.delete(stock_sold)
        db.session.commit()
        response_body = {
            "msg": "Stock Sold "
        }
        return jsonify(response_body), 200
    return jsonify({"message":"Stock not found" })


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
