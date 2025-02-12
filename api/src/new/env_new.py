# Ok let me try to rewrite everything using gym.Env
# By Yue Zhang, Feb 11, 2025
from .card import Hand, Card, CardCollection, Deck
from .player_new import Player
from typing import List, TYPE_CHECKING, Any, Generic, SupportsFloat
from .policy import Policy, RandomPolicy
from random import Random
import gymnasium as gym
from gymnasium import ObsType, ActType, RenderFrame
import secrets
import sqlite3
import json
import os
import numpy as np

DB_DIR = os.path.join("/data/record.db")



# Class of Gongzhu game using gym.Env
class Gongzhu(gym.Env):
    # Define 4 important cards
    PIG = Card("12", "spade")
    SHEEP = Card("11", "diamond")
    DOUBLER = Card("10", "club")
    BLOOD = Card("14", "heart")

    # Define blood cards with their scores
    class BloodCard:
        def __init__(self, rank, score):
            self.rank = rank
            self.score = score

        def get_rank(self):
            return self.rank

        def get_score(self):
            return self.score

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

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 20}

    def __init__(self, 
            render_mode=None, 
            enable_declaration : bool = False,
            n_players : int = 4):
        # A random unique identifier
        self.id : str = secrets.token_hex(16)

        # Meta information related to Gongzhu
        self._n_actions : int = 52 
        # 4 players by default. If I have time, I will implement 3 players version
        self._n_players : int = n_players 
        # 13 rounds for 4 players version
        self._max_rounds : int = 13
        self._round_count : int = 0

        # Observation and action spaces
        action_space = gym.spaces.Discrete(self._n_actions)

        # Observation space consists of 
        # 1. Information of the agent player (players[0])
        # 2. Other players' information (players[1:4])
        # 3. Game history (List of 52 x 1 one-hot vectors)
        # 4. Other meta information ?
        # observation_space = gym.spaces.Dict(
        #     {"agent_info": Box(-1, 1, shape=(2,)), 
        #     "color": Discrete(3)}, 
        # )

        # Initialize the effects of each special card
        self._pig_effect : float = 1.0
        self._sheep_effect : float = 1.0
        self._doubler_effect : float = 1.0
        self._blood_effect : float = 1.0

        self._current_player_index : int = 0  # Index of the current player in this round
        # Intialize players
        self._players : List[Player] = []

        # Policy for AI players
        # self._ai_policy : Policy = ai_policy(self)
        self._playedCardsThisRound : List[Card] = [] # List of cards played this round

        # Game history information
        self._history : List[np.array] = []

        # Scores of both teams
        self._my_team_score : int = 0
        self._opponent_team_score : int = 0

        # Whether declaration is enabled or not
        self._enable_declaration = enable_declaration

        # Start the game
        # self.start()

    # Start the game
    def start(self):
        # First, deal cards to players
        deck = Deck()
        deck.shuffle()
        for player in self._players:
            for _ in range(13):
                player.add_card_to_hand(deck.deal_card())
            player.sort_hand()
        # Initialize the effects of each special card
        self._pig_effect : float = 1.0
        self._sheep_effect : float = 1.0
        self._doubler_effect : float = 1.0
        self._blood_effect : float = 1.0
        # Reset round counts
        self._round_count = 0
        self._playedCardsThisRound = []
        # Figure out the first player initially
        self._first_player_index = self._who_goes_first_initial(self._players)
        self._current_player_index = self._first_player_index
        
        # Clear scores of both teams
        self._my_team_score : int = 0
        self._opponent_team_score : int = 0
        # Initialize the game history
        self.history = []

        return self.to_dict()
    
    # Get the legal moves
    def legal_moves(self, hand : Hand, played_cards : List[Card]) \
        -> CardCollection:
        # If no cards were played, any card in the hand is legal
        if len(played_cards) == 0:
            return hand

        legal_moves = hand.get_cards_by_suit(played_cards[0].get_suit())
        return legal_moves if not legal_moves.is_empty() else hand
    
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

    # Calculate the score based on a hand
    # TODO: rewrite using matrix operations
    def calc_score(self, collected_cards : CardCollection) -> int:
        score = 0
        has_pig = False
        has_sheep = False
        has_doubler = False
        has_all_blood = True
        no_blood = True

        # Score of pig
        if collected_cards.contains(Gongzhu.PIG):
            score -= 100.0 * self._pig_effect
            has_pig = True

        # Score of sheep
        if collected_cards.contains(Gongzhu.SHEEP):
            score += 100.0 * self._sheep_effect
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
            score += blood_score_total * self._blood_effect
        else:
            score -= blood_score_total * self._blood_effect

        # Score of doubler
        if collected_cards.contains(Gongzhu.DOUBLER):
            has_doubler = True

        # Bonus if collected everything
        if has_pig and has_sheep and has_all_blood and has_doubler:
            score += 200.0 * self._pig_effect

        # Effect of doubler
        if has_doubler:
            if not has_pig and not has_sheep and no_blood:
                score += 50 * self._doubler_effect
            else:
                score *= 2 * self._doubler_effect

        return score

    # Find the index of the player who goes first in the beginning of the game
    def _who_goes_first_initial(self, players : List[Player]) -> int:
        # Find the index of the player who goes first
        for i in range(len(players)):
            if players[i].get_hand().contains(self.FIRST_CARD):
                return i
        raise f"No Player has {self.FIRST_CARD} in this game."
    
    # Check if a move is legal for this round
    def is_legal_move(self, player : Player, card : Card) -> bool:
        legal_moves = self.legal_moves(player.get_hand(), self._playedCardsThisRound)
        return legal_moves.contains(card)

    def next_round(self):
        # Sanity check: ensure each player has exactly same number of cards
        assert \
            (len(self._players[0].get_hand()) == len(self._players[1].get_hand()) ) and \
            (len(self._players[0].get_hand()) == len(self._players[2].get_hand()) ) and \
            (len(self._players[0].get_hand()) == len(self._players[3].get_hand()) ), \
            "Error: Different number of cards in hand!"
        # Increase the round count by 1
        self._round_count += 1
        # Find the index of largest player
        largest_index = (self._first_player_index + self.find_largest_index(self._playedCardsThisRound)) % len(self.players)
        # The largest player collects all the cards played this round
        self._players[largest_index].add_collected_cards(self._playedCardsThisRound)
        self._players[largest_index].sort_collected_cards()
        # Empty the currentPlayedCard of players
        for player in self._players:
            player.remove_current_played_card()
        # Empty the played cards of this round
        self._playedCardsThisRound = []
        # Update the current player index
        if (self.is_end_episode()):
            self._first_player_index = -1
            self._current_player_index = -1
            # # Save the game history
            # print("Saving game history...")
            self.save_histroy()
        else:
            self._first_player_index = largest_index
            self._current_player_index = largest_index
        
        # self.add_history()

        return {
            "largestIndex": largest_index,
            "newRoundCount": self._round_count,
        }
        
    def next_player(self):
        # Play a card based on the policy
        old_player_index = self._current_player_index
        legal_moves = self.legal_moves(self._players[self._current_player_index].get_hand(), self._playedCardsThisRound)
        move : Card = self._players[self._current_player_index].policy.decide_action(
            legal_moves=legal_moves, 
            game_info=self.to_dict()
        )
        self._playedCardsThisRound.append(move)
        self._players[self._current_player_index].play_specific_card(move)
        # Update the current player index
        self._current_player_index = (self._current_player_index + 1) % self._n_players
        # Update the game history
        self.add_history(move.vec)
        
        return {
            "currentPlayerIndex": old_player_index,
            "move": move.to_dict(),
        }

    def play_selected_card(self, card : Card):
        # Check if the current player can play this card
        if self.is_legal_move(self._players[self._current_player_index], card):
            self._playedCardsThisRound.append(card)
            self._players[self._current_player_index].play_specific_card(card)
            # Update the current player index
            self._current_player_index = (self._current_player_index + 1) % len(self.players)
            # Update the game history
            self.history.append({
                "round": self._round_count,
                "playerIndex": 0,
                "move": card.to_dict(),
            })
            return self.to_dict()   
        else:
            return None

    def declaration(self):
        # TODO: Implement declaration phase
        pass
    
    @property
    def is_end_episode(self):
        return self._round_count >= self._max_rounds

    @property
    def to_state(self):
        return self.to_dict()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "aiPolicy": str(self._ai_policy),
            "players": [player.to_dict() for player in self._players],
            "roundCount": self._round_count,
            "firstPlayerIndex": self._first_player_index,
            "currentPlayerIndex": self._current_player_index,
            "cardsPlayedThisRound": [card.to_dict() for card in self._playedCardsThisRound],
            "isEndEpisode": self.is_end_episode,
        }
    
    def start_game(self):
        self.start()
        
    def get_current_player_index(self) -> int:
        return self._current_player_index
    
    def get_first_player_index(self) -> int:
        return self._first_player_index

    def is_your_turn(self) -> bool:
        return self._current_player_index == 0
    
    def is_end_one_round(self) -> bool:
        return len(self._playedCardsThisRound) >= 4

    def end_episode(self):
        return self.to_dict()

    def add_history(self, move : np.array) -> None:
        self.history.append(move)
    
    def save_histroy(self) -> None:
        # TODO: Implement saving game history
        return

    def step(self, action: ActType) \
        -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        return super().step(action)
    
    def reset(self, ai_players : List[Player] = [],
        seed=None) -> ObsType:
        assert len(ai_players) == 0 or len(ai_players) == 4, "Please specify exactly four players. The first player is you."
        # If the ai players are not specified, 
        if len(ai_players) == 0:
            self._players = [
                Player(id="You", name="You", avatar_url="avatar_url1", policy=RandomPolicy),
                Player(id="Panda", name="Panda", avatar_url="avatar_url2", policy=RandomPolicy),
                Player(id="Penguin", name="Penguin", avatar_url="avatar_url3", policy=RandomPolicy),
                Player(id="Elephant", name="Elephant", avatar_url="avatar_url4", policy=RandomPolicy),
            ]
        else:
            self._players =  ai_players

        if seed is not None:
            Random.seed(seed)
        
        # Reset player data (other than ratings)
        for player in self._players:
            player.reset()

        # Reset game data by restarting the game
        self.start()

        return self.to_state, {}
    
    def render(self, mode='human'):
        pass

    def close(self):
        pass
    









# If I have time, I would like to implement the full version of Gongzhu
# class GongzhuGameMultiround(Gongzhu):
#     def __init__(self, threshold = 1000, ai_policy : Policy = RandomPolicy, db_dir=None):
#         super().__init__(ai_policy, db_dir)

#         self.episode_count = 1

#         self.threshold = threshold
#         # You and player[2]
#         self.team1_scores : List[int] = []
#         # player[1] and player[3]
#         self.team2_scores : List[int] = []
    
#     def new_episode(self):

#         self.episode_count += 1
#         self.team1_scores.append(self.players[0].get_score() + self.players[2].get_score())
#         self.team1_scores.append(self.players[1].get_score() + self.players[3].get_score())

#         # Reset player data
#         for player in self.players:
#             player.reset()
        
#         # Start a new game
#         return self.start()

#     def to_dict(self) -> dict:
#         # Calculate scores for each player
#         for player in self.players:
#             player.get_score(self.env)
#         return {
#             "id": self.id,
#             "aiPolicy": str(self.ai_policy),
#             "players": [player.to_dict() for player in self.players],
#             "roundCount": self.round_count,
#             "firstPlayerIndex": self.first_player_index,
#             "currentPlayerIndex": self.current_player_index,
#             "cardsPlayedThisRound": [card.to_dict() for card in self.playedCardsThisRound],
#             "isEndEpisode": self.is_end_episode(),
#             "isYourTurn": self.is_your_turn(),
#             "isEndOneRound": self.is_end_one_round(),
#             "episode": self.episode_count,
#             "team1Scores": self.team1_scores,
#             "team2Scores": self.team2_scores,
#         }