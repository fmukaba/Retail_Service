from flask import Flask, flash, render_template, request, redirect, session
from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy

#flask setup
app = Flask(__name__) 
app.jinja_env.globals.update(zip=zip)
# set db with sqlalchemy and sqlite
app.config["SECRET_KEY"] = '571ebf8e13ca209536c29be68d435c00'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///retail.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import *

# db.drop_all()
db.create_all()
# run once
# populate_db()

# routes 
@app.route('/')
def index():
    return redirect('/home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        session['username'] = request.form.get('username')
        return redirect('/home')

@app.route('/home')  
def home():
    if session.get('username') != None:
        items = Item.query.all()
        return render_template('home.html', data=items, user=session['username'])
    else:
        return redirect('/login')

@app.route('/show/<int:item_id>', methods=['GET', 'POST'])  
def show(item_id):
    if session.get('username') != None:
        if request.method == 'GET':
            item = Item.query.get(item_id)
            item_type = Type.query.get(item.type_id)
            return render_template('show.html', item=item, item_type=item_type)
        else:
            # add order to cart
            item = Item.query.get(item_id)
            qty = request.form.get('qty')
            total = int(qty) * item.unit_price
            order = Orders(quantity=qty, item_id=item_id, total_price=total, user = session['username'])
            db.session.add(order)
            db.session.commit()
            return redirect('/home')
            
    else:
        return redirect('/login')

@app.route('/cart', methods=['GET', 'POST'])  
def cart():
    if session.get('username') != None:
        if request.method == 'GET':
            # load orders to cart
            orders = Orders.query.filter_by(user=session['username'], transaction_id=None) # get all order of username whose transaction_id is Null (Not yet processed)
            item_names = []
            for o in orders:
                name = Item.query.get(o.item_id).name
                item_names.append(name)
            return render_template('cart.html', data=orders, names=item_names, user=session['username'])
        else:
            # process transaction
            orders = Orders.query.filter_by(user=session['username'], transaction_id=None)
            final_amount = 0
            for o in orders:
                final_amount = final_amount + o.total_price
            transaction = Transactions(date=date.today(), user=session['username'], final_amount=final_amount,)
            db.session.add(transaction)
            db.session.commit()
            for o in orders:
                o.transaction_id = transaction.id
            db.session.commit()
            flash("You order is on its way !")
            return redirect('/home')
    else:
        return redirect('/login')

@app.route('/admin', methods=['GET', 'POST'])  
def admin():
    if session.get('username') == "admin":
        # query db for all orders made today grouped by user
        # engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        # db.create_engine() ?
        preparedStatement1 = "SELECT item.name, orders.quantity, orders.total_price, transactions.user"
        preparedStatement1 += " FROM item join orders ON item.id = orders.item_id" 
        preparedStatement1 += " JOIN transactions on transactions.id = transaction_id"
        preparedStatement1 += " WHERE transactions.date = '" + str(date.today()) + "' and orders.transaction_id is not null " 
        preparedStatement1 += " GROUP BY transactions.user, item.name, orders.quantity, orders.total_price"
        result = db.create_engine(app.config['SQLALCHEMY_DATABASE_URI'],{}).connect().execute(preparedStatement1).fetchall()
        if request.method == 'GET':
            return render_template('admin.html', data=result)
        else:
            username = request.form.get('user')
            amount = request.form.get('amount')
            preparedStatement2 = "SELECT transactions.date, transactions.final_amount, transactions.user"
            preparedStatement2 += " FROM transactions" 
            preparedStatement2 += " WHERE transactions.user = '" + username + "' and transactions.final_amount > " + amount
            preparedStatement2 += " ORDER BY transactions.date LIMIT 5"
            filtered =db.create_engine(app.config['SQLALCHEMY_DATABASE_URI'], {}).connect().execute(preparedStatement2).fetchall()
            return render_template('admin.html', data=result, filtered=filtered) 
    else:
        return redirect('/home')
   
# every path leads to [r]home
@app.route('/<path:path>')
def catch_all(path):
    # send an error message or render 404
    return redirect('/') 

@app.route('/logout')  
def logout():
    if session.get('username') != None:
        session.pop('username')     
    return redirect('/login')

if __name__ == "__main__":
    app.run()