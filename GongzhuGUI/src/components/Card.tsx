// Card component
import React from 'react';
import { View, Image, StyleSheet } from 'react-native';
import cardImages from './cardImages';  // Mapping of card names to images
import { CardInterface } from '../types';

const Card : React.FC< {
  card: CardInterface, // Card object with id and suit properties
  rotation?: number,  // Optional rotation angle
  visible?: boolean, // Optional visible
}> = ({ card, rotation, visible }) => {
  if (rotation === undefined) { 
    rotation = 0;  // Default rotation is 0 degrees if not provided
  }
  if (visible === undefined) { 
    visible = true;  // Default visibility is true if not provided
  }

  const cardName = visible ? `${card.suit}_${card.rank}` : 'back';  // Construct the card name from the suit and rank properties 
  const cardImage = cardImages[cardName];  // Fetch the image from the mapping

  return (
    <View style={styles.cardContainer}>
      <Image
        source={cardImage}
        style={[styles.cardImage, { transform: [{ rotate: `${rotation}deg` }] }]}
        resizeMode="contain" 
      />
    </View>
  );
}

const styles = StyleSheet.create({
  cardContainer: {
    margin: 0,
  },
  cardImage: {
    width: 100,  
    height: 140,
  },
});

export default Card;