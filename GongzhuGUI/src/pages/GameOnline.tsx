import React, { useState } from 'react';
import { View, Text, Button, StyleSheet, TouchableOpacity, Image } from 'react-native';
// import { } from 'react-native-paper'
import Card from '../components/Card';
import Hand from '../components/Hand';
import { CardInterface, PlayerInterface } from '../types';
import GameTable from '../components/GameTable';
// import {  } from '../types';
// Helper function to generate a deck of card

const GameOnline : React.FC = () => {
  const [gameStarted, setGameStarted] = useState<boolean>(false);
  const [aiPolicy, setAiPolicy] = useState<String>("random");
  const [gameMode, setGameMode] = useState<String>("full");
  const [declaration, setDeclaration] = useState<String>("enable");

  return (
    <View style={styles.container}>
      {!gameStarted ? (
        // Select a AiPolicy
        <View style={{ padding: 20 }}>
          <Text>AI Algorithm:</Text>
          <View style={{ flexDirection: "row", marginTop: 10, justifyContent: "space-between" }}>
          {["random", "greedy"].map((option) => (
            <TouchableOpacity
              key={option}
              onPress={() => setAiPolicy(option)}
              style={{
                flexDirection: "row",
                alignItems: "center",
                padding: 10,
                backgroundColor: aiPolicy === option ? "#007AFF" : "#BBB",
                borderRadius: 5,
                marginVertical: 5,
              }}
            >
              <Text style={{ color: aiPolicy === option ? "white" : "black" }}>
                {option}
              </Text>
            </TouchableOpacity>
          ))}
          </View>
          <Text>Display Mode:</Text>
          <View style={{ flexDirection: "row", marginTop: 10, justifyContent: "space-between" }}>
          {["full", "state-only"].map((option) => (
            <TouchableOpacity
              key={option}
              onPress={() => setGameMode(option)}
              style={{
                flexDirection: "row",
                alignItems: "center",
                padding: 10,
                backgroundColor: gameMode === option ? "#007AFF" : "#BBB",
                borderRadius: 5,
                marginVertical: 5,
              }}
            >
              <Text style={{ color: gameMode === option ? "white" : "black" }}>
                {option}
              </Text>
            </TouchableOpacity>
          ))}
          </View>
          <Text>Declaration:</Text>
          <View style={{ flexDirection: "row", marginTop: 10, justifyContent: "space-between" }}>
          {["enable", "disable"].map((option) => (
            <TouchableOpacity
              key={option}
              onPress={() => setDeclaration(option)}
              style={{
                flexDirection: "row",
                alignItems: "center",
                padding: 10,
                backgroundColor: declaration === option ? "#007AFF" : "#BBB",
                borderRadius: 5,
                marginVertical: 5,
              }}
            >
              <Text style={{ color: declaration === option ? "white" : "black" }}>
                {option}
              </Text>
            </TouchableOpacity>
          ))}
          </View>
          <View style={styles.buttonContainer}>        
              <Button title="Start Game!" onPress={() => setGameStarted(true)} />
          </View>
        </View>
      //   <View style={styles.container}>
      //     <Text>Select Difficulty</Text>
      //     <View style={styles.buttonContainer}>    
      //       <Button title="Easy (AI plays randomly)" onPress={() => setAiPolicy('random')} />
      //     </View>
      //     <View style={styles.buttonContainer}>        
      //         <Button title="Normal (AI knows some basic strategies)" onPress={() => setAiPolicy('greedy')} />
      //     </View>
      //     <View style={styles.buttonContainer}>        
      //         <Button title="Expert (Not yet implemented)" />
      //     </View>
      //   </View>

      // ) : !gameMode? (
      //   <View style={styles.container}>
      //     <Text>Select Game Mode</Text>
      //     <View style={styles.buttonContainer}>    
      //       <Button title="Full " onPress={() => setGameMode('full')} />
      //     </View>
      //     <View style={styles.buttonContainer}>        
      //         <Button title="State Only" onPress={() => setGameMode('state')} />
      //     </View>
      //   </View>        
      ) : (
        <GameTable 
          initialPlayers={[]} 
          online={true}
          ai={aiPolicy}
          gameMode={gameMode}  // State or Full state of the game
          enable_declarations={declaration=="enable"}  // Enable or Disable declaration of the game
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
