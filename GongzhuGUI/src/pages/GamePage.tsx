import React, { useState } from 'react';
import { View, Text, Button, StyleSheet, FlatList } from 'react-native';
import Card from '../components/Card';

// Helper function to generate a deck of cards
const generateDeck = () => {
  const suits = ['spade', 'heart', 'diamond', 'club'];
  const ranks = ['02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14'];
  let deck = [];

  suits.forEach(suit => {
    ranks.forEach(rank => {
      deck.push({ suit, rank, id: `${rank}_${suit}` });
    });
  });

  return deck;
};

// Helper function to shuffle the deck
const shuffleDeck = (deck) => {
  return deck.sort(() => Math.random() - 0.5);
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
          <FlatList
            data={players[currentPlayer]}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              // <Text style={styles.card}>
              //   {item.rank} {item.suit}
              // </Text>
               <Card cardName={item.suit + '_' + item.rank} /> 
            )}
          />
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
  container: {
    flex: 1,
    justifyContent: 'center',
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
});
