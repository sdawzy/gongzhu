import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import IndexPage from './src/pages/IndexPage';
import GamePage from './src/pages/GamePage'; // The card game page you'll create
import RulesPage from './src/pages/RulesPage';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="IndexPage">
        <Stack.Screen name="IndexPage" component={IndexPage} options={{ title: 'Home' }} />
        <Stack.Screen name="GamePage" component={GamePage} options={{ title: 'Card Game' }} />
        <Stack.Screen name="RulesPage" component={RulesPage} options={{ title: 'Game Rules' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
