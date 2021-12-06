from app import db

class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(25), nullable=False)
    name = db.Column(db.String(50), nullable=False)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    unit_price = db.Column(db.Integer)
    stock = db.Column(db.Integer)
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'),
        nullable=False)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.Integer)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'),
        nullable=True)  
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'),
        nullable=False)  
    user= db.Column(db.String(80))

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    user = db.Column(db.String(80))
    final_amount = db.Column(db.Integer)
    orders = db.relationship('Orders', backref='transactions', lazy=True)

# prepopulate db with items and item types
def populate_db():
    # item type
    shoes1 = Type(color="black", name="shoes")
    shoes2 = Type(color="white", name="shoes")
    socks1 = Type(color="black", name="socks")
    socks2 = Type(color="white", name="socks")
    # items
    item1 = Item(name= "Nike KD 14", unit_price=150, stock=30, type_id=1)
    item2 = Item(name= "Nike PG 5", unit_price=110, stock=100, type_id=2)
    item3 = Item(name= "Adidas Dame 5", unit_price=100, stock=95, type_id=1)
    item4 = Item(name= "UA Curry 8", unit_price=160, stock=20, type_id=2)
    item5 = Item(name= "Nike socks", unit_price=5, stock=200, type_id=3)
    item6 = Item(name= "Adidas socks", unit_price=3, stock=200, type_id=4)
    
    db.session.add(shoes1)
    db.session.add(shoes2)
    db.session.add(socks1)
    db.session.add(socks2)
    db.session.add(item1)
    db.session.add(item2)
    db.session.add(item3)
    db.session.add(item4)
    db.session.add(item5)
    db.session.add(item6)

    db.session.commit()
 