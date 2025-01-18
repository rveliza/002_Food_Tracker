from flask import Flask, render_template, g, request
from datetime import datetime
import sqlite3

app = Flask(__name__)

def connect_db():
    # "Connect to the actual db file"
    sql= sqlite3.connect('food_log.db')
    sql.row_factory = sqlite3.Row # Results will be returned as dictionaries instead of tuples
    return sql

def get_db():
    # "Check global object g if sqlite3_db exists"
    if not hasattr(g, 'sqlite3_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/',methods=["GET", "POST"])
def index():
    db = get_db()
    if request.method == "POST":
        date = request.form['date'] # 2025-01-17 <class 'str'>
        dt = datetime.strptime(date, '%Y-%m-%d') # <class 'datetime.datetime'>
        database_date = datetime.strftime(dt, '%Y%m%d') # <class 'str'>
        pretty_date = datetime.strftime(dt, '%B %d, %Y')
        
        db.execute("INSERT INTO log_date (entry_date) values (?)", [database_date])
        db.commit()
    
    return render_template('home.html')

@app.route('/view')
def view():
    return render_template('day.html')

@app.route('/food', methods=["GET", "POST"])
def food():
    db = get_db()
    if request.method == "POST":
        name = request.form['food-name']
        protein = int(request.form['protein'])
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])
        
        calories = protein * 4 + carbohydrates * 4 + fat * 9
        
        
        db.execute('INSERT INTO food (name, protein, carbohydrates, fat, calories) values (?, ?, ?, ?, ?)', [name, protein, carbohydrates, fat, calories])
        db.commit()


    cur = db.execute('SELECT * FROM food')
    results = cur.fetchall()
    
    return render_template('add_food.html', results=results)


if __name__ == "__main__":
    app.run(debug=True)