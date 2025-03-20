// Game page
import React, { useState } from 'react';
import { View, Text, Button, StyleSheet, TouchableOpacity } from 'react-native';
import GameTable from '../components/GameTable';

const GameOnline : React.FC = () => {
  const [gameStarted, setGameStarted] = useState<boolean>(false);
  const [aiPolicy, setAiPolicy] = useState<String>("random");
  const [gameMode, setGameMode] = useState<String>("full");
  const [declaration, setDeclaration] = useState<String>("enable");

  return (
    <View style={styles.container}>
      {!gameStarted ? (
        // Game configurations
        <View style={{ padding: 20 }}>
          <Text>AI Algorithm:</Text>
          <View style={{ flexDirection: "row", marginTop: 10, justifyContent: "space-between" }}>
          {["random", "greedy", "DMC"].map((option) => (
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
      ) : (
        // Start game
        <GameTable 
          initialPlayers={[]} 
          online={true}
          ai={aiPolicy}
          gameMode={gameMode}  // full version or state-only version
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
    backgroundColor: '#008000', 
  },
  playerContainer: {
    position: 'absolute',
    alignItems: 'center',
  },
  buttonContainer: {
    marginBottom: 16, 
    width: '80%', 
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
    position: 'absolute', 
    zIndex: 1, 
  },
  listContent: {
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
