import React from 'react';
import { View, Image, StyleSheet } from 'react-native';
// import FastImage from 'react-native-fast-image';
import cardImages from './cardImages';  // Mapping of card names to images

const Card : React.FC< {
  cardName: string  
}> = ({ cardName }) => {
  const cardImage = cardImages[cardName];  // Fetch the image from the mapping

  return (
    <View style={styles.cardContainer}>
      <Image
        source={cardImage}
        style={styles.cardImage}
        resizeMode="contain" // Keeps the image aspect ratio
      />
    </View>
  );
}

const styles = StyleSheet.create({
  cardContainer: {
    margin: 5,
  },
  cardImage: {
    width: 100,  // Adjust the size of the cards
    height: 140,
  },
});

export default Card;