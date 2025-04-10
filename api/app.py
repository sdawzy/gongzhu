# API for the Gongzhu environment
# By Yue Zhang, Jan 27, 2025
# Updated Apr 10, 2025
from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import torch
from cachetools import TTLCache
import os
# import redis

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

# from typing import List, dict
from env import Gongzhu
from card import Card
from declaration import Declaration
from policy import RandomPolicy, GreedyPolicy, Policy, DMC, MFE
from player import Player

DB_DIR = "data/record.db"
# CHECKPOINT_DIR = "src/gongzhuai_checkpoints/gongzhuai/weights_1e6_2.ckpt"
def load_policy(model_class, checkpoint_path):
    model = model_class()
    state_dict = torch.load(checkpoint_path)
    model.load_state_dict(state_dict)
    model.eval()
    return model

# Paths
CHECKPOINT_DIR_MFE = "trained_models/mfe/weights_15e5_4.ckpt"
CHECKPOINT_DIR_DMC = "trained_models/dmc/weights_1e6_2.ckpt"

# Load models
mfe_policy = load_policy(MFE, CHECKPOINT_DIR_MFE)
dmc_policy = load_policy(DMC, CHECKPOINT_DIR_DMC)

# Other policies
random_policy = RandomPolicy()
greedy_policy = GreedyPolicy()

# A dictionary to store ongoing games
# games = redis.Redis(host='localhost', port=6379, db=0)
# print(games.ping())  # Should print True

# games : dict = {}
games = TTLCache(maxsize=2000, ttl=3600)
# game : GongzhuGame = GongzhuGame(ai_policy=RandomPolicy)  # Initialize your game

def get_game_by_id(game_id):
    global games
    return games.get(game_id)

def store_game(game):
    global games
    games[game.get_id()] = game  # Store the game in the dictionary 
    # games.set(game.get_id(), game, ex=3600)

ai_policies = {
    "random": random_policy,
    "greedy": greedy_policy,
    "DMC": dmc_policy,
    "MFE": mfe_policy,
}

app = Flask(__name__)
CORS(app)

@app.route('/start_game', methods=['POST'])
def start_game_route():
    # Get AI policy 
    data : dict = request.json
    ai_policy : Policy = ai_policies[data.get('ai')]
    # if data.get('ai') == "DMC":
    #     checkpoint_state = torch.load(CHECKPOINT_DIR)
    #     ai_policy.load_state_dict(checkpoint_state)
    auto = data.get('auto')
    declaration = data.get('declaration')
    # print(f"Declaration is {declaration}")
    global games
    # game = GongzhuGame(ai_policy=RandomPolicy)
    game = Gongzhu(enable_declaration=declaration)
    # game.start_game()  # Start a new game
    game.reset(ai_players= [
                Player(id="You", name="You", avatar_url="avatar_url1", 
                policy=ai_policy),
                Player(id="Panda", name="Panda", avatar_url="avatar_url2", 
                policy=ai_policy),
                Player(id="Penguin", name="Penguin", avatar_url="avatar_url3",
                policy=ai_policy),
                Player(id="Elephant", name="Elephant", avatar_url="avatar_url4",
                policy=ai_policy),
        ], auto=auto)
    store_game(game)

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

@app.route('/evaluate', methods=['POST'])
def evaluate_route():
    data : dict = request.json
    id = data.get('id')
    game : Gongzhu = get_game_by_id(id)
    if game.get_current_player_index() != 0:  # Check if it's the current player's turn
        return jsonify({'message': 'It is not your turn'}), 403  # Return 403 Forbidden if it's not the current player's turn

    suit = data.get('suit')  # Get suit from the query parameter
    rank = data.get('rank')  # Get rank from the query parameter
    
    card = Card(suit=suit, rank=rank)  # Create a card object
    if game.is_legal_move(game.get_player_by_index(0), card):
        eval : torch.Tensor = game.action_value_estimate(action=card, policy=mfe_policy)
        return jsonify({'evaluation': round(eval.item() * 1000, 3)}), 200
    else:
        return jsonify({'evaluation': -114514}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
