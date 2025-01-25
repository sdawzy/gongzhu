from flask import Flask, jsonify, request
from flask_cors import CORS
# from typing import List, dict
from src.env import GongzhuGame
from src.card import Card
from src.policy import RandomPolicy, GreedyPolicy
import os

app = Flask(__name__)
CORS(app)

DB_DIR = os.path.join("data/record.db")
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
    ai_policy = data.get('ai')
    global games
    # game = GongzhuGame(ai_policy=RandomPolicy)
    game = GongzhuGame(ai_policy=ai_policies[ai_policy], db_dir=DB_DIR)
    game.start_game()  # Start a new game
    games[game.get_id()] = game  # Store the game in the dictionary
    # print(games)


    return jsonify({'message': 'Game started successfully', 'id': game.get_id()}), 200

@app.route('/get_game_state', methods=['POST'])
def get_game_state_route():
    data : dict = request.json
    id = data.get('id')
    # print(id)
    game = get_game_by_id(id)

    game_state = game.get_game_state()  # Get the current game state from your game logic
    return jsonify({'game_state': game_state}), 200

@app.route('/get_current_player_index', methods=['POST'])
def get_current_player_index_route():
    data : dict = request.json
    id = data.get('id')
    game = get_game_by_id(id)

    current_player_index = game.get_current_player_index(game)  # Get the current player index from your game logic
    return jsonify({'current_player_index': current_player_index}), 200

@app.route('/get_legal_moves', methods=['POST'])
def get_legal_moves_route():
    data : dict = request.json
    id = data.get('id')
    player_id = data.get('player_id')  # Get player ID from the query parameter
    game = get_game_by_id(id)
    
    legal_moves = game.get_legal_moves(game, player_id)  # Get the legal moves from your game logic
    return jsonify({'legal_moves': legal_moves}), 200

@app.route('/next_player', methods=['POST'])
def next_player_route():
    data : dict = request.json
    id = data.get('id')
    game = get_game_by_id(id)

    if game.current_player_index == 0:  # Check if it's the user's turn
        return jsonify({'message': 'It is your turn'}), 403
    index_and_move = game.next_player()  # Get the next player index and move from the request body
    return jsonify(index_and_move), 200

@app.route('/play_card', methods=['POST'])
def play_card_route():
    data : dict = request.json
    id = data.get('id')
    game = get_game_by_id(id)

    if game.current_player_index != 0:  # Check if it's the current player's turn
        return jsonify({'message': 'It is not your turn'}), 403  # Return 403 Forbidden if it's not the current player's turn

    suit = data.get('suit')  # Get suit from the query parameter
    rank = data.get('rank')  # Get rank from the query parameter
    
    print(request)
    print(suit, rank)
    card = Card(suit=suit, rank=rank)  # Create a card object
    if game.is_legal_move(game.players[0], card):
        game.play_selected_card(card)
        return jsonify({'message': 'Card played successfully'}), 200
    else:
        return jsonify({'message': 'Invalid move'}), 400

@app.route('/next_round', methods=['POST'])
def next_round_route():
    data : dict = request.json
    id = data.get('id')
    game = get_game_by_id(id)

    if not game.is_end_one_round():
        return jsonify({'message': 'It is not the end of the round'}), 403  # Return 403 Forbidden if it's not the end of the round
    
    largest_and_round_count = game.next_round()  # Get the next round index and move from your game logic
    largest_index = largest_and_round_count['largestIndex']
    return jsonify({'message': 'Next round starts', 'largestIndex': largest_index}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1926)  # Run the Flask app

# option 1: json
# option 2: sqlite