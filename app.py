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
        
        db.execute("INSERT INTO log_date (entry_date) values (?)", [database_date])
        db.commit()
    
    cur = db.execute("""SELECT log_date.entry_date,
                                sum(food.protein) as protein,
                                sum(food.carbohydrates) as carbohydrates,
                                sum(food.fat) as fat,
                                sum(food.calories) as calories 
                        FROM log_date 
                        JOIN food_date ON food_date.log_date_id = log_date.id
                        JOIN food ON food.id = food_date.food_id
                        GROUP BY log_date.id
                        ORDER BY log_date.entry_date DESC""")
    results = cur.fetchall()
    date_results = []

    for i in results:
        single_date = {}

        single_date['entry_date'] = i['entry_date']
        single_date['protein'] = i['protein']
        single_date['carbohydrates'] = i['carbohydrates']
        single_date['fat'] = i['fat']
        single_date['calories'] = i['calories']

        d = datetime.strptime(str(i['entry_date']), '%Y%m%d')
        single_date['pretty_date'] = datetime.strftime(d, '%B %d, %Y') #{'entry_date': 'January 17, 2025'}

        date_results.append(single_date)
    
    
    return render_template('home.html', results=date_results)

@app.route('/view/<date>', methods=["GET", "POST"]) # date is going to be 20170520
def view(date):
    db = get_db()
    cur = db.execute('SELECT id, entry_date FROM log_date WHERE entry_date = ?', [date])
    date_result = cur.fetchone() # fetchone returns a dict instead of a list

    if request.method == "POST":
        db.execute('INSERT INTO food_date (food_id, log_date_id) values (?, ?)', [request.form['food-select'], date_result['id']])
        db.commit()

    d = datetime.strptime(str(date_result['entry_date']), "%Y%m%d")
    pretty_date = datetime.strftime(d, "%B %d, %Y") # January 17, 2025

    ### Get list of foods from DB
    food_cur = db.execute("SELECT id, name FROM food")
    food_results = food_cur.fetchall()

    log_cur = db.execute("""
                         SELECT food.name, food.protein, food.carbohydrates, food.fat, food.calories
                         FROM log_date 
                         JOIN food_date 
                         ON food_date.log_date_id = log_date.id
                         JOIN food
                         ON food.id = food_date.food_id
                         WHERE log_date.entry_date = ?""", 
                         [date])
    log_results = log_cur.fetchall()
    # [<sqlite3.Row object at 0x0000024BCB88C8B0>, <sqlite3.Row object at 0x0000024BCB88CC10>, <sqlite3.Row object at 0x0000024BCB88CA60>]
    
    totals = {
        'protein': 0,
        'carbohydrates': 0,
        'fat': 0,
        'calories': 0
    }

    for food in log_results:
        totals['protein'] += food['protein']
        totals['carbohydrates'] += food['carbohydrates']
        totals['fat'] += food['fat']
        totals['calories'] += food['calories']

    return render_template('day.html', entry_date=date_result['entry_date'],pretty_date=pretty_date, food_results=food_results, log_results=log_results, totals=totals)


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