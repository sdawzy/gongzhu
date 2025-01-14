import React, { useState } from 'react';
import { View, Text, Button, StyleSheet, Image } from 'react-native';
import Card from '../components/Card';
import Hand from '../components/Hand';
import { CardInterface, PlayerInterface } from '../types';
import GameTable from '../components/GameTable';
// import {  } from '../types';
// Helper function to generate a deck of cards
const generateDeck = () => {
  const suits = ['spade', 'heart', 'diamond', 'club'];
  const ranks = ['02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14'];
  let deck = [];

  suits.forEach(suit => {
    ranks.forEach(rank => {
      deck.push({ suit, rank, id: `${suit}_${rank}` });
    });
  });

  return deck;
};

// Helper function to shuffle the deck
const shuffleDeck = (deck) => {
  return deck.sort(() => Math.random() - 0.5);
  // return deck;
};

// Helper function to deal cards to players
const dealCards = (deck) => {
  const hands = [[], [], [], []];
  deck.forEach((card, index) => {
    hands[index % 4].push(card);
  });
  // Sort hands
  for (let i = 0; i < 4; i++) {
    hands[i].sort((a, b) => a.id < b.id? -1 : 1);  
  }
  return hands;
};

const GameOnline : React.FC = () => {
  const [hands, setHands] = useState([]);
  const [currentPlayer, setCurrentPlayer] = useState(0); // Track the current player
  // setCurrentPlayer(1);

  const startGame = () => {
    const deck = shuffleDeck(generateDeck());
    const dealtPlayers = dealCards(deck);
    setHands(dealtPlayers);
  };

  const playerInfo = [
    { name: 'You', avatar: require('../../assets/images/avatars/You.png') },
    { name: 'Mr. Panda', avatar: require('../../assets/images/avatars/Panda.png') },
    { name: 'Mr. Penguin', avatar: require('../../assets/images/avatars/Penguin.png') },
    { name: 'Mrs. Elephant', avatar: require('../../assets/images/avatars/Elephant.png') },
  ]

  const collectedCards : CardInterface[][] = [
    [{suit : 'spade', rank : "02", id : 'spade_02'}, {suit : 'club', rank : "10", id : 'club_02'}], // Player 1
    [{suit : 'heart', rank : "02", id : 'heart_02'}], // Player 2
    [{suit : 'diamond', rank : "02", id : 'diamond_02'}], // Player 3
    [], // Player 4
  ]

  const openDeclaredCards : CardInterface[][] = [
    [{suit : 'heart', rank : "02", id : 'heart_02'}], // Player 1
    [{suit : 'club', rank : "10", id : 'club_10'}], // Player 2
    [{suit : 'diamond', rank : "02", id : 'diamond_02'}], // Player 3
    [{suit : 'club', rank : "02", id : 'club_02'}], // Player 4
  ]


  const currentPlayedCards : (CardInterface | null) [] = [
    {suit : 'diamond', rank : "14", id : 'diamond_14'}, // Player 1
    {suit : 'diamond', rank : "06", id : 'diamond_06'}, // Player 2
    {suit : 'diamond', rank : "11", id : 'diamond_11'}, // Player 3
    {suit : 'diamond', rank : "12", id : 'diamond_12'}, // Player 4
  ]
  
  const scores : number[] = [100, -20, 30, 60];

  const players : PlayerInterface[] = hands.map((hand, index) => ({
      name: playerInfo[index].name,
      avatar: playerInfo[index].avatar,
      hand: hand,
      collectedCards: [],
      playedCards: [],
      currentPlayedCard: null,
    }));

  return (
    <View style={styles.container}>
      {players.length === 0 ? (
        <View>        
            <Hand 
              hand={generateDeck()} 
              rotation={0}
              visible={false}
            />
            <Button title="Start Game" onPress={startGame} />
        </View>
      ) : (
        <GameTable 
          initialPlayers={players} 
          online={true}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  tableContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#008000', // Green table background like a card table
  },
  playerContainer: {
    position: 'absolute',
    alignItems: 'center',
  },
  container: {
    flex: 1,
    justifyContent: 'flex-end',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#f0f8ff',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center',
  },
  card: {
    fontSize: 18,
    textAlign: 'center',
    marginVertical: 4,
    color: '#333',
  },
  cardWrapper: {
    position: 'absolute', // Allow overlapping
    zIndex: 1, // Ensure overlapping is in order of the cards
  },
  listContent: {
    // alignItems: 'center',
    height: '100%',
  },
  topHand: {
    top: 20,
    alignItems: 'center',
    transform: [{ rotate: '180deg' }],
  },
  bottomHand: {
    bottom: 20,
    alignItems: 'center',
  },
  leftHand: {
    left: 20,
    justifyContent: 'center',
    transform: [{ rotate: '-90deg' }],
  },
  rightHand: {
    right: 20,
    justifyContent: 'center',
    transform: [{ rotate: '90deg' }],
  },
});

export default GameOnline;
