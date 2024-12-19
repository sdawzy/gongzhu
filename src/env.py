from card import Hand, Card, CardCollection
# from player import Player
from typing import List

class Env:
    # Class-level variables for round count and number of players
    round_count = 0
    num_players = 0

    def __init__(self):
        # Initialize allPlayedCards as a CardCollection instance
        self.all_played_cards = CardCollection()

    def get_round_count(self):
        return Env.round_count

    def inc_round_count(self):
        Env.round_count += 1

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
    PIG = Card("Queen", "Spade")
    SHEEP = Card("Jack", "Diamond")
    DOUBLER = Card("10", "Club")
    BLOOD = Card("Ace", "Heart")

    # Define blood cards with their scores
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
    FIRST_CARD = Card("2", "Spade")

    def __init__(self):
        super().__init__()
        self.set_num_players(4)
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
            card = Card(blood_card.get_rank(), "Heart")
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

    def legal_moves(self, hand : Hand, played_cards : List[Card]):
        if len(played_cards) == 0:
            return hand

        legal_moves = hand.get_cards_by_suit(played_cards[0].get_suit())
        return legal_moves if not legal_moves.is_empty() else hand

    def apply_effect(self, player, target_card : Card, 
                    suit, effect, card_name):
        if player.get_hand().contains(target_card):
            cards_by_suit = player.get_hand().get_cards_by_suit(suit)
            suit_count = cards_by_suit.size()

            if suit_count == 4:
                effect = 2.0
                print(f"{player.get_name()} secretly declared something.\n")
            if suit_count >= 5:
                effect = 4.0
                print(f"{player.get_name()} openly declared the {card_name}.\n")

        return effect

    def declaration(self, player):
        self.pig_effect = self.apply_effect(player, Gongzhu.PIG, "Spade", self.pig_effect, "Pig")
        self.sheep_effect = self.apply_effect(player, Gongzhu.SHEEP, "Diamond", self.sheep_effect, "Sheep")
        self.doubler_effect = self.apply_effect(player, Gongzhu.DOUBLER, "Club", self.doubler_effect, "Doubler")
        self.blood_effect = self.apply_effect(player, Gongzhu.BLOOD, "Heart", self.blood_effect, "Blood")

    def go_first(self, player):
        return player.get_hand().contains(Gongzhu.FIRST_CARD)

    def find_largest(self, played_cards : List[Card]):
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
