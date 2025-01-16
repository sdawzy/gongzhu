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

const GameOnline : React.FC = () => {
  const [gameStarted, setGameStarted] = useState<boolean>(false);

  return (
    <View style={styles.container}>
      {!gameStarted ? (
        <View>        
            <Hand 
              hand={generateDeck()} 
              rotation={0}
              visible={false}
            />
            <Button title="Start Game" onPress={setGameStarted(()=>true)} />
        </View>
      ) : (
        <GameTable 
          initialPlayers={[]} 
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
