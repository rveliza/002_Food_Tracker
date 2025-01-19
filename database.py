from flask import g
import sqlite3

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