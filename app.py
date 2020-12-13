import os
import random
from html import unescape

import bcrypt
from flask import Flask, render_template, request, session
import peewee
from playhouse.shortcuts import model_to_dict
import requests

from models import Achievements
from models import EasterEggs
from models import Leaderboard
from models import UserAchievements
from models import UserEasterEggs, Users
from models import database


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
# app.secret_key = 'secret'  # for debug mode


def get_quiz():
    r = requests.get('https://opentdb.com/api.php?amount=10&category=15&difficulty=easy&type=multiple')
    r_json = r.json()['results']
    quiz = []
    for i in range(10):
        question = r_json[i]['question']
        choices = r_json[i]['incorrect_answers']
        answer = r_json[i]['correct_answer']
        choices.append(answer)
        random.shuffle(choices)
        quiz.append({'question': question, 'choices': choices, 'answer': answer})
    return quiz


def get_without_failing(Model, query):
    """
    Credit for the following function: 
    https://stackoverflow.com/questions/37006869/
    peewee-using-model-get-with-a-default-value-instead-of-throwing-an-exception
    Profile: https://stackoverflow.com/users/5551941/wyattis
    """
    results = Model.select().where(query).limit(1)
    return results[0] if len(results) > 0 else None


def handle_common_cases(easter_egg_source):
    if easter_egg_source.startswith('pac'):
        easter_egg_source = 'pacman'
    if easter_egg_source.startswith('reggie'):
        easter_egg_source = 'reggie'
    if easter_egg_source == 'did you know gaming?':
        easter_egg_source = 'didyouknowgaming'
    if easter_egg_source == 'zelda ii':
        easter_egg_source = 'zelda 2'
    return easter_egg_source


def get_user_id(name):
    return Users.select(Users.id).where(Users.username == name).get()


def get_leaderboard_details():
    results = Leaderboard.select().order_by(Leaderboard.score.desc())
    tuples = [(result.name, result.score) for result in results] 
    return {'Scores': tuples}


def get_num_easter_eggs(user_id):
    return UserEasterEggs.select().where(UserEasterEggs.user_id == user_id).count()


def get_num_achievements(user_id):
    return UserAchievements.select().where(UserAchievements.user_id == user_id).count()


def check_for_platinum(user_id):
    num_achievements = get_num_achievements(user_id)
    if num_achievements == 6:
        update_achievement_by_id(user_id, 7)

    
def get_achievements(user_id):
    achievements = []
    results = UserAchievements.select().where(UserAchievements.user_id == user_id)
    lst = [result.achievement_id for result in results]
    for achievement in lst:
        achievement_name = achievement.achievement_name
        uri = achievement.uri
        achievements.append((achievement_name, uri))
    return (achievements)

    
def update_achievement_by_id(user_id, achievement_id):
    try:
        has_it = UserAchievements.select().where((UserAchievements.user_id == user_id) & (UserAchievements.achievement_id == achievement_id)).get()
    except peewee.DoesNotExist:
        has_it = None
    finally:
        if not has_it:
            achievement = UserAchievements(achievement_id=achievement_id, user_id=user_id)
            achievement.save()
    

"""@app.before_request
def before_request():
    db.connect(os.environ.get('DATABASE_URL'))  # for heroku 
    # database.connect()
    

@app.teardown_request
def close_db(_):
    if not database.is_closed():
        db.close()
"""

@app.route('/profile')
def show_profile():
    user_dict = {}
    user_dict['username'] = '-'
    user_dict['email'] = '-'
    user_dict['num_easter_eggs'] = '-'
    user_dict['num_achievements'] = '-'
    user_dict['Achievements'] = []
       
    if 'user' in session:
        name = session['user']
        user_id = get_user_id(name)
        user = Users.get_by_id(user_id)
    
        user_dict = model_to_dict(user)
        user_dict['num_easter_eggs'] = get_num_easter_eggs(user_id)
        user_dict['num_achievements'] = get_num_achievements(user_id)
        user_dict['Achievements'] = get_achievements(user_id)

    return render_template('profile.j2', user_dict=user_dict)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        return render_template('sign_up.j2')

    salt = bcrypt.gensalt(prefix=b'2b', rounds=10)
    unhashed_password = request.form['password'].encode('utf-8')
    hashed_password = bcrypt.hashpw(unhashed_password, salt)
    fields = {
        **request.form,
        'password': hashed_password,
    }
    user = Users(**fields)
    user.save()
    session['user'] = user.username
    session['password'] = hashed_password
    session['email'] = user.email
    message = 'Hi ' + session['user'] + ','
    return render_template('/index.j2', message=message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.j2')

    username = request.form['username']
    password = request.form['password'].encode('utf-8')
    if username is None:
        return render_template("error_page.j2", error='400', info="No username supplied")
    try:
        user = Users.select().where(Users.username == username).get()
    except peewee.DoesNotExist:
        return render_template("error_page.j2", error='404', info="user not found")
    actual_password = str(user.password).encode('utf-8')
    if not bcrypt.checkpw(password, actual_password):
        return render_template("error_page.j2", error='403', info="username and password don't match")
    
    session['user'] = user.username
    session['password'] = actual_password
    session['email'] = user.email
    message = 'Hi ' + session['user'] + ','
    return render_template('/index.j2', message=message)


@app.route('/game', methods=['GET', 'POST'])
def play_game():
    if request.method == 'GET':
        questions = get_quiz()
        q = questions[0]
        choices = [unescape(choice) for choice in q['choices']]
        fields = {
            'question': unescape(q['question']),
            'first': choices[0],
            'second': choices[1],
            'third': choices[2],
            'fourth': choices[3],
            'answer': q['answer']
        }
        session['questions'] = questions
        session['current_question'] = 1
        session['correct_answer'] = choices.index(unescape(q['answer']))
        session['score'] = 0
        return render_template('trivia_game.j2', **fields)

    questions = session.get('questions', None)
    user_answer = int(request.form['choice'])
    current_correct = (session.get("correct_answer", None))

    if user_answer == current_correct:
        session['score'] += 10
    
    session['current_question'] += 1
    if session['current_question'] <= 10:
        question_idx = session['current_question']
        q = questions[question_idx - 1]
        choices = [unescape(choice) for choice in q['choices']]
        fields = {
            'question': unescape(q['question']),
            'first': choices[0],
            'second': choices[1],
            'third': choices[2],
            'fourth': choices[3],
            'answer': unescape(q['answer'])
        }
        session['correct_answer'] = choices.index(unescape(q['answer']))
        return render_template('trivia_game.j2', **fields)

    if session['current_question'] == 11:
        if 'user' in session:
            name = session['user']
            user_id = get_user_id(name).id
            score = session['score']
            try:
                leader_board_score = Leaderboard.select().where(Leaderboard.user_id == user_id).get().score
                if score > leader_board_score:
                    query = Leaderboard.update(score=score).where(Leaderboard.user_id == user_id)
                    query.execute()
            except peewee.DoesNotExist:
                leaderboard = Leaderboard(user_id=user_id, name=name, score=score)
                leaderboard.save()
            
            achievement_id = ""
            if score <= 30:
                achievement_id = 1
            elif score >= 60 and score < 80:
                achievement_id = 2
            elif score >= 80:
                achievement_id = 3

            results = Leaderboard.select().where(Leaderboard.user_id == user_id).order_by(Leaderboard.score.desc()).limit(10).get()
            if results.user_id.id == user_id:
                update_achievement_by_id(user_id, 4)

            if achievement_id:
                update_achievement_by_id(user_id, achievement_id)

            check_for_platinum(user_id)
        return render_template('result.j2', score=session.get('score', None))


@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    if request.method == "GET":
        details = get_leaderboard_details()
        return render_template('leaderboard.j2', details=details)
    
    if 'user' in session:
        name = session['user']
        user_id = get_user_id(name)
        query = Leaderboard.delete().where(Leaderboard.user_id == user_id)
        query.execute()
    details = get_leaderboard_details()
    return render_template('leaderboard.j2', details=details)


@app.route('/easter_eggs', methods=['GET', 'POST'])
def easter_eggs():
    to_add = True
    if request.method == "GET":
        return render_template('easter_eggs.j2')
    easter_egg_source = request.form['easter_egg'].lower()
    if type(easter_egg_source) == str:
        easter_egg_source = handle_common_cases(easter_egg_source)
        _id = get_without_failing(EasterEggs, EasterEggs.name == easter_egg_source)
        if 'user' in session:
            name = session['user']
            user_id = Users.select(Users.id).where(Users.username == name).get()
            current_easter_eggs = get_without_failing(UserEasterEggs, UserEasterEggs.user_id == user_id)
            if _id:
                easter_egg_id = _id.id
                try:
                    UserEasterEggs.select().where((UserEasterEggs.user_id == user_id) & (UserEasterEggs.easter_egg_id == easter_egg_id)).get()
                    user_already_has = True
                except peewee.DoesNotExist:
                    user_already_has = False
                if current_easter_eggs:
                    if user_already_has:
                        to_add = False
                if to_add:
                    achievement_id = ""
                    user_easter_egg = UserEasterEggs(easter_egg_id=easter_egg_id, user_id=user_id.id)
                    user_easter_egg.save()
                    num_easter_eggs = get_num_easter_eggs(user_id)
                    if num_easter_eggs == 1:
                        achievement_id = 5
                    elif num_easter_eggs == 7:
                        achievement_id = 6
                    if achievement_id:
                        update_achievement_by_id(user_id, achievement_id)
                        check_for_platinum(user_id)
              
        if _id:
            result = "Nice! you found one!"
            return render_template('easter_eggs_result.j2', result=result)
        else:
            result = "Maybe next time..."
        return render_template('easter_eggs_result.j2', result=result) 


@app.route('/easter_eggs_result', methods=['GET'])
def easter_eggs_result():
    render_template('easter_eggs_result.j2')


@app.route('/')
def home_page():
    if 'user' in session:
        message = 'Hi ' + session['user'] + ',' 
    else:
        message = ""
    return render_template('index.j2', message=message)


if __name__ == '__main__':
    app.run()