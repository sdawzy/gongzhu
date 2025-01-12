import React, {useState} from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import Card from './Card';
import { CardInterface } from '../types';

const Hand: React.FC< {
    hand: CardInterface[], // List of cards in the hand
    rotation?: number,  // Optional rotation angle
    visible?: boolean,  // Optional visibility state
    selectedCard?: CardInterface | null,  // Optional selected card ID
    setSelectedCard?: Function,  // Optional callback function to update selected card state
  }> = ({ hand, rotation, visible, selectedCard, setSelectedCard }) => {
    if (rotation === undefined) { 
      rotation = 0;  // Default rotation is 0 degrees if not provided
    }
    if (visible === undefined) { 
      visible = true;  // Default visibility is true if not provided
    }

    const cardBack = require('../../assets/images/cards/card_back.png');
    if (selectedCard === undefined) { 
      // console.warn('No selectedCard provided, using first card in hand');
      [selectedCard, setSelectedCard] = useState<CardInterface | null>(null);
    }
    const numberOfCards = hand.length;
    const handleCardPress = (card: CardInterface) => {
        setSelectedCard(card);
    };

    if (visible === true) {
      return (
          <View style={styles.handContainer}>    
              <FlatList horizontal={true}
              data={hand}
              keyExtractor={(item) => item.id}
              renderItem={({ item, index }) => (
                  <TouchableOpacity onPress={() => handleCardPress(item)}>
                      <View style={[styles.cardWrapper, 
                      selectedCard == item && styles.selectedCardWrapper,
                      {left: index * 30,}]}>
                          <Card 
                              card={item}
                              visible={visible}
                          />
                      </View>
                  </TouchableOpacity>
              )}
              contentContainerStyle={[styles.listContent, {width: (numberOfCards-1) * 30 + 100}]}
              style={{ transform: [{ rotate: `${rotation}deg` }] }}
              />
          </View>
      );
    } else { 
      return (
          <View style={styles.handContainer}>
              <FlatList horizontal={true}
              data={hand}
              keyExtractor={(item) => item.id}
              renderItem={({ item, index }) => (
                  <View style={[styles.cardWrapper, 
                  {left: index * 30,}]}>
                      <Card 
                          card={item}
                          visible={visible}
                      />
                  </View>
              )}
              contentContainerStyle={[styles.listContent, {width: (numberOfCards-1) * 30 + 100}]}
              style={{ transform: [{ rotate: `${rotation}deg` }] }}
              />
          </View>
      );
    }
}

const styles = StyleSheet.create({
    handContainer: {
      height: 170, // Match card height
      position: 'relative', // Allow absolute positioning of cards
      overflow: 'hidden', // Hide overflowing cards
      justifyContent: 'flex-end', // Align cards to the bottom
    //   alignItems: 'center', //
      width: 500,
    },
    title: {
      fontSize: 20,
      fontWeight: 'bold',
      marginBottom: 16,
      textAlign: 'center',
    },
    cardWrapper: {
      position: 'absolute', // Allow overlapping
      zIndex: 1, // Ensure overlapping is in order of the cards
      transform: [{ translateY: -140 }],
    },
    listContent: {
      height: '100%',
    //   alignItems: 'flex-end'
      
      flexDirection: 'row',
      alignItems: 'flex-end', // Aligns cards to the bottom of the container
      paddingBottom: 10, // Adds spacing from the bottom
    },
    selectedCardWrapper: {
        borderWidth: 5,
        borderColor: '#FFD700', // Highlight color (gold in this case)
        borderRadius: -5,
        zIndex: 2, // Ensure selected card is above other cards
        transform: [{ translateY: -160 }],
    },
});

export default Hand;
