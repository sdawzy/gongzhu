import React, { useState } from 'react';
import { View, Text, Button, StyleSheet, Image } from 'react-native';
import Card from '../components/Card';
import Hand from '../components/Hand';
import { CardInterface, PlayerInterface } from '../types';
import GameTable from '../components/GameTable';
// import {  } from '../types';
// Helper function to generate a deck of card

const GameOnline : React.FC = () => {
  const [gameStarted, setGameStarted] = useState<boolean>(false);
  const [aiPolicy, setAiPolicy] = useState<String | null>(null);

  return (
    <View style={styles.container}>
      {!aiPolicy ? (
        // Select a AiPolicy
        <View style={styles.container}>
          <Text>Select Difficulty</Text>
          <View style={styles.buttonContainer}>    
            <Button title="Easy (AI plays randomly)" onPress={() => setAiPolicy('random')} />
          </View>
          <View style={styles.buttonContainer}>        
              <Button title="Normal (AI knows some basic strategies)" onPress={() => setAiPolicy('greedy')} />
          </View>
        </View>

      ) : (
        <GameTable 
          initialPlayers={[]} 
          online={true}
          ai={aiPolicy}
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
  buttonContainer: {
    marginBottom: 16, // Add vertical spacing between buttons
    width: '80%', // Optional: Set a consistent width for buttons
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
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
