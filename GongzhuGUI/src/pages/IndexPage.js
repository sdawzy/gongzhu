import React from 'react';
import { View, Button, StyleSheet } from 'react-native';

export default function IndexPage({ navigation }) {
  return (
    <View style={styles.container}>
      <View style={styles.buttonContainer}>
        <Button
          title="New Game"
          onPress={() => navigation.navigate('GamePage')}
        />
      </View>
      <View style={styles.buttonContainer}>
        <Button
          title="Game Rules"
          onPress={() => navigation.navigate('RulesPage')}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonContainer: {
    marginBottom: 16, // Add vertical spacing between buttons
    width: '80%', // Optional: Set a consistent width for buttons
  },
});
