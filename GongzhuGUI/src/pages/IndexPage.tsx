// Index page
import React from 'react';
import { View, Button, StyleSheet, Text } from 'react-native';

export default function IndexPage({ navigation }) {
  return (
    <View style={styles.container}>
      {/* <View style={styles.buttonContainer}>
        <Button
          title="New Offline Game"
          onPress={() => navigation.navigate('GamePage')}
        />
      </View> */}
      <View style={styles.buttonContainer}>
        <Button
          title="New Game"
          onPress={() => navigation.navigate('GameOnline')}
        />
      </View>
      <View style={styles.buttonContainer}>
        <Button
          title="Game Rules"
          onPress={() => navigation.navigate('RulesPage')}
        />
      </View>
      <View style={styles.footer}>
        <Text style={styles.footerText}><p data-key="footer">© 2025 Yue Zhang. All rights reserved.</p></Text>
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
    marginBottom: 16, 
    width: '80%', 
  },
  footer: {
    height: 50,
    justifyContent: "center",
    alignItems: "center",
  },
  footerText: {
    fontSize: 16,
    color: "#333",
  },
});
