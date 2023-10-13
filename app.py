import requests
import ssl
import smtplib
import random
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
from flask import Flask, render_template, request,jsonify,session,g,redirect,url_for

app = Flask(__name__)
app.secret_key = 'tef'
app.config['DATABASE'] = 'pokemon.db'
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = '465'
EMAIL_ADDRESS = 'zhenya.lember@mail.ru'
EMAIL_PASSWORD = 'STFdVAVjVKmjexRN4gsA'
def send_email(message, to_email):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = 'реузльтат битвы покемонов'
        msg.attach(MIMEText(message, 'plain'))
        print(msg.as_string())
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
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
def insert_battle_result(player_name,computer_name,outcome):
    db = get_db()
    db.execute('INSERT INTO battle_results (player_name,computer_name, outcome, battle_date) VALUES (?, ?, ?,CURRENT_TIMESTAMP)',
               [player_name,computer_name,outcome])
    db.commit()
def main():
    # print('program going forward2')
    url = 'https://pokeapi.co/api/v2/pokemon/'
    param = {"limit": 20}
    response = requests.get(url, params=param)
    if response.status_code == 200:
        pokemon_list = []
        answer_data = response.json()
        pokemons_list = answer_data.get('results', [])
        for i, pokemon in enumerate(pokemons_list, start=1):
            current_pokemon_data = requests.get(
                f'https://pokeapi.co/api/v2/pokemon/{i}/').json()
            health = current_pokemon_data.get('stats', [])[0]['base_stat']
            attack = current_pokemon_data.get('stats', [])[1]['base_stat']
            pokemon_info = {
                "id": i,
                "name": pokemon['name'],
                "health": health,
                "attack": attack
            }
            pokemon_list.append(pokemon_info)
        return pokemon_list
    else:
        print(f"{response.status_code}")


@app.route("/", methods=["GET", "POST"])

def choosing():
    outcome_message = "" 

    if request.method == "POST":
        choice = request.form["choice"]
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

                return render_template('pokemon.html', i=player_pokemon, name=name, health=health, attack=attack, 
                                       defence=defence, speed=speed, special_attack=special_attack,
                                       special_attack_points=special_attack_points, 
                                       player_health=p_hp_left, computer_health=c_hp_left, computer_def=c_def,
                                       outcome_message=outcome_message)
            else:
                return "Invalid choice"
        except ValueError:
            pass
    else:
        pokemon_list = main()
        print(outcome_message)
        return render_template('index.html', pokemon_list=pokemon_list, outcome_message=outcome_message)
@app.route("/qbattle", methods = ["POST"])
def qbattle():
    if request.method == "POST":
        player_choice = random.randint(1,10)
        computer_choice = random.randint(1, 10)
        player_pokemon = session.get("player_pokemon")
        current_pokemon_data=requests.get(f'https://pokeapi.co/api/v2/pokemon/{player_pokemon}/').json()
        computer_data = requests.get(f'https://pokeapi.co/api/v2/pokemon/{session.get("computer_pokemon")}/').json()
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
        while(True):
            new_computer_health = session.get('computer_health')
            new_player_health = session.get('player_health')
            player_choice = random.randint(1, 10)
            computer_choice = random.randint(1, 10)
            is_even_round = (player_choice + computer_choice) % 2 == 0
            if(is_even_round):
                player_attack = session.get('player_damage')
                new_computer_health = computer_health - (player_attack-0.5*computer_def)
            else:
                computer_attack = session.get('computer_damage')
                new_player_health = player_health - (computer_attack -0.5*player_def)
            session['player_health'] = new_player_health
            session['computer_health'] = new_computer_health
            print(new_player_health)
            print(session.get('player_health'))
            if new_player_health <= 0:
                session.clear()
                insert_battle_result(current_pokemon_data['name'],computer_data['name'], "Defeat")
                outcome_message = 'Defeat'
                rec_mail = 'tefferino@gmail.com'
                mail_message = current_pokemon_data['name'] +'\n'+ computer_data['name'] + '\n'+outcome_message
                send_email(mail_message,rec_mail)
                return render_template('pokemon.html', i=player_pokemon, name=name, health=health, attack=attack, defence=defence, speed=speed, special_attack=special_attack, special_attack_points=special_attack_points, player_choice=player_choice, computer_choice=computer_choice, player_attack=player_attack, computer_attack=computer_attack, player_health=new_player_health, computer_health=new_computer_health,computer_def = computer_def,outcome_message = outcome_message)
            elif new_computer_health <= 0:
                session.clear()
                insert_battle_result(current_pokemon_data['name'],computer_data['name'], "Win")
                outcome_message = 'Win'
                rec_mail = 'tefferino@gmail.com'
                mail_message = current_pokemon_data['name'] +'\n'+ computer_data['name'] + '\n'+outcome_message
                send_email(mail_message,rec_mail)
                return render_template('pokemon.html', i=player_pokemon, name=name, health=health, attack=attack, defence=defence, speed=speed, special_attack=special_attack, special_attack_points=special_attack_points, player_choice=player_choice, computer_choice=computer_choice, player_attack=player_attack, computer_attack=computer_attack, player_health=new_player_health, computer_health=new_computer_health,computer_def = computer_def,outcome_message = outcome_message)
    return "Invalid request method."
@app.route("/battle", methods=["POST"])
def battle():
    if request.method == "POST":
        player_choice = int(request.form["player_choice"])
        computer_choice = random.randint(1, 10)
        player_pokemon = session.get("player_pokemon")
        current_pokemon_data=requests.get(f'https://pokeapi.co/api/v2/pokemon/{player_pokemon}/').json()
        computer_data = requests.get(f'https://pokeapi.co/api/v2/pokemon/{session.get("computer_pokemon")}/').json()
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
            new_computer_health = computer_health - (player_attack-0.5*computer_def)
        else:
            computer_attack = session.get('computer_damage')
            new_player_health = player_health - (computer_attack -0.5*player_def)
        print(player_health)
        print('\n')
        print(player_def)
        print('\n')
        session['player_health'] = new_player_health
        session['computer_health'] = new_computer_health
        if new_player_health <= 0:
            session.clear()
            insert_battle_result(current_pokemon_data['name'],computer_data['name'], "Defeat")
            outcome_message = 'Defeat'
            rec_mail = 'tefferino@gmail.com'
            mail_message = current_pokemon_data['name'] +'\n'+ computer_data['name'] + '\n'+outcome_message
            #send_email(mail_message,rec_mail)
            return render_template('pokemon.html', i=player_pokemon, name=name, health=health, attack=attack, defence=defence, speed=speed, special_attack=special_attack, special_attack_points=special_attack_points, player_choice=player_choice, computer_choice=computer_choice, player_attack=player_attack, computer_attack=computer_attack, player_health=new_player_health, computer_health=new_computer_health,computer_def = computer_def,outcome_message = outcome_message)
        elif new_computer_health <= 0:
            session.clear()
            insert_battle_result(current_pokemon_data['name'],computer_data['name'], "Win")
            outcome_message = 'Win'
            rec_mail = 'tefferino@gmail.com'
            mail_message = current_pokemon_data['name'] +'\n'+ computer_data['name'] + '\n'+outcome_message
            #send_email(mail_message,rec_mail)            
            return render_template('pokemon.html', i=player_pokemon, name=name, health=health, attack=attack, defence=defence, speed=speed, special_attack=special_attack, special_attack_points=special_attack_points, player_choice=player_choice, computer_choice=computer_choice, player_attack=player_attack, computer_attack=computer_attack, player_health=new_player_health, computer_health=new_computer_health,computer_def = computer_def,outcome_message = outcome_message)
        else:
            round_number = session.get('round_number', 1)
            session['round_number'] = round_number + 1
            return render_template('pokemon.html', i=player_pokemon, name=name, health=health, attack=attack, defence=defence, speed=speed, special_attack=special_attack, special_attack_points=special_attack_points, player_choice=player_choice, computer_choice=computer_choice, player_attack=player_attack, computer_attack=computer_attack, player_health=new_player_health, computer_health=new_computer_health,round_number=round_number,computer_def = computer_def)
    return "Invalid request method."
        
if __name__ =='__main__':
    app.run(debug=True)
