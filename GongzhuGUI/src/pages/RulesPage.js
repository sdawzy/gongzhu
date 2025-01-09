import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

export default function RulesPage() {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Card Game Rules</Text>
      
      <Text style={styles.subtitle}>Objective</Text>
      <Text style={styles.text}>
        The objective of the game is to collect the highest number of points by forming valid card combinations.
      </Text>
      
      <Text style={styles.subtitle}>Setup</Text>
      <Text style={styles.text}>
        - Each player is dealt 5 cards from a shuffled deck.
        - The remaining deck is placed face down to form the draw pile.
        - A discard pile is created by flipping the top card from the draw pile.
      </Text>
      
      <Text style={styles.subtitle}>Gameplay</Text>
      <Text style={styles.text}>
        - On their turn, a player can either draw a card from the draw pile or pick the top card from the discard pile.
        - The player then discards one card to end their turn.
        - The game continues clockwise until one player declares a win or the draw pile is empty.
      </Text>
      
      <Text style={styles.subtitle}>Winning</Text>
      <Text style={styles.text}>
        - A player wins by achieving a valid combination of cards (e.g., a straight, flush, or other game-specific hands).
        - If the draw pile is exhausted, the player with the highest score wins.
      </Text>
      
      <Text style={styles.note}>
        Note: The rules can be customized depending on the variant of the card game being played.
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 16,
    backgroundColor: '#f9f9f9',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center',
    color: '#333',
  },
  subtitle: {
    fontSize: 18,
    fontWeight: '600',
    marginTop: 16,
    marginBottom: 8,
    color: '#555',
  },
  text: {
    fontSize: 16,
    lineHeight: 24,
    color: '#444',
  },
  note: {
    fontSize: 14,
    fontStyle: 'italic',
    marginTop: 16,
    color: '#888',
    textAlign: 'center',
  },
});
