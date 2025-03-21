# Ok let me try to rewrite everything using gym.Env
# By Yue Zhang, Feb 11, 2025
# Updated Feb 18, 2025
from card import Hand, Card, CardCollection, Deck, PIG, SHEEP, BLOOD, DOUBLER, SPECIAL_CARDS, EMPTY_CARD
from player import Player
from policy import Policy, RandomPolicy
from declaration import Declaration

from typing import List, TYPE_CHECKING, Any, Generic, SupportsFloat, TypeVar
from random import Random
import gymnasium as gym
from gymnasium.spaces import Discrete, Box, Sequence, Dict, Space
import secrets
import sqlite3
import json
import os
import numpy as np

# if TYPE_CHECKING:
#     
ObsType = TypeVar("ObsType")
ActType = TypeVar("ActType")
RenderFrame = TypeVar("RenderFrame")

DB_DIR = os.path.join("/data/record.db")


# Class of Gongzhu game using gym.Env
class Gongzhu(gym.Env):
    # Define 4 important cards
    PIG = PIG
    SHEEP = SHEEP
    DOUBLER = DOUBLER
    BLOOD = BLOOD

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
        BloodCard("2", 0),
        BloodCard("3", 0),
        BloodCard("4", 0),
        BloodCard("5", 10),
        BloodCard("6", 10),
        BloodCard("7", 10),
        BloodCard("8", 10),
        BloodCard("9", 10),
        BloodCard("10", 10),
        BloodCard("Jack", 20),
        BloodCard("Queen", 30),
        BloodCard("King", 40),
        BloodCard("Ace", 50),
    ]
    # Define the first card
    FIRST_CARD = Card("2", "spade")

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 20}

    def __init__(self, 
            render_mode=None, 
            enable_declaration : bool = False,
            n_players : int = 4):
        # A random unique identifier
        self._id : str = secrets.token_hex(16)

        # Meta information related to Gongzhu
        self._n_actions : int = 52 
        # 4 players by default. If I have time, I will implement 3 players version
        self._n_players : int = n_players 
        # 13 rounds for 4 players version
        self._max_rounds : int = 13
        self._round_count : int = 0

        # Observation and action spaces
        self.action_space = Box(0, 1, shape=(52,))

        # Observation space consists of 
        # 1. Information of the agent player (players[0])
        # 2. Other players' information (players[1:4])
        # 3. Game history (List of 52 x 1 one-hot vectors)
        # 4. First player each round (List of indices)
        # Other meta information:
        # 5. Declaration phase (True or False)
        self._render_mode : str = render_mode  # "human" or "rgb_array"

        self.observation_space = Dict(
            {"agent_info": Box(0, 1, shape=(52, 6)), 
            "players_info": Box(0, 1, shape=(3, 52, 6)),
            "history": Sequence(Box(0, 1, shape=(52,))),
            "first_player_indices": Sequence(Discrete(4)),
            "is_declaration_phase": Space()},
        )

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
        self._history : List[Card] = []

        # Scores of both teams
        self._my_team_score : int = 0
        self._opponent_team_score : int = 0

        # Whether declaration is enabled or not
        self._enable_declaration : bool = enable_declaration

        # If declaration is enabled, this variable tells whether it's
        # the declaration phase or not
        self._declaration_phase : bool = enable_declaration

        self._has_moved : List[bool] = [False, False, False, False]

        self._first_player_indices : List[int] = []

        self._suit_rounds : dict[str : int] = {
            "spade": 0,
            "heart": 0,
            "diamond": 0,
            "club": 0,
        }
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
        self._history = []

        # Set the phase to declaration phase
        self._declaration_phase = self._enable_declaration

        self._has_moved = [False, False, False, False]

        self._suit_rounds = {
            "spade": 0,
            "heart": 0,
            "diamond": 0,
            "club": 0,
        }

        self._first_player_indices = [self._first_player_index]
        return self.to_dict()
    
    # Update known declaration effects
    def update_effects(self):
        for player in self._players:
            declarations = player.get_declarations()
            closed_declarations = declarations.get_revealed_closed_declarations()
            open_declarations = declarations.get_open_declarations()
            for card in closed_declarations:
                if card.get_rank() == self.PIG.get_rank():
                    self._pig_effect = 2.0
                elif card.get_rank() == self.SHEEP.get_rank():
                    self._sheep_effect = 2.0
                elif card.get_rank() == self.DOUBLER.get_rank():
                    self._doubler_effect = 2.0
                elif card.get_rank() == self.BLOOD.get_rank():
                    self._blood_effect = 2.0
            for card in open_declarations:
                if card.get_rank() == self.PIG.get_rank():
                    self._pig_effect = 4.0
                elif card.get_rank() == self.SHEEP.get_rank():
                    self._sheep_effect = 4.0
                elif card.get_rank() == self.DOUBLER.get_rank():
                    self._doubler_effect = 4.0
                elif card.get_rank() == self.BLOOD.get_rank():
                    self._blood_effect = 4.0

    # Get current legal moves of the agent
    def agent_legal_moves(self) -> CardCollection:
        agent_hand = self._players[0].get_hand()
        return self.legal_moves(agent_hand, self._playedCardsThisRound)

    # Get the legal moves
    def legal_moves(self, hand : Hand, played_cards : List[Card]) \
        -> CardCollection:
        '''
        Return a CardCollection of legal moves for a given hand and played cards.
        If no cards were played, any card in the hand is legal.
        '''

        # If no cards were played, any card in the hand is legal
        legal_moves = hand if len(played_cards) == 0 else hand.get_cards_by_suit(played_cards[0].get_suit())
        # If no cards of the same suit, then the whole hand is legal
        legal_moves = legal_moves if not legal_moves.is_empty() else hand
        # Special rule: if the suit is the same as an openly declared card,
        # and this suit is not yet played, then this openly declared card
        # is illegal
        legal_moves = CardCollection(cards=legal_moves.cards)
        if len(legal_moves) > 1:
            if self._pig_effect >= 4.0 and PIG in legal_moves and self._suit_rounds['spade'] == 0:
                legal_moves -= PIG
            if self._sheep_effect >= 4.0 and SHEEP in legal_moves and self._suit_rounds['diamond'] == 0:
                legal_moves -= SHEEP
            if self._blood_effect >= 4.0 and BLOOD in legal_moves and self._suit_rounds['heart'] == 0:
                legal_moves -= BLOOD
            if self._doubler_effect >= 4.0 and DOUBLER in legal_moves and self._suit_rounds['club'] == 0:
                legal_moves -= DOUBLER
        return legal_moves
    
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
    def calc_score(self, collected_cards : CardCollection) -> float:
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
        '''
        Check if a move is legal for this round
        '''
        legal_moves = self.legal_moves(player.get_hand(), self._playedCardsThisRound)
        return legal_moves.contains(card)

    def is_legal_declarations(self, player : Player, declarations : Declaration) -> bool:
        hand = player.get_hand()
        # First, check if the player has the declared cards
        open_declarations = CardCollection(declarations.get_open_declarations())
        closed_declarations = CardCollection(declarations.get_all_closed_declarations())
        # print(open_declarations)
        # print(closed_declarations)
        # print([card for card in hand])
        # print(open_declarations in hand)
        # print(closed_declarations in hand)
        if (not open_declarations in hand) or (not closed_declarations in hand):
            return False
        # Ensure there is no intersection between open and closed declarations
        if not open_declarations.intersect(closed_declarations).is_empty():
            return False
        return True

    def next_round(self):
        # print(f"Round {self._round_count} ends")
        # print(f"Length of history is {len(self._history)} ")
        # Sanity check: ensure each player has exactly same number of cards
        assert \
            (len(self._players[0].get_hand()) == len(self._players[1].get_hand()) ) and \
            (len(self._players[0].get_hand()) == len(self._players[2].get_hand()) ) and \
            (len(self._players[0].get_hand()) == len(self._players[3].get_hand()) ), \
            "Error: Different number of cards in hand!"
        # Reset moved flags
        self._has_moved = [False, False, False, False]
        # Check if it is the declaration phase
        if self._declaration_phase:
            self._declaration_phase = False
            self._current_player_index = self._first_player_index
            self.update_effects()
            return 
        # Increase the round count by 1
        self._round_count += 1
        # Find the index of largest player
        largest_index = (self._first_player_index + self.find_largest_index(self._playedCardsThisRound)) % self._n_players
        # The largest player collects all the cards played this round
        self._players[largest_index].add_collected_cards(self._playedCardsThisRound)
        self._players[largest_index].sort_collected_cards()
        # Empty the currentPlayedCard of players
        for player in self._players:
            player.remove_current_played_card()
        # Increase suit round by one
        self._suit_rounds[self._playedCardsThisRound[0].get_suit()] += 1
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
            # Update the list of first player indices
            self._first_player_indices.append(self._current_player_index)

        return {
            "largestIndex": largest_index,
            "newRoundCount": self._round_count,
        }
        
    def next_player(self):
        old_player_index = self._current_player_index
        self._has_moved[old_player_index] = True
        # Check if right now is the declaration phase
        if self.is_declaration_phase():
            print(f"player {old_player_index} is making a declaration")
            declarations : Declaration = self._players[self._current_player_index].policy.decide_declarations(
                hand=self._players[self._current_player_index].get_hand(),
                game_info=self.to_dict()
            )
            self._players[self._current_player_index].set_declarations(declarations)
            self._current_player_index = (self._current_player_index + 1) % self._n_players
            if self.is_end_one_round():
                self.next_round()
            return {
                "currentPlayerIndex": old_player_index,
                "move": declarations.to_dict(),
            }
            pass
        # Play a card based on the policy
        legal_moves = self.legal_moves(self._players[self._current_player_index].get_hand(), self._playedCardsThisRound)
        move : Card = self._players[self._current_player_index].policy.decide_action(
            legal_moves=legal_moves, 
            game_info=self.to_state()
        )
        if move in SPECIAL_CARDS:
            self.update_effects()
        self._playedCardsThisRound.append(move)
        self._players[self._current_player_index].play_specific_card(move)
        # Update the current player index
        self._current_player_index = (self._current_player_index + 1) % self._n_players
        # Update the game history
        self.add_history(move)
        # print(f"Player {old_player_index} played {move}")
        return {
            "currentPlayerIndex": old_player_index,
            "move": move.to_dict(),
        }

    def agent_declarations(self, declarations: Declaration):
        # # For debug purposes
        # return self.next_player() 
        if self.is_legal_declarations(self._players[self._current_player_index], declarations):
            self._has_moved[0] = True
            self._players[self._current_player_index].set_declarations(declarations)
            self._current_player_index = (self._current_player_index + 1) % self._n_players
            if self.is_end_one_round():
                self.next_round()
            return self.to_dict()   
        else:
            return None

    def make_declarations(self, declarations: Declaration):
        return self.agent_declarations(declarations)

    def play_selected_card(self, card : Card):
        # Check if the current player can play this card
        if self.is_legal_move(self._players[self._current_player_index], card):
            self._has_moved[0] = True
            if card in SPECIAL_CARDS:
                self.update_effects()
            self._playedCardsThisRound.append(card)
            self._players[self._current_player_index].play_specific_card(card)
            # Update the current player index
            self._current_player_index = (self._current_player_index + 1) % self._n_players
            # Update the game history
            self.add_history(card)
            return self.to_dict()   
        else:
            return None

    def to_state(self):
        # return self.to_dict()
        return {"agent_info": self._players[0].vec_full, 
            "players_info": np.array([self._players[1].vec_partial,
                 self._players[2].vec_partial,
                 self._players[3].vec_partial]),
            "history": self._history,
            "first_player_indices": self._first_player_indices,
            "is_declaration_phase": self._declaration_phase} 
    
    def is_declaration_phase(self):
        return self._declaration_phase

    def is_end_episode(self) -> bool:
        return self._round_count >= self._max_rounds

    def to_dict(self) -> dict:
        for player in self._players:
            player.get_score(self)
        return {
            "id": self._id,
            "players": [player.to_dict() for player in self._players],
            "roundCount": self._round_count,
            "firstPlayerIndex": self._first_player_index,
            "currentPlayerIndex": self._current_player_index,
            "cardsPlayedThisRound": [card.to_dict() for card in self._playedCardsThisRound],
            "isEndEpisode": self.is_end_episode(),
            "history": [card.to_dict() for card in self._history],
            "firstPlayerIndices": self._first_player_indices,
            "isDeclarationPhase": self._declaration_phase
        }
    
    def get_game_state(self) -> dict:
        return self.to_dict()
    
    def start_game(self) -> None:
        self.start()
        
    def get_current_player_index(self) -> int:
        return self._current_player_index
    
    def get_player_by_index(self, index) -> Player:
        return self._players[index]

    def get_first_player_index(self) -> int:
        return self._first_player_index

    def is_your_turn(self) -> bool:
        return self._current_player_index == 0
    
    def is_end_one_round(self) -> bool:
        return all(self._has_moved)

    def end_episode(self):
        return self.to_dict()

    def add_history(self, move : np.array) -> None:
        self._history.append(move)
    
    def save_histroy(self) -> None:
        # TODO: Implement saving game history
        return

    def get_id(self) -> str:
        return self._id

    def get_played_cards_this_round(self) -> List[Card] :
        return self._playedCardsThisRound
    
    # Some functions related to scoring
    # @property
    def my_team_score(self) -> float:
        return self._players[0].score(self) + self._players[2].score(self)
    
    # @property
    def opponent_team_score(self):
        return self._players[1].score(self) + self._players[3].score(self)
    
    # @property
    def score_diff(self):
        return self.my_team_score() - self.opponent_team_score()

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

    # AI plays the game until the agent's turn
    # Or until the game is over
    def play_until_your_turn(self) -> None:
        # while not self.is_your_turn() or self.is_end_one_round() or self._declaration_phase:
        while not self.is_your_turn() or self.is_end_one_round():
            # print(f"History length is {len(self._history)}")
            if self.is_end_episode():
                break
            if self.is_end_one_round():
                assert len(self._history) % 4 == 0, f"History does not match current played cards! \
                    played cards this round are {self._playedCardsThisRound}"
                self.next_round()
            else:
                self.next_player()

    # Estimate the action value based on a policy
    def action_value_estimate(self, action: Card, policy: Policy) -> float:
        return policy.action_value_estimate(
            legal_moves=self.agent_legal_moves(),
            action=action,
            game_info=self.to_state()
        )

    def step(self, action: ActType) \
        -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        # First, sanity check
        assert self._round_count < self._max_rounds, "More than max rounds"
        assert self.is_your_turn() , \
                f"It's not your turn: player {self._current_player_index}"

        if not self.is_declaration_phase():
            assert action in self.legal_moves(self._players[self._current_player_index].get_hand(), self._playedCardsThisRound), \
                f"Illegal move: {action} for player {self._current_player_index} \
                    Hand of player {self._current_player_index} is \
                    {np.asarray(self._players[self._current_player_index].get_hand())}. \
                        Legal moves are {np.asarray(self.legal_moves(self._players[self._current_player_index].get_hand(), self._playedCardsThisRound))} \
                            Played cards this round are {np.asarray(self._playedCardsThisRound)}"

        score_diff = self.score_diff()

        if not self.is_declaration_phase():
            self.play_selected_card(action)
        else:
            self.make_declarations(action)

        self.play_until_your_turn()

        new_score_diff = self.score_diff()

        # Reward is proportional to the change of advantage over the opponent team
        # If the game is over, the reward is exactly the difference
        reward = new_score_diff - score_diff  
        if not self.is_end_episode():
            reward /= 10
        else:
            reward = new_score_diff

        # Return the new state, reward, and whether the game is over
        return self.to_state(), reward, self.is_end_episode(), False, {}
    
    def reset(self, ai_players : List[Player] = [], auto : bool = True,
        seed=None) -> ObsType:
        assert len(ai_players) == 0 or len(ai_players) == 4, "Please specify exactly four players. The first player is you."
        # If the ai players are not specified, 
        if len(ai_players) == 0:
            self._players = [
                Player(id="You", name="You", avatar_url="avatar_url1", 
                policy=RandomPolicy(env=self)),
                Player(id="Panda", name="Panda", avatar_url="avatar_url2", 
                policy=RandomPolicy(env=self)),
                Player(id="Penguin", name="Penguin", avatar_url="avatar_url3",
                policy=RandomPolicy(env=self)),
                Player(id="Elephant", name="Elephant", avatar_url="avatar_url4",
                policy=RandomPolicy(env=self)),
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

        if auto:
            self.play_until_your_turn()

        return self.to_state(), {"enable_declaration": self._enable_declaration}
    
    # Maybe not need rn?
    def render(self, mode='human'):
        pass

    # Maybe not needed rn?
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


# Archaic implementation
# from .card import Hand, Card, CardCollection, Deck
# from .player import Player
# from typing import List, TYPE_CHECKING
# from .policy import Policy, RandomPolicy
# import sqlite3
# import json
# import os

# DB_DIR = os.path.join("/data/record.db")
# # Game environment class to manage game rules and state.
# class Env:
#     # Class-level variables for round count and number of players

#     def __init__(self):
#         # Initialize round count and number of players
#         self.num_players = 0
#         # Initialize allPlayedCards as a CardCollection instance
#         self.all_played_cards = CardCollection()

#     def get_all_played_cards(self):
#         return self.all_played_cards

#     def add_cards_to_played_cards(self, cards):
#         # Add cards to the collection
#         if isinstance(cards, CardCollection):
#             self.all_played_cards.add_cards_from_collection(cards)
#         elif isinstance(cards, list):
#             self.all_played_cards.add_cards(cards)
#         else:
#             raise ValueError("Invalid type for cards. Must be CardCollection or list of Card objects.")

#     def get_num_players(self):
#         return Env.num_players

#     def set_num_players(self, n):
#         Env.num_players = n

#     def calc_score(self, collected_cards):
#         raise NotImplementedError("'calc_score' not yet implemented.")

#     def legal_moves(self, hand, played_cards):
#         raise NotImplementedError("'legal_moves' not yet implemented.")

# class BloodCard:
#     def __init__(self, rank, score):
#         self.rank = rank
#         self.score = score

#     def get_rank(self):
#         return self.rank

#     def get_score(self):
#         return self.score


# class Gongzhu(Env):
#     # Define 4 important cards
#     PIG = Card("12", "spade")
#     SHEEP = Card("11", "diamond")
#     DOUBLER = Card("10", "club")
#     BLOOD = Card("14", "heart")

#     # Define blood cards with their scores
#     BLOOD_CARDS = [
#         BloodCard("02", 0),
#         BloodCard("03", 0),
#         BloodCard("04", 0),
#         BloodCard("05", 10),
#         BloodCard("06", 10),
#         BloodCard("07", 10),
#         BloodCard("08", 10),
#         BloodCard("09", 10),
#         BloodCard("10", 10),
#         BloodCard("11", 20),
#         BloodCard("12", 30),
#         BloodCard("13", 40),
#         BloodCard("14", 50),
#     ]

#     # Define the first card
#     FIRST_CARD = Card("02", "spade")

#     def __init__(self):
#         super().__init__()
#         self.max_round = 13
#         self.set_num_players(4)
        
#         # Initialize the effects of each special card
#         self.pig_effect = 1.0
#         self.sheep_effect = 1.0
#         self.doubler_effect = 1.0
#         self.blood_effect = 1.0

#     def calc_score(self, collected_cards : CardCollection):
#         score = 0
#         has_pig = False
#         has_sheep = False
#         has_doubler = False
#         has_all_blood = True
#         no_blood = True

#         # Score of pig
#         if collected_cards.contains(Gongzhu.PIG):
#             score -= 100.0 * self.pig_effect
#             has_pig = True

#         # Score of sheep
#         if collected_cards.contains(Gongzhu.SHEEP):
#             score += 100.0 * self.sheep_effect
#             has_sheep = True

#         # Score of blood
#         blood_score_total = 0
#         for blood_card in Gongzhu.BLOOD_CARDS:
#             card = Card(blood_card.get_rank(), "heart")
#             if collected_cards.contains(card):
#                 blood_score_total += blood_card.get_score()
#                 no_blood = False
#             else:
#                 has_all_blood = False

#         if has_all_blood:
#             score += blood_score_total * self.blood_effect
#         else:
#             score -= blood_score_total * self.blood_effect

#         # Score of doubler
#         if collected_cards.contains(Gongzhu.DOUBLER):
#             has_doubler = True

#         # Bonus if collected everything
#         if has_pig and has_sheep and has_all_blood and has_doubler:
#             score += 200.0 * self.pig_effect

#         # Effect of doubler
#         if has_doubler:
#             if not has_pig and not has_sheep and no_blood:
#                 score += 50 * self.doubler_effect
#             else:
#                 score *= 2 * self.doubler_effect

#         return score

#     def legal_moves(self, hand : Hand, played_cards : List[Card]) -> CardCollection:
#         if len(played_cards) == 0:
#             return hand

#         legal_moves = hand.get_cards_by_suit(played_cards[0].get_suit())
#         return legal_moves if not legal_moves.is_empty() else hand

#     def go_first(self, player : Player):
#         return player.get_hand().contains(Gongzhu.FIRST_CARD)

#     # Find the index of the player who goes first in the beginning of the game
#     def who_goes_first_initial(self, players : List[Player]) -> int:
#         # Find the index of the player who goes first
#         for i in range(len(players)):
#             if self.go_first(players[i]):
#                 return i
#         return -1  # No player goes first

#     # find the index of the player who played the largest card
#     def find_largest_index(self, played_cards : List[Card]) -> int:
#         largest_card = played_cards[0]
#         index = 0
#         for i in range(1, len(played_cards)):
#             card = played_cards[i]
#             if card.get_suit() != largest_card.get_suit():
#                 continue
#             if card > largest_card:
#                 largest_card = card
#                 index = i
#         return index
    
#     def find_largest_card(self, played_cards : List[Card]):
#         # Return None if no card has been played yet
#         if len(played_cards) == 0:
#             return None
#         largest_card = played_cards[0]
#         for i in range(1, len(played_cards)):
#             card = played_cards[i]
#             if card.get_suit() != largest_card.get_suit():
#                 continue
#             if card > largest_card:
#                 largest_card = card
#         return largest_card

# class GongzhuGame:
#     def __init__(self, ai_policy : Policy = RandomPolicy, db_dir=None):
#         import secrets
#         # A random unique identifier
#         self.id : str = secrets.token_hex(16)

#         self.env = Gongzhu()
#         self.round_count = 0
#         self.first_player_index = 0  # Index of the player who played first in this round
#         self.current_player_index = 0  # Index of the current player in this round
#         self.players : List[Player] = [
#             Player(id="You", name="You", avatar_url="avatar_url1"),
#             Player(id="Panda", name="Panda", avatar_url="avatar_url2"),
#             Player(id="Penguin", name="Penguin", avatar_url="avatar_url3"),
#             Player(id="Elephant", name="Elephant", avatar_url="avatar_url4"),
#         ]
#         # Policy for AI players
#         self.ai_policy = ai_policy(self.env)
#         self.playedCardsThisRound : List[Card] = [] # List of cards played this round

#         # Game history information
#         self.history = []

#         # Database directory for storing game history
#         self.db_dir = DB_DIR if db_dir is None else db_dir

#         # 
#         self.allow_declarations = False
#     def get_id(self):
#         return self.id

#     def get_round_count(self):
#         return self.round_count

#     def inc_round_count(self):
#         self.round_count += 1
    
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
#         }

#     def get_history(self) -> List[dict]:
#         return self.history

#     def save_histroy(self):
#         # from dotenv import load_dotenv
#         # import os
#         recordHistory = os.getenv('RECORD_HISTORY')
#         if recordHistory != 'True':
#             return
#         # import edgedb

#         # load_dotenv()

#         # secret_key = os.getenv("EDGEDB_SECRET_KEY")
#         # instance = os.getenv("EDGEDB_INSTANCE")
#         # # Connect to the database
#         # client = edgedb.create_client(instance, secret_key=secret_key)
#         conn = sqlite3.connect(self.db_dir)
#         cursor = conn.cursor()
        
#         # Create a table with a JSON column
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS data (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 game_id TEXT,
#                 ai_policy TEXT,
#                 allow_declarations BOOLEAN,
#                 history TEXT
#             )
#         ''')
#         conn.commit()

#         # Save the game state to the database
#         game_id = self.get_id()
#         ai_policy = str(self.ai_policy)
#         allow_declarations = self.allow_declarations
#         history = json.dumps(self.get_history())
#         cursor.execute('INSERT INTO data (game_id, ai_policy, allow_declarations, history) VALUES (?, ?, ?, ?)', 
#             (game_id, ai_policy, allow_declarations, history))
        
#         conn.commit()
#         conn.close()
    
#     def get_game_state(self) -> dict:
#         return self.to_dict()

#     def start(self):
#         # First, deal cards to players
#         deck = Deck()
#         deck.shuffle()
#         for player in self.players:
#             for _ in range(13):
#                 player.add_card_to_hand(deck.deal_card())
#             player.sort_hand()

#         self.round_count = 0
#         self.playedCardsThisRound = []
#         # Figure out the first player initially
#         self.first_player_index = self.env.who_goes_first_initial(self.players)
#         self.current_player_index = self.first_player_index
        
#         # Initialize the game history
#         self.history = []

#         return self.to_dict()
    
#     def start_game(self):
#         self.start()
        
#     def get_current_player_index(self) -> int:
#         return self.current_player_index
    
#     def get_first_player_index(self) -> int:
#         return self.first_player_index

#     def is_end_episode(self) -> bool:
#         return self.round_count >= self.env.max_round

#     def is_your_turn(self) -> bool:
#         return self.current_player_index == 0
    
#     def is_end_one_round(self) -> bool:
#         return len(self.playedCardsThisRound) >= 4

#     def end_episode(self):
#         return self.to_dict()

#     def add_history(self, record : dict):
#         self.history.append(record)


#     # Check if a move is legal for this round
#     def is_legal_move(self, player : Player, card : Card) -> bool:
#         legal_moves = self.env.legal_moves(player.get_hand(), self.playedCardsThisRound)
#         return legal_moves.contains(card)


#     def next_round(self):
#         # Sanity check: ensure each player has exactly same number of cards
#         assert \
#             (len(self.players[0].get_hand()) == len(self.players[1].get_hand()) ) and \
#             (len(self.players[0].get_hand()) == len(self.players[2].get_hand()) ) and \
#             (len(self.players[0].get_hand()) == len(self.players[3].get_hand()) ), \
#             "Error: Different number of cards in hand!"
#         # Increase the round count by 1
#         self.round_count += 1
#         # Find the index of largest player
#         largest_index = (self.first_player_index + self.env.find_largest_index(self.playedCardsThisRound)) % len(self.players)
#         # The largest player collects all the cards played this round
#         self.players[largest_index].add_collected_cards(self.playedCardsThisRound)
#         self.players[largest_index].sort_collected_cards()
#         # Empty the currentPlayedCard of players
#         for player in self.players:
#             player.remove_current_played_card()
#         # Empty the played cards of this round
#         self.playedCardsThisRound = []
#         # Update the current player index
#         if (self.is_end_episode()):
#             self.first_player_index = -1
#             self.current_player_index = -1
#             # # Save the game history
#             # print("Saving game history...")
#             self.save_histroy()
#         else:
#             self.first_player_index = largest_index
#             self.current_player_index = largest_index
        
#         self.add_history({
#             "round": self.round_count,
#             "largestIndex": largest_index,
#         })

#         return {
#             "largestIndex": largest_index,
#             "newRoundCount": self.round_count,
#         }
        
#     def next_player(self):
#         # Play a card based on the policy
#         old_player_index = self.current_player_index
#         legal_moves = self.env.legal_moves(self.players[self.current_player_index].get_hand(), self.playedCardsThisRound)
#         move : Card = self.ai_policy.decide_action(legal_moves=legal_moves, game_info=self.to_dict())
#         self.playedCardsThisRound.append(move)
#         self.players[self.current_player_index].play_specific_card(move)
#         # Update the current player index
#         self.current_player_index = (self.current_player_index + 1) % len(self.players)
#         # Update the game history
#         self.add_history({
#             "round": self.round_count,
#             "playerIndex": old_player_index,
#             "move": move.to_dict(),
#         })
        
#         return {
#             "currentPlayerIndex": old_player_index,
#             "move": move.to_dict(),
#         }

#     def play_selected_card(self, card : Card):
#         # Check if the current player can play this card
#         if self.is_legal_move(self.players[self.current_player_index], card):
#             self.playedCardsThisRound.append(card)
#             self.players[self.current_player_index].play_specific_card(card)
#             # Update the current player index
#             self.current_player_index = (self.current_player_index + 1) % len(self.players)
#             # Update the game history
#             self.history.append({
#                 "round": self.round_count,
#                 "playerIndex": 0,
#                 "move": card.to_dict(),
#             })
#             return self.to_dict()   
#         else:
#             return None

#     def declaration(self):
#         # TODO: Implement declaration phase
#         pass

# class GongzhuGameMultiround(GongzhuGame):
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