import React, { useState } from 'react';
import { View, Text, Button, StyleSheet, FlatList } from 'react-native';
import Card from '../components/Card';
import Hand from '../components/Hand';

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
  const players = [[], [], [], []];
  deck.forEach((card, index) => {
    players[index % 4].push(card);
  });
  return players;
};

export default function GamePage() {
  const [players, setPlayers] = useState([]);
  const [currentPlayer, setCurrentPlayer] = useState(0); // Track the current player

  const startGame = () => {
    const deck = shuffleDeck(generateDeck());
    const dealtPlayers = dealCards(deck);
    setPlayers(dealtPlayers);
    setCurrentPlayer(0);
  };

  return (
    <View style={styles.container}>
      {players.length === 0 ? (
        <Button title="Start Game" onPress={startGame} />
      ) : (
        <View>
          <Text style={styles.title}>Player {currentPlayer + 1}'s Cards:</Text>
          <Hand hand={players[currentPlayer]}/>
          <Button
            title="Next Player"
            onPress={() => setCurrentPlayer((currentPlayer + 1) % 4)}
          />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  handContainer: {
    height: 250, // Match card height
    position: 'relative', // Allow absolute positioning of cards
    overflow: 'hidden', // Hide overflowing cards
    width: 500,
    // justifyContent: 'center',
    // alignItems: 'center',
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
});
