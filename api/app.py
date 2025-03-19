# API for the Gongzhu environment
# By Yue Zhang, Jan 27, 2025
from flask import Flask, jsonify, request
from flask_cors import CORS
# from typing import List, dict
from src.env import Gongzhu
from src.card import Card
from src.declaration import Declaration
from src.policy import RandomPolicy, GreedyPolicy, Policy
from src.player import Player
import os

app = Flask(__name__)
CORS(app)

DB_DIR = "data/record.db"
# A dictionary to store ongoing games
games : dict = {}
# game : GongzhuGame = GongzhuGame(ai_policy=RandomPolicy)  # Initialize your game

def get_game_by_id(game_id):
    global games
    return games.get(game_id)

ai_policies = {
    "random": RandomPolicy,
    "greedy": GreedyPolicy,
    # Add more AI policies as needed
}
@app.route('/start_game', methods=['POST'])
def start_game_route():
    # Get AI policy 
    data : dict = request.json
    ai_policy : Policy = ai_policies[data.get('ai')]
    auto = data.get('auto')
    declaration = data.get('declaration')
    print(f"Declaration is {declaration}")
    global games
    # game = GongzhuGame(ai_policy=RandomPolicy)
    game = Gongzhu(enable_declaration=declaration)
    # game.start_game()  # Start a new game
    game.reset(ai_players= [
                Player(id="You", name="You", avatar_url="avatar_url1", 
                policy=ai_policy(env=game)),
                Player(id="Panda", name="Panda", avatar_url="avatar_url2", 
                policy=ai_policy(env=game)),
                Player(id="Penguin", name="Penguin", avatar_url="avatar_url3",
                policy=ai_policy(env=game)),
                Player(id="Elephant", name="Elephant", avatar_url="avatar_url4",
                policy=ai_policy(env=game)),
        ], auto=auto)

    games[game.get_id()] = game  # Store the game in the dictionary
    # print(games)


    return jsonify({'message': 'Game started successfully', 'id': game.get_id()}), 200

@app.route('/step', methods=['POST'])
def step():
    data : dict = request.json
    id = data.get('id')
    game : Gongzhu = get_game_by_id(id)
    if game.is_declaration_phase():
        open_declarations = data.get('open_declarations')
        open_declarations = [Card(suit=card['suit'], rank=card['rank']) for card in open_declarations]
        closed_declarations = data.get('closed_declarations')
        closed_declarations = [{"card" : Card(suit=card['suit'], rank=card['rank']), "revealed" : False} 
            for card in closed_declarations]
        declarations = Declaration(open_declarations=open_declarations, closed_declarations=closed_declarations)

        if game.is_legal_declarations(player=game.get_player_by_index(0), declarations=declarations):
            game.step(declarations)
            return jsonify({'message': 'Declarations made successfully'}), 200
        else:
            return jsonify({'message': 'Invalid declarations'}), 400
    else:
        suit = data.get('suit')  # Get suit from the query parameter
        rank = data.get('rank')  # Get rank from the query parameter
        action = Card(suit=suit, rank=rank)  # Create a tuple representing the action to be taken by the player
        
        if not game.is_legal_move(game.get_player_by_index(0), action):
            return jsonify({'message': 'Invalid move'}), 400
        
        game.step(action)  # Step the game with the provided action
        return jsonify({'message': "stepped to the next state"}), 200

@app.route('/get_game_state', methods=['POST'])
def get_game_state_route():
    data : dict = request.json
    id = data.get('id')
    # print(id)
    game : Gongzhu = get_game_by_id(id)

    game_state = game.get_game_state()  # Get the current game state from your game logic
    # print(game_state)
    return jsonify({'game_state': game_state}), 200

@app.route('/get_current_player_index', methods=['POST'])
def get_current_player_index_route():
    data : dict = request.json
    id = data.get('id')
    game : Gongzhu = get_game_by_id(id)

    current_player_index = game.get_current_player_index(game)  # Get the current player index from your game logic
    return jsonify({'current_player_index': current_player_index}), 200

@app.route('/get_legal_moves', methods=['POST'])
def get_legal_moves_route():
    data : dict = request.json
    id = data.get('id')
    player_id = data.get('player_id')  # Get player ID from the query parameter
    game : Gongzhu = get_game_by_id(id)
    
    legal_moves = game.legal_moves(hand=game.get_player_by_index(player_id).get_hand(), 
                    played_cards=game.get_played_cards_this_round())  # Get the legal moves from your game logic
    return jsonify({'legal_moves': legal_moves}), 200

@app.route('/next_player', methods=['POST'])
def next_player_route():
    data : dict = request.json
    id = data.get('id')
    game : Gongzhu = get_game_by_id(id)

    if game.get_current_player_index() == 0:  # Check if it's the user's turn
        return jsonify({'message': 'It is your turn'}), 403
    index_and_move = game.next_player()  # Get the next player index and move from the request body
    return jsonify(index_and_move), 200


@app.route('/make_declarations', methods=['POST'])
def make_declarations_route():
    data : dict = request.json
    id = data.get('id')
    game : Gongzhu = get_game_by_id(id)

    if game.get_current_player_index() != 0:  # Check if it's the current player's turn
        return jsonify({'message': 'It is not your turn'}), 403  # Return 403 Forbidden if it's not the current player's turn
    
    open_declarations = data.get('open_declarations')
    open_declarations = [Card(suit=card['suit'], rank=card['rank']) for card in open_declarations]
    closed_declarations = data.get('closed_declarations')
    closed_declarations = [{"card" : Card(suit=card['suit'], rank=card['rank']), "revealed" : False} 
        for card in closed_declarations]
    declarations = Declaration(open_declarations=open_declarations, closed_declarations=closed_declarations)

    if game.is_legal_declarations(player=game.get_player_by_index(0), declarations=declarations):
        game.make_declarations(declarations)
        return jsonify({'message': 'Declarations made successfully'}), 200
    else:
        return jsonify({'message': 'Invalid declarations'}), 400

@app.route('/play_card', methods=['POST'])
def play_card_route():
    data : dict = request.json
    id = data.get('id')
    game : Gongzhu = get_game_by_id(id)

    if game.get_current_player_index() != 0:  # Check if it's the current player's turn
        return jsonify({'message': 'It is not your turn'}), 403  # Return 403 Forbidden if it's not the current player's turn

    suit = data.get('suit')  # Get suit from the query parameter
    rank = data.get('rank')  # Get rank from the query parameter
    
    # print(request)
    # print(suit, rank)
    card = Card(suit=suit, rank=rank)  # Create a card object
    if game.is_legal_move(game.get_player_by_index(0), card):
        game.play_selected_card(card)
        return jsonify({'message': 'Card played successfully'}), 200
    else:
        return jsonify({'message': 'Invalid move'}), 400

@app.route('/next_round', methods=['POST'])
def next_round_route():
    data : dict = request.json
    id = data.get('id')
    game : Gongzhu = get_game_by_id(id)

    if not game.is_end_one_round():
        return jsonify({'message': 'It is not the end of the round'}), 403  # Return 403 Forbidden if it's not the end of the round
    
    largest_and_round_count = game.next_round()  # Get the next round index and move from your game logic
    largest_index = largest_and_round_count['largestIndex']
    return jsonify({'message': 'Next round starts', 'largestIndex': largest_index}), 200

if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port=1926)  # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=1926)

# option 1: json
# option 2: sqlite