import requests
import ssl
import smtplib
import random
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
from flask import Flask, render_template, request,jsonify,session,g,redirect,url_for,flash
from flask_caching import Cache
import redis
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
from flask_bcrypt import Bcrypt 
from functools import wraps
from flask_oauthlib.client import OAuth
import secrets
# from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
app.secret_key = 'tef'
app.config['DATABASE'] = 'pokemon.db'
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 465
EMAIL_ADDRESS = 'zhenya.lember@mail.ru'
EMAIL_PASSWORD = 'STFdVAVjVKmjexRN4gsA'
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_KEY_PREFIX'] = 'pokemon_cache'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 0
# metrics = PrometheusMetrics(app)
cache = Cache(app)
oauth = OAuth(app)
vk = oauth.remote_app(
    'vk',
    consumer_key='51805289',
    consumer_secret='ym2I5aN7qLmJsApFScl3',
    request_token_params={'scope': 'email'},
    base_url='https://login.vk.ru/',
    authorize_url='https://oauth.vk.ru/authorize',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://oauth.vk.ru/token',
)
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped_view

def send_email(message, to_email):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = 'результат битвы покемонов'
        msg.attach(MIMEText(message, 'plain'))
        print(msg.as_string())
        server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT)
        print('starttls')
        time.sleep(5)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print('login')
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        print('sended')
        server.quit()
    except Exception as e:
        print("Error", str(e))
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()
def insert_battle_result(player_name,computer_name,outcome,user_id,rounds):
    db = get_db()
    db.execute('INSERT INTO battle_results (player_name,computer_name, outcome,user_id,rounds,battle_date) VALUES (?, ?, ?,?,?,CURRENT_TIMESTAMP)',
               [player_name,computer_name,outcome,user_id,rounds])
    db.commit()

@app.route('/cache-info', methods=['GET'])
@login_required
def cache_info():
    cache_data = {}

    # Connect to the Redis server
    redis_conn = redis.StrictRedis(host='localhost', port=6379, db=0)

    # Fetch all keys using the KEYS command (Note: KEYS can be resource-intensive)
    all_keys = redis_conn.keys('*')

    # Fetch values for each key
    for key in all_keys:
        value = redis_conn.get(key)
        cache_data[key.decode('utf-8', errors='replace')] = value.decode('utf-8', errors='replace') if value else None

    return jsonify(cache_data)

def main(page):
    offset = (page - 1) * 20
    @cache.memoize(timeout=300) 
    def fetch_pokemon_data(url,**params):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('results', [])
        else:
            print(f"{response.status_code}")

    # print('program going forward2')
    url = f'https://pokeapi.co/api/v2/pokemon/?limit=20&offset={offset}'
    pokemons_list = fetch_pokemon_data(url)
    response = requests.get(url)
    if response.status_code == 200:
        pokemon_list = []
        answer_data = response.json()
        pokemons_list = answer_data.get('results', [])
        for i, pokemon in enumerate(pokemons_list, start=1):
            current_pokemon_data = requests.get(
                f'https://pokeapi.co/api/v2/pokemon/{i+offset}/').json()
            health = current_pokemon_data.get('stats', [])[0]['base_stat']
            attack = current_pokemon_data.get('stats', [])[1]['base_stat']
            image = current_pokemon_data.get('sprites', {}).get('front_default', '')
            print(image)
            pokemon_info = {
                "id": i,
                "name": pokemon['name'],
                "health": health,
                "attack": attack,
                "pokemon_image": image
            }
            pokemon_list.append(pokemon_info)
        return pokemon_list
    else:
        print(f"{response.status_code}")

@app.route("/", methods=["GET", "POST"])
@login_required
def choosing():
    outcome_message = ""
    page = request.args.get('page', 1, type=int)
    if request.method == "POST":
        choice = request.form["choice"]
        print(choice)
        try:
            player_pokemon = int(choice)
            if 0 < player_pokemon < 20:
                current_pokemon_data = requests.get(f'https://pokeapi.co/api/v2/pokemon/{player_pokemon}/').json()
                health = current_pokemon_data.get('stats', [])[0]['base_stat']
                name = current_pokemon_data['name']
                attack = current_pokemon_data.get('stats', [])[1]['base_stat']
                defence = current_pokemon_data.get('stats', [])[2]['base_stat']
                speed = current_pokemon_data.get('stats', [])[4]['base_stat']
                special_attack = current_pokemon_data.get('stats', [])[3]['base_stat']
                special_attack_points = current_pokemon_data.get('stats', [])[3]['effort']
                image = current_pokemon_data.get('sprites', {}).get('front_default', '')
                computer_pokemon = random.randint(1, 20)
                while player_pokemon == computer_pokemon:
                    computer_pokemon = random.randint(1, 20)

                computer_pokemon_data = requests.get(f'https://pokeapi.co/api/v2/pokemon/{computer_pokemon}/').json()
                c_hp_left = computer_pokemon_data.get('stats', [])[0]['base_stat']
                p_hp_left = health
                c_att = computer_pokemon_data.get('stats', [])[1]['base_stat']
                p_att = attack
                c_def = computer_pokemon_data.get('stats', [])[2]['base_stat']
                p_def = defence

                session['round_number'] = 1
                session['player_pokemon'] = player_pokemon
                session['computer_pokemon'] = computer_pokemon
                session['player_health'] = p_hp_left
                session['computer_health'] = c_hp_left
                session['player_damage'] = p_att
                session['computer_damage'] = c_att
                session['player_def'] = p_def
                session['computer_def'] = c_def
                print(choice)
                return render_template('pokemon.html', i=player_pokemon, name=name, health=health, attack=attack, 
                                       defence=defence, speed=speed, special_attack=special_attack,
                                       special_attack_points=special_attack_points, 
                                       player_health=p_hp_left, computer_health=c_hp_left, computer_def=c_def,
                                       outcome_message=outcome_message,image = image)
            else:
                return "Invalid choice"
        except ValueError:
            pass
    else:
        cached_pokemon_list = cache.get(f'pokemon_list_{page}')
        if cached_pokemon_list:
            pokemon_list = cached_pokemon_list
        else:
            pokemon_list = main(page)
        cache.set(f'pokemon_list_{page}', pokemon_list)
        print('something')
        return render_template('index.html', pokemon_list=pokemon_list, outcome_message=outcome_message,page=page)

@app.route("/qbattle", methods = ["POST"])
#@login_required
def qbattle():
    if request.method == "POST":
        player_choice = random.randint(1,10)
        computer_choice = random.randint(1, 10)
        player_pokemon = session.get("player_pokemon")
        cached_pokemon_info = cache.get(f'pokemon_{player_pokemon}')
        if cached_pokemon_info:
            current_pokemon_data = cached_pokemon_info
        else:
            current_pokemon_data=requests.get(f'https://pokeapi.co/api/v2/pokemon/{player_pokemon}/').json()
        cache.set(f'pokemon_{player_pokemon}', current_pokemon_data)
        cached_pokemon_info = cache.get(f'pokemon_{session.get("computer_pokemon")}')
        if cached_pokemon_info:
            computer_data = cached_pokemon_info
        else:
            computer_data = requests.get(f'https://pokeapi.co/api/v2/pokemon/{session.get("computer_pokemon")}/').json()
        cache.set(f'pokemon_{player_pokemon}', current_pokemon_data)
        cache.set(f'pokemon_{player_pokemon}', computer_data)
        player_health = session.get('player_health')
        computer_health = session.get('computer_health')
        player_def = session.get('player_def')
        computer_def = session.get('computer_def')
        health = current_pokemon_data.get('stats', [])[0]['base_stat']
        name = current_pokemon_data['name']
        attack = current_pokemon_data.get('stats', [])[1]['base_stat']
        defence = current_pokemon_data.get('stats', [])[2]['base_stat']
        speed = current_pokemon_data.get('stats', [])[4]['base_stat']
        special_attack = current_pokemon_data.get('stats', [])[
                    3]['base_stat']
        special_attack_points = current_pokemon_data.get('stats', [])[
                    3]['effort']
        new_computer_health = session.get('computer_health')
        new_player_health = session.get('player_health')
        computer_attack = session.get('computer_damage')
        player_attack = session.get('player_damage')
        computer_attack = session.get('computer_damage')
        while(True):
            new_computer_health = session.get('computer_health')
            new_player_health = session.get('player_health')
            player_choice = random.randint(1, 10)
            computer_choice = random.randint(1, 10)
            is_even_round = (player_choice + computer_choice) % 2 == 0
            if(is_even_round):
                player_attack = session.get('player_damage')
                computer_attack = session.get('computer_damage')
                new_computer_health = computer_health - max(10, (player_attack-0.5*computer_def))
            else:
                computer_attack = session.get('computer_damage')
                player_attack = session.get('player_damage')
                new_player_health = player_health - max(10,(computer_attack -0.5*player_def))
            session['player_health'] = new_player_health
            session['computer_health'] = new_computer_health
            if new_player_health <= 0:
                insert_battle_result(current_pokemon_data['name'],computer_data['name'], "Defeat",get_current_id(),session.get('round_number'))
                outcome_message = 'Defeat'
                rec_mail = 'tefferino@gmail.com'
                mail_message = current_pokemon_data['name'] +'\n'+ computer_data['name'] + '\n'+outcome_message
                send_email(mail_message,rec_mail)
                return render_template('pokemon.html', i=player_pokemon, name=name, health=health, attack=attack, defence=defence, speed=speed, special_attack=special_attack, special_attack_points=special_attack_points, player_choice=player_choice, computer_choice=computer_choice, player_attack=player_attack, computer_attack=computer_attack, player_health=new_player_health, computer_health=new_computer_health,computer_def = computer_def,outcome_message = outcome_message)
            elif new_computer_health <= 0:
                insert_battle_result(current_pokemon_data['name'],computer_data['name'], "Win",get_current_id(),session.get('round_number'))
                outcome_message = 'Win'
                rec_mail = 'tefferino@gmail.com'
                mail_message = current_pokemon_data['name'] +'\n'+ computer_data['name'] + '\n'+outcome_message
                send_email(mail_message,rec_mail)
                return render_template('pokemon.html', i=player_pokemon, name=name, health=health, attack=attack, defence=defence, speed=speed, special_attack=special_attack, special_attack_points=special_attack_points, player_choice=player_choice, computer_choice=computer_choice, player_attack=player_attack, computer_attack=computer_attack, player_health=new_player_health, computer_health=new_computer_health,computer_def = computer_def,outcome_message = outcome_message)
    return "Invalid request method."
@app.route("/battle", methods=["POST"])
#@login_required
def battle():
    if request.method == "POST":
        player_choice = int(request.form["player_choice"])
        computer_choice = random.randint(1, 10)
        player_pokemon = session.get("player_pokemon")

        cached_pokemon_info = cache.get(f'pokemon_{player_pokemon}')
        if cached_pokemon_info:
            current_pokemon_data = cached_pokemon_info
        else:
            current_pokemon_data=requests.get(f'https://pokeapi.co/api/v2/pokemon/{player_pokemon}/').json()
        cache.set(f'pokemon_{player_pokemon}', current_pokemon_data)
        cached_pokemon_info = cache.get(f'pokemon_{session.get("computer_pokemon")}')
        if cached_pokemon_info:
            computer_data = cached_pokemon_info
        else:
            computer_data = requests.get(f'https://pokeapi.co/api/v2/pokemon/{session.get("computer_pokemon")}/').json()
        cache.set(f'pokemon_{player_pokemon}', current_pokemon_data)
        cache.set(f'pokemon_{player_pokemon}', computer_data)
        player_health = session.get('player_health')
        computer_health = session.get('computer_health')
        player_def = session.get('player_def')
        computer_def = session.get('computer_def')
        health = current_pokemon_data.get('stats', [])[0]['base_stat']
        name = current_pokemon_data['name']
        attack = current_pokemon_data.get('stats', [])[1]['base_stat']
        defence = current_pokemon_data.get('stats', [])[2]['base_stat']
        speed = current_pokemon_data.get('stats', [])[4]['base_stat']
        special_attack = current_pokemon_data.get('stats', [])[
                    3]['base_stat']
        special_attack_points = current_pokemon_data.get('stats', [])[
                    3]['effort']
        new_computer_health = session.get('computer_health')
        new_player_health = session.get('player_health')
        is_even_round = (player_choice + computer_choice) % 2 == 0
        print(is_even_round)
        player_attack=0
        computer_attack=0
        if(is_even_round):
            player_attack = session.get('player_damage')
            computer_attack = session.get('computer_damage')
            new_computer_health = computer_health - (player_attack-0.5*computer_def)
        else:
            computer_attack = session.get('computer_damage')
            player_attack = session.get('player_damage')
            new_player_health = player_health - (computer_attack -0.5*player_def)
        session['player_health'] = new_player_health
        session['computer_health'] = new_computer_health
        if new_player_health <= 0:
            session.clear()
            insert_battle_result(current_pokemon_data['name'],computer_data['name'], "Defeat",get_current_id(),session.get('round_number'))
            outcome_message = 'Defeat'
            rec_mail = 'tefferino@gmail.com'
            mail_message = current_pokemon_data['name'] +'\n'+ computer_data['name'] + '\n'+outcome_message
            send_email(mail_message,rec_mail)
            print(player_attack)
            return render_template('pokemon.html', i=player_pokemon, name=name, health=health, attack=attack, defence=defence, speed=speed,
                                    special_attack=special_attack, special_attack_points=special_attack_points, player_choice=player_choice, 
                                    computer_choice=computer_choice, player_attack=player_attack, computer_attack=computer_attack, player_health=new_player_health, 
                                    computer_health=new_computer_health,computer_def = computer_def,outcome_message = outcome_message)
        elif new_computer_health <= 0:
            session.clear()
            insert_battle_result(current_pokemon_data['name'],computer_data['name'], "Win",get_current_id(),session.get('round_number'))
            outcome_message = 'Win'
            rec_mail = 'tefferino@gmail.com'
            mail_message = current_pokemon_data['name'] +'\n'+ computer_data['name'] + '\n'+outcome_message
            send_email(mail_message,rec_mail)  
            print(player_attack)          
            return render_template('pokemon.html', i=player_pokemon, name=name, health=health, attack=attack, defence=defence, speed=speed,
                                    special_attack=special_attack, special_attack_points=special_attack_points, player_choice=player_choice, 
                                    computer_choice=computer_choice, player_attack=player_attack, computer_attack=computer_attack, player_health=new_player_health, 
                                    computer_health=new_computer_health,computer_def = computer_def,outcome_message = outcome_message)
        else:
            round_number = session.get('round_number', 1)
            session['round_number'] = round_number + 1
            return render_template('pokemon.html', i=player_pokemon, name=name, health=health, attack=attack, defence=defence, speed=speed,
                                    special_attack=special_attack, special_attack_points=special_attack_points, player_choice=player_choice,
                                      computer_choice=computer_choice, player_attack=player_attack, computer_attack=computer_attack, player_health=new_player_health, 
                                      computer_health=new_computer_health,round_number=round_number,computer_def = computer_def)
    return "Invalid request method."
def get_current_id():
    if session.get('user_id'):
        return session.get('user_id')
    else: 
        return session.get('vk_id')
bcrypt = Bcrypt(app) 
@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        otp_enabled = True
        if (password == confirm_password):  
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            db = get_db()
            db.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, password_hash))
            db.commit()
            if otp_enabled:
                otp_secret = bcrypt.generate_password_hash(pyotp.random_base32()).decode('utf-8')
                db.execute('UPDATE users SET otp_secret = ? WHERE email = ?', (otp_secret, email))
                db.commit()
                msg = MIMEMultipart()
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = email
                msg['Subject'] = 'One time password'
                msg.attach(MIMEText(otp_secret, 'plain'))
                server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT)
                time.sleep(5)
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
                server.quit()    
            return redirect(url_for('login'))
        else: return render_template('register.html',outcome_message='Пароли не совпадают')
    else:
        return render_template('register.html')

@app.route('/password_recovery', methods=['GET', 'POST'])
def password_recovery():
    db=get_db()
    if request.method == 'POST':
        email = request.form['email']
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user:
            reset_token = secrets.token_urlsafe(32)
            db.execute('UPDATE users SET reset_token = ? WHERE email = ?',
                       (reset_token, email))
            db.commit()
            reset_link = f"{request.url_root}reset_password/{reset_token}"            
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = email
            msg['Subject'] = 'recovery password link'
            msg.attach(MIMEText(reset_link, 'plain'))
            server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT)
            time.sleep(5)
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
            server.quit()    
            flash('Password recovery instructions sent to your email.')
            return redirect(url_for('login'))
        else:
            flash('Email not found. Please check your email and try again.')

    return render_template('recover_page.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    db=get_db()
    user = db.execute('SELECT * FROM users WHERE reset_token = ?', (token,)).fetchone()

    if not user:
        flash('Invalid reset token.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            db.execute('UPDATE users SET password_hash = ?, reset_token = NULL WHERE id = ?',
                       (hashed_password, user['id']))
            db.commit()

            flash('Password reset successfully. You can now log in with your new password.')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match. Please try again.')

    return render_template('reset_password.html', token=token)

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        db = get_db()
        email = request.form['email']
        password = request.form['password']
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if user and bcrypt.check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            return redirect(url_for('choosing'))
        else:
            return 'Invalid email or password', 401
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('choosing'))

@app.route('/login_vk')
def login_vk():
    return vk.authorize(callback=url_for('authorized', _external=True))

@app.route('/authorized')
def authorized():
    db=get_db()
    response = vk.authorized_response()
    print(response)
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    user_info = vk.get('users.get', params={'fields': 'code,email'})

    vk_id = user_info.data['response'][0]['id']
    email = user_info.data['response'][0]['email']

    user = db.execute('SELECT * FROM users WHERE vk_id = ?', (vk_id,)).fetchone()

    if not user:
        db.execute('INSERT INTO users (id, email) VALUES (?, ?)', (vk_id, email))
        db.commit()
    session['user_id'] = vk_id
    return redirect(url_for('choosing'))


@app.route('/login_2fa', methods=['POST','GET'])
def login_2fa():
    if request.method == 'POST':
        db = get_db()
        email = request.form['email']
        otp = request.form['otp']
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if user and bcrypt.check_password_hash(user['otp_secret'], otp):
            session['user_id'] = user['id']
            return redirect(url_for('choosing'))
        else:
            return 'Invalid email or one time password', 401
    else:
        return render_template('login_2fa.html')

@app.route('/protected')
@login_required
def protected():
    return 'This page requires login'
if __name__ =='__main__':
    app.run(debug=True)
