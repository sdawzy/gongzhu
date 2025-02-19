import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
// import { View, StyleSheet, Text } from 'react-native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import IndexPage from './src/pages/IndexPage';
// import GamePage from './src/pages/GamePage'; 
import RulesPage from './src/pages/RulesPage';
import GameOnline from './src/pages/GameOnline'; 

const Stack = createNativeStackNavigator();

const App: React.FC = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="IndexPage">
        <Stack.Screen name="IndexPage" component={IndexPage} options={{ title: 'Gongzhu Emulator' }} />
        {/* <Stack.Screen name="GamePage" component={GamePage} options={{ title: 'Game' }} /> */}
        <Stack.Screen name="GameOnline" component={GameOnline} options={{ title: 'Have fun Gongzhu!' }} />
        <Stack.Screen name="RulesPage" component={RulesPage} options={{ title: 'Gongzhu Rules' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;