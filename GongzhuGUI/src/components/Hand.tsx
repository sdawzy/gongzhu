import React, {useState} from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import Card from './Card';
import { CardInterface } from '../types';

const Hand: React.FC< {
    hand: CardInterface[], // List of cards in the hand
    rotation?: number,  // Optional rotation angle
  }> = ({ hand, rotation }) => {
    if (rotation === undefined) { 
      rotation = 0;  // Default rotation is 0 degrees if not provided
    }

    const [selectedCard, setSelectedCard] = useState<string | null>(null);
    const handleCardPress = (card: CardInterface) => {
        setSelectedCard(card.id);
    };

    return (
        <View style={styles.handContainer}>    
            <FlatList horizontal={true}
            data={hand}
            keyExtractor={(item) => item.id}
            renderItem={({ item, index }) => (
                <TouchableOpacity onPress={() => handleCardPress(item)}>
                    <View style={[styles.cardWrapper, 
                    selectedCard === item.id && styles.selectedCardWrapper,
                    {left: index * 30,}]}>
                        <Card 
                            card={item}
                            rotation={rotation}
                        /> 
                    </View>
                </TouchableOpacity>
            )}
            contentContainerStyle={[styles.listContent, {width: 1000}]}
            />
        </View>
    );
}

const styles = StyleSheet.create({
    handContainer: {
      height: 180, // Match card height
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
        borderWidth: 3,
        borderColor: '#FFD700', // Highlight color (gold in this case)
        borderRadius: 5,
        zIndex: 2, // Ensure selected card is above other cards
        transform: [{ translateY: -160 }],
    },
});

export default Hand;
// import React, { useState } from 'react';
// import { View, Text, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
// import Card from './Card';
// import { CardInterface } from '../types';

// const Hand: React.FC<{
//   hand: CardInterface[]; // List of cards in the hand
//   rotation?: number; // Optional rotation angle
// }> = ({ hand, rotation = 0 }) => {
//   const [selectedCard, setSelectedCard] = useState<string | null>(null);

//   const handleCardPress = (card: CardInterface) => {
//     setSelectedCard((prev) => (prev === card.id ? null : card.id)); // Toggle selection
//   };

//   return (
//     <View style={styles.handContainer}>
//       {hand.map((card, index) => (
//         <TouchableOpacity key={card.id} onPress={() => handleCardPress(card)}>
//           <View
//             style={[
//               styles.cardWrapper,
//               { left: index * 30 }, // Adjust horizontal spacing
//               selectedCard === card.id && styles.selectedCardWrapper,
//             ]}
//           > 
//             <Card card={card} rotation={rotation} />
//           </View>
//         </TouchableOpacity>
//       ))}
//     </View>
//   );
// };

// const styles = StyleSheet.create({
//   handContainer: {
//     height: 180, // Match card height
//     position: 'relative', // Enable absolute positioning of cards
//     overflow: 'hidden', // Hide overflowing cards
//     justifyContent: 'flex-end', // Align cards to the bottom
//   },
//   cardWrapper: {
//     position: 'absolute', // Enable overlapping
//     zIndex: 1, // Default stacking order
//     transform: [{ translateY: 0 }], // Default position
//   },
//   selectedCardWrapper: {
//     transform: [{ translateY: -20 }], // Move selected card upward
//     zIndex: 2, // Ensure selected card overlaps others
//     borderWidth: 2,
//     borderColor: '#FFD700', // Gold border for highlighting
//     borderRadius: 8,
//   },
// });

// export default Hand;
