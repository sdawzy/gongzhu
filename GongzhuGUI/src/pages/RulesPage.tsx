import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import Card from '../components/Card'
import {PIG, SHEEP, BLOOD, BlOODS, DOUBLER, SPECIAL_CARDS} from '../components/specialCards'
import Hand from '../components/Hand'
import { CardInterface } from '../types';

// const PIG : CardInterface = { suit : "spade", rank : "Queen", id : "spade_12"}
// const SHEEP : CardInterface = { suit : "diamond", rank : "Jack", id : "diamond_11"}
// const DOUBLER : CardInterface = { suit : "club", rank : "10", id : "club_10"}


const HandExample1: CardInterface[] = [
  PIG,
  BlOODS[2],
  BlOODS[7]
]

const HandExample2: CardInterface[] = [
  SHEEP,
  BlOODS[12],
  BlOODS[8],
  DOUBLER
]

const HandExample3: CardInterface[] = [...BlOODS, PIG]
const RulesPage: React.FC = () => {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      <Text style={styles.title}>Rules of Gongzhu</Text>
      <Text style={styles.title}>By Yue Zhang</Text>
      <Text style={styles.text}>
        Gongzhu (lit. "Pushing the Pig") is a traditional Chinese card game. It is usually played by 4 players with the standard deck of 52 playing cards. 
         The goal of Gongzhu is to score the highest points by<Text style={styles.highlight}> avoiding penalty cards</Text>  and <Text style={styles.highlight}>collecting beneficial ones</Text>.
      </Text>

      <Text style={styles.sectionTitle}>Gameplay</Text>
      <Text style={styles.text}>
        1. The game is played with 4 players and a standard deck of 52 cards.
      </Text>
      <Text style={styles.text}>
        2. Cards are dealt equally to all players, with each player receiving 13 cards.
      </Text>
      <Text style={styles.text}>
        3. Players take turns playing one card each. The first card determines the suit for that round.
      </Text>
      <Text style={styles.text}>
        4. <Text style={styles.highlight}>Players must follow suit if possible</Text>. If a player cannot follow suit, they may play any card.
      </Text>
      <Text style={styles.text}>
        5. The highest card of the lead suit wins the round, and the winner collects all cards played. Note that Ace is the largest and 2 is the smallest in any suit. 
      </Text>

      <Text style={styles.sectionTitle}>Card Values</Text>
      <Text style={styles.text}>The following cards have special values:</Text>
      <Text style={styles.bulletedList}>- Queen of Spade (♠): <Text style={styles.highlight}>Known as the Pig.</Text> Its value is <Text style={styles.highlight}>-100</Text> points. Try your best to avoid collecting the Pig!</Text>
      <Card card={PIG}/>
      <Text style={styles.bulletedList}>- Jack of Diamond (♦): <Text style={styles.highlight}>Known as the Sheep.</Text> Its value is <Text style={styles.highlight}>+100</Text> points. Try your best to catch the Sheep!</Text>
      <Card card={SHEEP}/>
      <Text style={styles.bulletedList}>- Hearts (♥): <Text style={styles.highlight}>Known as the Bloods.</Text> Most of heart cards have negative points. </Text>
      <Hand hand={BlOODS} spacing={100} selectable={false}/>
      <Text style={styles.bulletedList}>  - 2, 3 and 4 of Heart have no values. </Text>
      <Hand hand={BlOODS.slice(0,3)} spacing={100} selectable={false}/>
      <Text style={styles.bulletedList}>  - 5 to 10 of Heart are <Text style={styles.highlight}>-10</Text> points each. </Text>
      <Hand hand={BlOODS.slice(3,9)} spacing={100} selectable={false}/>
      <Text style={styles.bulletedList}>  - Jack, Queen, King and Ace of Heart worth <Text style={styles.highlight}>-20, -30, -40 and -50</Text> points, respectively. </Text>
      <Hand hand={BlOODS.slice(9,13)} spacing={100} selectable={false}/>
      <Text style={styles.bulletedList}>- Ten of Club (♣): <Text style={styles.highlight}>Known as the Doubler.</Text> Your score will double if you collect the Doubler, no matter it is positive or negative.</Text>
      <Card card={DOUBLER}/>
      <Text style={styles.bulletedList}>- All the other cards do not have any values.</Text>


      <Text style={styles.sectionTitle}>Score Calculation</Text>
      <Text style={styles.text}>
        After each game, the score of each player is determined by their collected cards that have values. It is simply <Text style={styles.highlight}>the sum of the values</Text> of each card. If they have the Doubler (10 of Club), the score would double.
      </Text>
      <Text style={styles.sectionSubTitle}>Special Situations</Text>
      <Text style={styles.bulletedList}>- If a player collects <Text style={styles.highlight}>only the Doubler</Text>, without the Pig, the Sheep, nor any Blood, the Doubler will worth +50 points.</Text>
      <Text style={styles.bulletedList}>- If a player collects <Text style={styles.highlight}>all the hearts</Text> including 2, 3 and 4, the values of the hearts will become positive. (+200 points in total) </Text>
      <Text style={styles.bulletedList}>- If a player collects <Text style={styles.highlight}>the Pig, the Sheep, the Doubler and all the hearts</Text> including 2, 3 and 4, the values of the pig will become positive. (+100 points) </Text>
      <Text style={styles.sectionSubTitle}> Example 1</Text>
      <Text style={styles.bulletedList}>The score of the following player is -100-0-10=-110. </Text>
      <Hand hand={HandExample1} spacing={100} selectable={false}/>
      <Text style={styles.sectionSubTitle}> Example 2</Text>
      <Text style={styles.bulletedList}>The score of the following player is (+100-50-10)*2=+80. </Text>
      <Hand hand={HandExample2} spacing={100} selectable={false}/>
      <Text style={styles.sectionSubTitle}> Example 3</Text>
      <Text style={styles.bulletedList}>The score of the following player is +200-100=+100. </Text>
      <Hand hand={HandExample3} spacing={100} selectable={false}/>



      <Text style={styles.sectionTitle}>Winning and Losing</Text>
      <Text style={styles.text}>
        You and the player directly opposite you are teammates. Your team's score is the <Text style={styles.highlight}>combined total</Text> of both players' individual scores.
      </Text>
      <Text style={styles.text}>
        The game is typically played across multiple rounds, with scores for both teams accumulating over time. The game continues until one team's score reaches or exceeds +1000 points, or falls to or below -1000 points.
      </Text>
      <Text style={styles.text}>
      <Text style={styles.highlight}>A team wins by reaching or exceeding +1000 points. Conversely, a team loses if their score falls to or below -1000 points.</Text>
      </Text>

      <Text style={styles.sectionTitle}>Declaration Mode</Text>
      <Text style={styles.text}>
       To make the game more exciting, you can <Text style={styles.highlight}>enable card declarations</Text> in the beginning of the game!
       Now there is an extra <Text style={styles.highlight}>declaration phase</Text> before the first round of game. During the declaration phase, 
       each player takes turns to decide whether to <Text style={styles.highlight}>declare special card(s)</Text> in their hand.
      </Text>
      <Text style={styles.text}>
       The special cards are <Text style={styles.highlight}>the Pig, the Sheep, the Big Blood (Ace of Heart) and the Doubler.</Text>
      </Text>  
      <Hand hand={SPECIAL_CARDS} spacing={100} selectable={false}/>
      <Text style={styles.text}>
       If a player decides to declare one of those special cards, they can either declare it <Text style={styles.highlight}>secretly (closedly)</Text> or <Text style={styles.highlight}>openly</Text>. 
      </Text>
      <Text style={styles.bulletedList}> - A <Text style={styles.highlight}>secretly delcared</Text> card has <Text style={styles.highlight}>doubled (times 2)</Text> effect. 
      That is to say, a secretly declared Pig is -200 instead of -100, a secretly declared Sheep is +200 instead of +100, a secretly declared Doubler quadruple one's score, and 
      a secretly declared Big Blood causes all Bloods' scores to double. 
      When one secretly declares a card, they does not need to show that card until that card is played. </Text>
      <Text style={styles.bulletedList}> - A <Text style={styles.highlight}>openly delcared</Text> card has <Text style={styles.highlight}>quadrupled (times 4)</Text> effect!  
      When one secretly declares a card, they must always show that declared card. </Text>
      <Text style={styles.text}>
       Note that in order to prevent openly declared cards from being too overpowered,
       <Text style={styles.highlight}>it is not allowed to play an openly card in the first round of the suit of that card (unless that card is the only one in that suit).</Text> 
       For example, one cannot play an openly declared Pig in the first round of spade, or an openly declared Doubler in the first round of Heart.
      </Text>      
      
      <Text style={styles.sectionTitle}>Have fun playing Gongzhu!</Text>
      {/* <Text style={styles.sectionTitle}>Tips</Text>
      <Text style={styles.text}>
        - Avoid collecting penalty cards like the Queen of Spades and Hearts.
      </Text>
      <Text style={styles.text}>
        - Try to win the Jack of Diamonds and the Ten of Clubs for bonus points.
      </Text>
      <Text style={styles.text}>
        - Keep track of cards that have already been played to make strategic decisions.
      </Text> */}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  contentContainer: {
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#343a40',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 20,
    marginBottom: 10,
    color: '#495057',
  },
  sectionSubTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 20,
    marginBottom: 10,
    color: '#222222',
  },
  text: {
    fontSize: 16,
    lineHeight: 24,
    color: '#212529',
    marginBottom: 10,
  },
  bulletedList: {
    fontSize: 16,
    lineHeight: 24,
    color: '#212529',
    marginLeft: 20,
  },
  highlight: {
    backgroundColor: '#FFFF99', // Light yellow background
    color: '#000', // Black text color
    fontWeight: 'bold',
    paddingHorizontal: 2,
    borderRadius: 4,
  },
  strongHighlight: {
    backgroundColor: '#FF9999', // Light red background
    color: '#fff', // White text color
    paddingHorizontal: 4,
    borderRadius: 4,
    fontWeight: 'bold',
  },
});

export default RulesPage;