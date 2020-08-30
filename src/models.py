from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(80), unique=False, nullable=False)
#     is_active = db.Column(db.Boolean(), unique=False, nullable=False)

#     def __repr__(self):
#         return '<User %r>' % self.username

#     def serialize(self):
#         return {
#             "id": self.id,
#             "email": self.email,
#             # do not serialize the password, its a security breach
#         }


class User(db.Model):
     __tablename__="user"
     id = db.Column(db.Integer, primary_key=True)
     username = db.Column(db.String(80), unique=False, nullable=False)
     email = db.Column(db.String(120), unique=False, nullable=False)
     password = db.Column(db.String(80), unique=False, nullable=False)
     is_active = db.Column(db.Boolean(), default=False)
     portfolio = db.relationship('Portfolio', lazy='dynamic')


     def __repr__(self):
        return '<User %r>' % self.username

     def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "is_active": self.is_active,
            "portfolio": [portfolio.serialize() for portfolio in self.portfolios.all()]
            # do not serialize the password, its a security breach
        }



# class Stock(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     symbol = db.Column(db.String(120), unique=False, nullable=False)
#     companyName = db.Column(db.String(120), unique=False, nullable=False)
#     price = db.Column(db.Integer, unique=False, nullable=False)
#     # password = db.Column(db.String(80), unique=False, nullable=False)
#     is_active = db.Column(db.Boolean(), unique=False, nullable=False)

#     def __repr__(self):
#         return '<Stock %r>' % self.symbol

#     def serialize(self):
#         return {
#             "id": self.id,
#             "symbol": self.symbol,
#             "companyName":self.companyName,
#             "price":self.price
#             # do not serialize the password, its a security breach
#         }



class Portfolio(db.Model):
     __tablename__="portfolio"
     id = db.Column(db.Integer, primary_key=True)
     symbol = db.Column(db.String(120), unique=False, nullable=False)
     companyName = db.Column(db.String(120), unique=False, nullable=False)
     price = db.Column(db.Integer, unique=False, nullable=False)
     shares= db.Column(db.Integer, unique=False, nullable=False)
     totalReturn=db.Column(db.Integer, unique=False, nullable=False)
    # password = db.Column(db.String(80), unique=False, nullable=False)
     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
     user = db.relationship('User')
     def __repr__(self):
        return '<Portfolio %r>' % self.companyName

     def serialize(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "companyName":self.companyName,
            "price":self.price,
            "shares":self.shares,
            "totalReturn":self.totalReturn
           
        }