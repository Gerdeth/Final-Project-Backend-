import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User,Portfolio, Transaction
import datetime
from flask import Flask, jsonify, request
from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt_identity
)

#from models import Person
app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
# Setup the Flask-JWT-Simple extension
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)
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
    return jsonify(all_users), 200

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    params = request.get_json()
    username = params.get('username', None)
    password = params.get('password', None)

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    usercheck = User.query.filter_by(username=username, password=password).first()
    if usercheck == None:
      return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    ret = {'jwt': create_jwt(identity=username), 'user': usercheck.serialize()}
    return jsonify(ret), 200
# @app.route('/login', methods=['POST'])
# def handle_login():
#     request_data=request.get_json()
#     users_query = User.query.filter_by(email=request_data["email"]).first()
#     if users_query:
#         return jsonify(users_query.serialize()), 200 
#     return  jsonify({"Message":"User not found"})

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
        buying_power=request_data["buying_power"],
        is_active=True
        )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        "msg": "User was created "
    }),200

@app.route('/portfolio/<id>', methods=['GET'])
def get_portfolio(id):
    user_portfolios = Portfolio.query.filter_by(user_id=id).all()
    if user_portfolios:        
        return jsonify([portfolio.serialize() for portfolio in user_portfolios])
    return jsonify([])

@app.route('/portfolio/<user_id>', methods=['POST'])
def buy_stock(user_id):

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify ({"Message":"No user found"})

    request_data = request.get_json()
    stock = Portfolio.query.filter_by(companyName=request_data["companyName"]).filter_by(user_id=user_id).first()
    x = datetime.datetime.now()
    new_transaction = Transaction(
        user_id=user_id,
        transactionName="buy", 
        symbol=request_data["symbol"],
        price=request_data["price"],
        shares=request_data["shares"],
        date= str(x.strftime("%x"))
        )
    if user.buying_power < request_data["price"]*request_data["shares"]:
        return jsonify({"message":"insufficient funds"})
    if stock:
        user.buying_power-=request_data["price"]*request_data["shares"]
        stock.shares += request_data["shares"]
        db.session.add(new_transaction)
        db.session.add(stock)
        db.session.commit()    
        return jsonify ({"Message":"shares updated"})
    stock_added = Portfolio(
        symbol=request_data["symbol"],
        companyName=request_data["companyName"],
        price= request_data["price"],
        shares= request_data["shares"],
        user_id=user_id
    )
    user.buying_power-=request_data["price"]*request_data["shares"]
    db.session.add(new_transaction)
    db.session.add(stock_added)
    db.session.commit() 
    return jsonify({"message":"new stock created "}), 200

@app.route('/portfolio/<user_id>', methods=['PUT'])
def sell_stock(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message":"Not a valid user ID"})
    request_data = request.get_json()
    stock = Portfolio.query.filter_by(symbol=request_data["symbol"]).filter_by(user_id=user_id).first()
    if not stock:
        return jsonify({"Message":"This user has no stocks","Stocks":stock})
    if stock.shares< request_data["shares"]:
        return jsonify({"message":"not enough stock"})    
    stock.shares -= request_data["shares"]
    user.buying_power += request_data["price"]*request_data["shares"]
    x = datetime.datetime.now()
    new_transaction = Transaction(
        user_id=user_id,
        transactionName="sell", 
        price= request_data["price"],
        shares= request_data["shares"],
        symbol=stock.symbol,
        date= str(x.strftime("%x"))
        )
    if stock.shares :
        db.session.add(new_transaction)
        db.session.commit() 
        return jsonify ({"Message":"stock sold"})
    db.session.add(new_transaction)
    db.session.delete(stock)
    db.session.commit() 
    return jsonify ({"Message":"stock sold"})


@app.route('/transactions/<user_id>', methods=['GET'])
def get_transactions(id):
    transactions=Transaction.query.filter_by(user_id=id)
    transactions = list(map(lambda x: x.serialize(), transactions))
    return jsonify(transactions), 200




    
# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

