import random

# Define suits and ranks for the deck
SUITS = ['spade', 'heart', 'diamond', 'club']
# RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANKS = ['02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14']

# Helper function to generate a deck of cards
def generate_deck():
    deck = []
    for suit in SUITS:
        for rank in RANKS:
            deck.append({'rank': rank, 'suit': suit})
    return deck

# Helper function to shuffle the deck
def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

# Function to start a new game
def start_game():
    # Generate and shuffle the deck
    deck = generate_deck()
    shuffled_deck = shuffle_deck(deck)

    # Deal cards to 4 players (each gets 13 cards)
    players = {i: [] for i in range(4)}  # Create a dictionary for 4 players
    for i in range(52):
        player_id = i % 4  # Distribute cards to players in round-robin fashion
        players[player_id].append(shuffled_deck[i])

    # Return the game state
    return {'deck': shuffled_deck, 'players': players}

# Function to get the cards for a specific player
def get_player_cards(game_state, player_id):
    return game_state['players'].get(player_id, [])

# Function to move to the next player
def next_player(game_state):
    # In Bridge, players take turns clockwise. We can simply cycle through players.
    # For simplicity, we are not tracking the current player here, just return the next player's cards.
    game_state['current_player'] = (game_state.get('current_player', 0) + 1) % 4
    return game_state
