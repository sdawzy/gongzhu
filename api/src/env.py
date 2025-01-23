from .card import Hand, Card, CardCollection, Deck
from .player import Player
from typing import List, TYPE_CHECKING
from .policy import Policy, RandomPolicy
import sqlite3
import json
import os

DB_DIR = os.path.join("/data/record.db")
# Game environment class to manage game rules and state.
class Env:
    # Class-level variables for round count and number of players

    def __init__(self):
        # Initialize round count and number of players
        self.num_players = 0
        # Initialize allPlayedCards as a CardCollection instance
        self.all_played_cards = CardCollection()

    def get_all_played_cards(self):
        return self.all_played_cards

    def add_cards_to_played_cards(self, cards):
        # Add cards to the collection
        if isinstance(cards, CardCollection):
            self.all_played_cards.add_cards_from_collection(cards)
        elif isinstance(cards, list):
            self.all_played_cards.add_cards(cards)
        else:
            raise ValueError("Invalid type for cards. Must be CardCollection or list of Card objects.")

    def get_num_players(self):
        return Env.num_players

    def set_num_players(self, n):
        Env.num_players = n

    def calc_score(self, collected_cards):
        raise NotImplementedError("'calc_score' not yet implemented.")

    def legal_moves(self, hand, played_cards):
        raise NotImplementedError("'legal_moves' not yet implemented.")

class BloodCard:
    def __init__(self, rank, score):
        self.rank = rank
        self.score = score

    def get_rank(self):
        return self.rank

    def get_score(self):
        return self.score


class Gongzhu(Env):
    # Define 4 important cards
    PIG = Card("12", "spade")
    SHEEP = Card("11", "diamond")
    DOUBLER = Card("10", "club")
    BLOOD = Card("14", "heart")

    # Define blood cards with their scores
    BLOOD_CARDS = [
        BloodCard("02", 0),
        BloodCard("03", 0),
        BloodCard("04", 0),
        BloodCard("05", 10),
        BloodCard("06", 10),
        BloodCard("07", 10),
        BloodCard("08", 10),
        BloodCard("09", 10),
        BloodCard("10", 10),
        BloodCard("11", 20),
        BloodCard("12", 30),
        BloodCard("13", 40),
        BloodCard("14", 50),
    ]

    # Define the first card
    FIRST_CARD = Card("02", "spade")

    def __init__(self):
        super().__init__()
        self.max_round = 13
        self.set_num_players(4)
        
        # Initialize the effects of each special card
        self.pig_effect = 1.0
        self.sheep_effect = 1.0
        self.doubler_effect = 1.0
        self.blood_effect = 1.0

    def calc_score(self, collected_cards : CardCollection):
        score = 0
        has_pig = False
        has_sheep = False
        has_doubler = False
        has_all_blood = True
        no_blood = True

        # Score of pig
        if collected_cards.contains(Gongzhu.PIG):
            score -= 100.0 * self.pig_effect
            has_pig = True

        # Score of sheep
        if collected_cards.contains(Gongzhu.SHEEP):
            score += 100.0 * self.sheep_effect
            has_sheep = True

        # Score of blood
        blood_score_total = 0
        for blood_card in Gongzhu.BLOOD_CARDS:
            card = Card(blood_card.get_rank(), "heart")
            if collected_cards.contains(card):
                blood_score_total += blood_card.get_score()
                no_blood = False
            else:
                has_all_blood = False

        if has_all_blood:
            score += blood_score_total * self.blood_effect
        else:
            score -= blood_score_total * self.blood_effect

        # Score of doubler
        if collected_cards.contains(Gongzhu.DOUBLER):
            has_doubler = True

        # Bonus if collected everything
        if has_pig and has_sheep and has_all_blood and has_doubler:
            score += 200.0 * self.pig_effect

        # Effect of doubler
        if has_doubler:
            if not has_pig and not has_sheep and no_blood:
                score += 50 * self.doubler_effect
            else:
                score *= 2 * self.doubler_effect

        return score

    def legal_moves(self, hand : Hand, played_cards : List[Card]) -> CardCollection:
        if len(played_cards) == 0:
            return hand

        legal_moves = hand.get_cards_by_suit(played_cards[0].get_suit())
        return legal_moves if not legal_moves.is_empty() else hand

    def go_first(self, player : Player):
        return player.get_hand().contains(Gongzhu.FIRST_CARD)

    # Find the index of the player who goes first in the beginning of the game
    def who_goes_first_initial(self, players : List[Player]) -> int:
        # Find the index of the player who goes first
        for i in range(len(players)):
            if self.go_first(players[i]):
                return i
        return -1  # No player goes first

    # find the index of the player who played the largest card
    def find_largest_index(self, played_cards : List[Card]) -> int:
        largest_card = played_cards[0]
        index = 0
        for i in range(1, len(played_cards)):
            card = played_cards[i]
            if card.get_suit() != largest_card.get_suit():
                continue
            if card > largest_card:
                largest_card = card
                index = i
        return index
    
    def find_largest_card(self, played_cards : List[Card]):
        # Return None if no card has been played yet
        if len(played_cards) == 0:
            return None
        largest_card = played_cards[0]
        for i in range(1, len(played_cards)):
            card = played_cards[i]
            if card.get_suit() != largest_card.get_suit():
                continue
            if card > largest_card:
                largest_card = card
        return largest_card

class GongzhuGame:
    def __init__(self, ai_policy : Policy = RandomPolicy, db_dir=None):
        import secrets
        # A random unique identifier
        self.id : str = secrets.token_hex(16)

        self.env = Gongzhu()
        self.round_count = 0
        self.first_player_index = 0  # Index of the player who played first in this round
        self.current_player_index = 0  # Index of the current player in this round
        self.players : List[Player] = [
            Player(id="You", name="You", avatar_url="avatar_url1"),
            Player(id="Panda", name="Panda", avatar_url="avatar_url2"),
            Player(id="Penguin", name="Penguin", avatar_url="avatar_url3"),
            Player(id="Elephant", name="Elephant", avatar_url="avatar_url4"),
        ]
        # Policy for AI players
        self.ai_policy = ai_policy(self.env)
        self.playedCardsThisRound : List[Card] = [] # List of cards played this round

        # Game history information
        self.history = []

        # Database directory for storing game history
        self.db_dir = DB_DIR if db_dir is None else db_dir

        print(self.db_dir)
    def get_id(self):
        return self.id

    def get_round_count(self):
        return self.round_count

    def inc_round_count(self):
        self.round_count += 1
    
    def to_dict(self) -> dict:
        # Calculate scores for each player
        for player in self.players:
            player.get_score(self.env)
        return {
            "id": self.id,
            "aiPolicy": str(self.ai_policy),
            "players": [player.to_dict() for player in self.players],
            "roundCount": self.round_count,
            "firstPlayerIndex": self.first_player_index,
            "currentPlayerIndex": self.current_player_index,
            "cardsPlayedThisRound": [card.to_dict() for card in self.playedCardsThisRound],
            "isEndEpisode": self.is_end_episode(),
            "isYourTurn": self.is_your_turn(),
            "isEndOneRound": self.is_end_one_round(),
        }

    def get_history(self) -> List[dict]:
        return self.history

    def save_histroy(self):
        # Connect to the database
        conn = sqlite3.connect(self.db_dir)
        cursor = conn.cursor()
        
        # Create a table with a JSON column
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT,
                ai_policy TEXT,
                history TEXT
            )
        ''')
        conn.commit()

        # Save the game state to the database
        game_id = self.get_id()
        ai_policy = str(self.ai_policy)
        history = json.dumps(self.get_history())
        cursor.execute('INSERT INTO data (game_id, ai_policy, history) VALUES (?, ?, ?)', 
            (game_id, ai_policy, history))
        
        conn.commit()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(tables)  # Output: [('data',), ...]
        conn.close()
    
    def get_game_state(self) -> dict:
        return self.to_dict()

    def start(self):
        # First, deal cards to players
        deck = Deck()
        deck.shuffle()
        for player in self.players:
            for _ in range(13):
                player.add_card_to_hand(deck.deal_card())
            player.sort_hand()

        self.round_count = 0
        self.playedCardsThisRound = []
        # Figure out the first player initially
        self.first_player_index = self.env.who_goes_first_initial(self.players)
        self.current_player_index = self.first_player_index
        
        # Initialize the game history
        self.history = []

        return self.to_dict()
    
    def start_game(self):
        self.start()
        
    def get_current_player_index(self) -> int:
        return self.current_player_index
    
    def get_first_player_index(self) -> int:
        return self.first_player_index

    def is_end_episode(self) -> bool:
        return self.round_count >= self.env.max_round

    def is_your_turn(self) -> bool:
        return self.current_player_index == 0
    
    def is_end_one_round(self) -> bool:
        return len(self.playedCardsThisRound) >= 4

    def end_episode(self):
        return self.to_dict()

    def add_history(self, record : dict):
        self.history.append(record)


    # Check if a move is legal for this round
    def is_legal_move(self, player : Player, card : Card) -> bool:
        legal_moves = self.env.legal_moves(player.get_hand(), self.playedCardsThisRound)
        return legal_moves.contains(card)


    def next_round(self):
        # Sanity check: ensure each player has exactly same number of cards
        assert \
            (len(self.players[0].get_hand()) == len(self.players[1].get_hand()) ) and \
            (len(self.players[0].get_hand()) == len(self.players[2].get_hand()) ) and \
            (len(self.players[0].get_hand()) == len(self.players[3].get_hand()) ), \
            "Error: Different number of cards in hand!"
        # Increase the round count by 1
        self.round_count += 1
        # Find the index of largest player
        largest_index = (self.first_player_index + self.env.find_largest_index(self.playedCardsThisRound)) % len(self.players)
        # The largest player collects all the cards played this round
        self.players[largest_index].add_collected_cards(self.playedCardsThisRound)
        self.players[largest_index].sort_collected_cards()
        # Empty the currentPlayedCard of players
        for player in self.players:
            player.remove_current_played_card()
        # Empty the played cards of this round
        self.playedCardsThisRound = []
        # Update the current player index
        if (self.is_end_episode()):
            self.first_player_index = -1
            self.current_player_index = -1
            # Save the game history
            print("Saving game history...")
            self.save_histroy()
        else:
            self.first_player_index = largest_index
            self.current_player_index = largest_index
        
        self.add_history({
            "round": self.round_count,
            "largestIndex": largest_index,
        })

        return {
            "largestIndex": largest_index,
            "newRoundCount": self.round_count,
        }
        
    def next_player(self):
        # Play a card based on the policy
        old_player_index = self.current_player_index
        legal_moves = self.env.legal_moves(self.players[self.current_player_index].get_hand(), self.playedCardsThisRound)
        move : Card = self.ai_policy.decide_action(legal_moves=legal_moves, game_info=self.to_dict())
        self.playedCardsThisRound.append(move)
        self.players[self.current_player_index].play_specific_card(move)
        # Update the current player index
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        # Update the game history
        self.add_history({
            "round": self.round_count,
            "playerIndex": old_player_index,
            "move": move.to_dict(),
        })
        
        return {
            "currentPlayerIndex": old_player_index,
            "move": move.to_dict(),
        }

    def play_selected_card(self, card : Card):
        # Check if the current player can play this card
        if self.is_legal_move(self.players[self.current_player_index], card):
            self.playedCardsThisRound.append(card)
            self.players[self.current_player_index].play_specific_card(card)
            # Update the current player index
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            # Update the game history
            self.history.append({
                "round": self.round_count,
                "playerIndex": 0,
                "move": card.to_dict(),
            })
            return self.to_dict()   
        else:
            return None

    def declaration(self):
        # TODO: Implement declaration phase
        pass
    
    

