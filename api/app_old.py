from flask import Flask
from flask import jsonify
from flask import request
from bridge_game import start_game, next_player, get_player_cards  # Import your game logic
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize your game
game = start_game()  # Assuming `start_game()` is a function in your Python code

@app.route('/start_game', methods=['GET'])
def start_game_route():
    global game
    game = start_game()  # Start a new game
    return jsonify({'message': 'Game started successfully'}), 200

@app.route('/get_player_cards', methods=['GET'])
def get_player_cards_route():
    player_id = request.args.get('player_id', type=int)  # Get player ID from the query parameter
    cards = get_player_cards(game, player_id)  # Get the cards of the player from your game logic
    return jsonify({'cards': cards}), 200

@app.route('/next_player', methods=['POST'])
def next_player_route():
    global game
    game = next_player(game)  # Update the game to the next player
    return jsonify({'message': 'Next player'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1926)  # Run the Flask app
