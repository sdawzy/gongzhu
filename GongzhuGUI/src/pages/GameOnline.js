import React, { useState, useEffect } from 'react';
import { View, Text, Button, StyleSheet, FlatList } from 'react-native';
import axios from 'axios';

export default function GameOnline() {
  const [players, setPlayers] = useState([]);
  const [currentPlayer, setCurrentPlayer] = useState(0); // Track the current player
  const URL = 'http://localhost:1926';

  useEffect(() => {
    // Fetch player cards when the game starts
    axios.get(URL + '/start_game')
      .then(response => {
        console.log(response.data);
        fetchPlayerCards(0);  // Fetch cards for player 1 after game starts
      })
      .catch(error => {
        console.error("There was an error starting the game!", error);
      });
  }, []);

  const fetchPlayerCards = (playerId) => {
    axios.get(`${URL}/get_player_cards?player_id=${playerId}`)
      .then(response => {
        setPlayers(response.data.cards);
      })
      .catch(error => {
        console.error("There was an error fetching player cards!", error);
      });
  };

  const nextPlayer = () => {
    axios.post(URL + '/next_player')
      .then(response => {
        setCurrentPlayer((currentPlayer + 1) % 4);
        fetchPlayerCards((currentPlayer + 1) % 4);
      })
      .catch(error => {
        console.error("There was an error moving to the next player!", error);
      });
  };

  return (
    <View style={styles.container}>
      {players.length === 0 ? (
        <Text>Loading game...</Text>
      ) : (
        <View>
          <Text style={styles.title}>Player {currentPlayer + 1}'s Cards:</Text>
          <FlatList
            data={players}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <Text style={styles.card}>
                {item.rank} {item.suit}
              </Text>
            )}
          />
          <Button title="Next Player" onPress={nextPlayer} />
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
