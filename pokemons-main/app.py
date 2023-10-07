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
                return render_template('pokemon.html', i=player_pokemon, name=name, health=health,attack = attack, defence=defence, speed=speed, special_attack=special_attack, special_attack_points=special_attack_points)
            return player_pokemon
        except ValueError:
            pass
    else:
        pokemon_list = main()
        return render_template('index.html', pokemon_list=pokemon_list)


@app.route('/battle/<int:id>/<int:number>/<int:comp>')
def fight_json_return(id, number,comp):
    print('called')
    result = fight(id,number,comp)
    return jsonify({'result':result})

c_hp = 0
p_hp= 0
turn = 0
def fight(player_pokemon,number,comp):
    player_first = False
    computer_pokemon = comp
    if (number+random.randint(1,10)%2==0):
        player_first = True
    computer_pokemon_data = requests.get(
                    f'https://pokeapi.co/api/v2/pokemon/{computer_pokemon}/').json()
    current_pokemon_data = requests.get(
                    f'https://pokeapi.co/api/v2/pokemon/{player_pokemon}/').json()
    if (turn == 0):
        c_hp_left = computer_pokemon_data.get('stats', [])[0]['base_stat']
        p_hp_left = current_pokemon_data.get('stats', [])[0]['base_stat']
    else:
        c_hp_left =c_hp
        p_hp_left = p_hp
    c_att = computer_pokemon_data.get('stats', [])[1]['base_stat']
    p_att = current_pokemon_data.get('stats', [])[1]['base_stat']
    if(p_hp_left>0 and c_hp_left >0):
        if(player_first):
            c_hp_left -= p_att
            player_first = not player_first
            c_hp = c_hp_left
        else:
            p_hp_left -= c_att
            p_hp = p_hp_left
            player_first = not player_first
        
        if(p_hp_left>0 and c_hp_left >0):
            turn+=1
    return p_hp_left - c_hp_left
    

        
if __name__ =='__main__':
    app.run(debug=True)
