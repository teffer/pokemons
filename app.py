import requests
import ssl
import random
from flask import Flask, render_template, request,jsonify

app = Flask(__name__)


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
    if request.method == "POST":
        choice = request.form["choice"]
        try:
            player_pokemon = int(choice)
            if (player_pokemon > 0 and player_pokemon < 20):
                current_pokemon_data = requests.get(
                    f'https://pokeapi.co/api/v2/pokemon/{player_pokemon}/').json()
                health = current_pokemon_data.get('stats', [])[0]['base_stat']
                name = current_pokemon_data['name']
                attack = current_pokemon_data.get('stats', [])[1]['base_stat']
                defence = current_pokemon_data.get('stats', [])[2]['base_stat']
                speed = current_pokemon_data.get('stats', [])[4]['base_stat']
                special_attack = current_pokemon_data.get('stats', [])[
                    3]['base_stat']
                special_attack_points = current_pokemon_data.get('stats', [])[
                    3]['effort']
                print(f"{player_pokemon}.{current_pokemon_data['name']}, Здоровье - {health}, Урон - {attack}\nЗащита - {defence} Скорость - {speed}\n Спец атака нанесёт урона - {special_attack}"
                      f" и потратит {special_attack_points} очков усилий")
                return render_template('pokemon.html', i=player_pokemon, name=name, health=health,attack = attack, defence=defence, speed=speed, special_attack=special_attack, special_attack_points=special_attack_points)
            return player_pokemon
        except ValueError:
            pass
    else:
        pokemon_list = main()
        return render_template('index.html', pokemon_list=pokemon_list)


@app.route('/battle/<int:id>')
def fight_json_return(id):
    result = fight(id)
    return jsonify({'result':result})


def fight(player_pokemon):
    not_player_type = True
    player_first = False
    while(not_player_type):
        computer_pokemon = random.randint(1,20)
        if player_pokemon == computer_pokemon:
            pass
        else:
            break
    if (random.randint(1,6)+random.randint(1,6)%2==0):
        player_first = True
    computer_pokemon_data = requests.get(
                    f'https://pokeapi.co/api/v2/pokemon/{computer_pokemon}/').json()
    current_pokemon_data = requests.get(
                    f'https://pokeapi.co/api/v2/pokemon/{player_pokemon}/').json()
    c_hp_left = computer_pokemon_data.get('stats', [])[0]['base_stat']
    p_hp_left = current_pokemon_data.get('stats', [])[0]['base_stat']
    print(c_hp_left, p_hp_left)
    c_att = computer_pokemon_data.get('stats', [])[1]['base_stat']
    p_att = current_pokemon_data.get('stats', [])[1]['base_stat']
    while(c_hp_left>0 and p_hp_left>0):
        if(player_first):
            c_hp_left -= p_att
        else:
            p_hp_left -= c_att
        player_first = not player_first
    if(c_hp_left > p_hp_left):
        return False
    if(p_hp_left > c_hp_left):
        return True

        
if __name__ =='__main__':
    app.run(debug=True)
