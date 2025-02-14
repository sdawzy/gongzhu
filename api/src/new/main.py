import random
# from .player_new import Player
from env_new import Gongzhu
from card import Card, CardCollection, Hand, Deck
import argparse
import numpy as np
from policy import RandomPolicy

def emulate():
    pass

def play_game():
    game = Gongzhu()
    state, _ = game.reset()
    round_count = 0
    policy = RandomPolicy(game)
    reward = 0
    while not game.is_end_episode():
        print(f"Round {round_count}")
        # print(state)
        # isYourTurn = game.is_your_turn()
        # isEndOneRound = game.is_end_one_round()
        # currentPlayerIndex = game.get_current_player_index()
        # action = input(f"{game._players[currentPlayerIndex].get_name()}, your turn (0: pass, 1: play): ")
        # Retrive hands state
        hand : np.ndarray = state["agent_info"][0].view(Hand)
        played_cards = state["history"][round_count * 4 :]
        # print(f"played cards : {played_cards}")
        action = policy.decide_action(legal_moves=game.legal_moves(hand=hand,
                        played_cards=played_cards))
        print(f"Action: {action}")
        state, reward, terminated, _, _ = game.step(action=action)
        print(f"Reward from this round: {reward}")
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        round_count += 1
        if terminated:
            break
        
# def emulate():
#     deck = Deck()
#     deck.shuffle()
#     env = Gongzhu()
#     players = [Player("Alice"), Player("Bob"), Player("Carl"), Player("Dave")]

#     for i in range(52):
#         players[i % 4].add_card_to_hand(deck.deal_card())

#     for player in players:
#         player.sort_hand()
#         player.show_hand()

#     host = 0
#     for i, player in enumerate(players):
#         if env.go_first(player):
#             host = i
#             break

#     for i, player in enumerate(players):
#         env.declaration(players[(i + host) % 4])

#     round_count = env.get_round_count()
#     while round_count < 13:
#         env.inc_round_count()
#         round_count = env.get_round_count()
#         print(f"----ROUND {round_count}------")
#         played_cards = []

#         for i in range(4):
#             player_index = (i + host) % 4
#             played_card = players[player_index].get_legal_moves(env, played_cards).get_one_random_card()
#             players[player_index].play_specific_card(played_card)
#             played_cards.append(played_card)

#         largest_index = env.find_largest(played_cards)
#         host = (host + largest_index) % 4
#         players[host].add_collected_cards(played_cards)
#         print(f"{players[host].name} was the largest.")
#         print(f"----END ROUND {round_count}------\n")

#     for player in players:
#         player.show_collected_cards()
#         score = player.get_score(env)
#         print(f"Score of {player.name} is {score}\n")


# def play():
#     YOU = 3
#     deck = Deck()
#     deck.shuffle()
#     env = Gongzhu()
#     players = [Player("Alice"), Player("Bob"), Player("Carl"), Player("You")]

#     for i in range(52):
#         players[i % 4].add_card_to_hand(deck.deal_card())

#     players[YOU].sort_hand()
#     players[YOU].show_hand()

#     # Decide who plays first
#     host = 0
#     for i, player in enumerate(players):
#         if env.go_first(player):
#             host = i
#             break
#     print(f"{players[host].name} plays first.")

#     # Make declarations
#     for i in range(4):
#         player_index = (i + host) % 4
#         if player_index == 3:
#                 # Mapping of option to (card, effect attribute, messages)
#             declaration_map = {
#                 1: ("PIG", "pig_effect", "You don't have the Pig!", "You secretly declared the Pig.", "You openly declared the Pig."),
#                 2: ("SHEEP", "sheep_effect", "You don't have the Sheep!", "You secretly declared the Sheep.", "You openly declared the Sheep."),
#                 3: ("DOUBLER", "doubler_effect", "You don't have the Doubler!", "You secretly declared the Doubler.", "You openly declared the Doubler."),
#                 4: ("BLOOD", "blood_effect", "You don't have the Blood!", "You secretly declared the Blood.", "You openly declared the Blood.")
#             }

#             while True:
#                 # Get the declaration option
#                 print("Do you want to declare anything?")
#                 print("0 for no declaration")
#                 print("1 for pig")
#                 print("2 for sheep")
#                 print("3 for doubler")
#                 print("4 for blood")
                
#                 try:
#                     opt = int(input())  # Getting user input for the option
#                     if opt < 0 or opt > 4:
#                         print("Invalid option. Please select a valid option.")
#                         continue
#                 except ValueError:
#                     print("Invalid input! Please enter a number.")
#                     continue
                
#                 if opt == 0:
#                     break
                
#                 # Ask for open declaration if the option is not 0
#                 print("Open declare? 1 for yes, 0 for no")
#                 try:
#                     open_declare = int(input())  # Getting input for open declare
#                 except ValueError:
#                     print("Invalid input! Please enter 0 or 1.")
#                     continue

#                 # Validate if open_declare is either 0 or 1
#                 if open_declare not in [0, 1]:
#                     print("Invalid input for open declare. Please enter 0 or 1.")
#                     continue
                
#                 # Fetch the card and effect related to the selected option
#                 if opt in declaration_map:
#                     card, effect_attr, no_card_msg, secret_msg, open_msg = declaration_map[opt]

#                     # Check if player has the card and apply effects
#                     if card in players[3].hand.cards:
#                         # Set the effect to 2 initially
#                         setattr(env, effect_attr, 2)
#                         if open_declare == 1:
#                             setattr(env, effect_attr, getattr(env, effect_attr) * 2)
#                             print(open_msg)
#                         else:
#                             print(secret_msg)
#                     else:
#                         print(no_card_msg)
#                 else:
#                     print("Invalid Declaration!")
#         else:
#             env.declaration(players[player_index])


#     round = env.get_round_count()
#     while round < 13:
#         env.inc_round_count()
#         round = env.get_round_count()
#         print(f"----ROUND {round}------")
#         played_cards = []

#         # Play cards one by one
#         for i in range(4):
#             played_card = None
#             player_index = (i + host) % 4
            
#             if player_index == YOU:
#                 made_valid_move = False
#                 while not made_valid_move:
#                     players[player_index].show_hand()
#                     legal_moves = players[player_index].get_legal_moves(env, played_cards)
#                     print("Which one you wanna play? [Suit] [Rank]: ")
#                     suit, rank = input().split()
#                     try:
#                         candidate = Card(rank, suit)
#                     except:
#                         print("Ilegal Card!")
#                         continue

#                     if candidate in legal_moves:
#                         played_card = candidate
#                         made_valid_move = True
#                     else:
#                         print("Ilegal Move!")
#             else:
#                 played_card = players[player_index].get_legal_moves(env, played_cards).get_one_random_card()

#             players[player_index].play_specific_card(played_card)
#             played_cards.append(played_card)
#             print(f"{players[player_index].get_name()} played {played_card}")

#         # Find which one is largest
#         largest_index = env.find_largest(played_cards)
        
#         # Update host
#         host = (host + largest_index) % 4
#         players[host].add_collected_cards(played_cards)
#         print(f"{players[host].get_name()} was the largest.")
#         print(f"----END ROUND {round}------\n")


#     for player in players:
#         player.show_collected_cards()
#         score = player.get_score(env)
#         print(f"Score of {player.name} is {score}\n")


if __name__ == "__main__":
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Choose to emulate or play the game.")
    
    # Add arguments
    parser.add_argument(
        "--mode", 
        choices=["emulate", "play"],  # Restrict to 'emulate' or 'play'
        default="play",  # Default is play
        help="Choose the mode of the game (emulate or play)"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Call the appropriate function based on the argument
    if args.mode == "emulate":
        emulate()  # Call emulate
    elif args.mode == "play":
        play_game()  # Call play
