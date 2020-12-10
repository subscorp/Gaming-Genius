import sqlite3

import models


def connect():
    return sqlite3.connect("trivia_game.db")


def create_tables(db):
    TABLES = [
        models.Users, models.Achievements, models.EasterEggs, models.Leaderboard, models.UserAchievements,
        models.UserEasterEggs,
    ]

    with models.database.connection_context():
        models.database.create_tables(TABLES, safe=True)
        models.database.commit()


def insert_into(db, query, values):
    cursor = db.cursor()
    cursor.execute(query, values)
    db.commit()


def insert_into_users(db, values):
    query = f"INSERT INTO users (username, password, email) VALUES (?, ?, ?)"
    insert_into(db, query, values)


def insert_into_achievements(db, values):
    query = f"INSERT INTO achievements (achievement_name, uri) VALUES (?, ?)"
    insert_into(db, query, values)


def insert_into_easter_eggs(db, values):
    query = f"INSERT INTO easter_eggs (name) VALUES (?)"
    insert_into(db, query, values)


def insert_into_leaderboard(db, values):
    query = f"INSERT INTO leaderboard (name, score) VALUES (?, ?)"
    insert_into(db, query, values)


def insert_into_user_achievements(db, values):
    query = f"INSERT INTO user_achievements (user_id, achievement_id) VALUES (?, ?)"
    insert_into(db, query, values)


def insert_into_user_easter_eggs(db, values):
    query = f"INSERT INTO user_easter_eggs (user_id, easter_egg_id) VALUES (?, ?)"
    insert_into(db, query, values)


def delete_by_id(db, table_name, _id):
    c = db.cursor()
    c.execute(f"DELETE FROM {table_name} WHERE rowid = (?)", _id)
    db.commit()
    db.close()


def delete_multiple(db, table_name, List):
    c = db.cursor()
    c.execute(f"DELETE FROM {table_name} WHERE rowid in {List}")
    db.commit()
    db.close()


def print_all(db, table_name):
    c = db.cursor()
    c.execute(f"SELECT rowid, * FROM {table_name}")
    items = c.fetchall()
    for item in items:
        print(item)
    db.commit()
    db.close()


def search_by_username(db, username):
    c = db.cursor()
    c.execute("SELECT rowid, * FROM users WHERE username = (?)", (username,))
    users = c.fetchall()
    for user in users:
        print(user)
    db.commit()
    db.close()


def fill_easter_eggs(db):
    names = ['didyouknowgaming?', 'reggie', 'pacman', 'nintendo power', 'portal', 'zelda 2', 'star fox']
    for name in names:
        insert_into_easter_eggs(db, (name,))


def fill_achievements(db):
    names = (
        ("That's what you get for guessing...", '../static/guess.jpg'),
        ("That's just ok..", "../static/pass.jpg"),
        ('Excellent! you must be cheating...', "../static/crash.jpg"),
        ("Top of the game!", "../static/top_ten.jpg"),
        ("First easter egg! gotta catch 'em all!", "../static/addict.jpg"),
        ('Easter egg hunter!', "../static/hunter.jpg"),
        ("Completionist!", "../static/Completionist.jpg")
    )
    for name in names:
        insert_into_achievements(db, name)