import React, { useState } from 'react';
import { View, Text, Button, StyleSheet, Image, ImageSourcePropType } from 'react-native';
import Card from '../components/Card';
import Hand from '../components/Hand';
import { CardInterface } from '../types';
import { PlayerInterface } from '../types';

// interface Player {
//     name: string;
//     avatar: ImageSourcePropType;
// }

interface GameTableProps {
    players: PlayerInterface[]; // Array of arrays of cards for each player
}
const GameTable: React.FC<GameTableProps> = ({ players }) => {
  return (
    (<View style={styles.tableContainer}>
        {/* Top Player */}
        <View style={[styles.playerContainer, styles.topPlayer]}>
            <Hand hand={players[2].hand} rotation={0} visible={false}/>
            <View style={[styles.avatarNameContainer, {transform: [{ rotate: '180deg' }]}]}>
                <Image source={players[2].avatar} style={styles.avatar} />
                <Text style={styles.playerName}>{players[2].name}</Text>
            </View>  
        </View>
        {/* Left Player */}
        <View style={[styles.playerContainer, styles.leftPlayer]}>
            <Image source={players[3].avatar} style={styles.avatar} />
            <Text style={styles.playerName}>{players[3].name}</Text>
            <Hand hand={players[3].hand} rotation={0} visible={false}/>
        </View>
        {/* Right Player */}
        <View style={[styles.playerContainer, styles.rightPlayer]}>
            <Image source={players[1].avatar} style={styles.avatar} />
            <Text style={styles.playerName}>{players[1].name}</Text>
            <Hand hand={players[1].hand} rotation={0} visible={false}/>
        </View>
        {/* Bottom Player */}
        <View style={[styles.playerContainer, styles.bottomPlayer]}>
            <Hand hand={players[0].hand} rotation={0} visible={true}/>
            <View style={styles.avatarNameContainer}>
                <Image source={players[0].avatar} style={styles.avatar} />
                <Text style={styles.playerName}>{players[0].name}</Text>
            </View>
        </View>
    </View>
    )
  )
}

const styles = StyleSheet.create({
  tableContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    // backgroundColor: '#008000', // Green table background like a card table
    width: '100%'
  },
  playerContainer: {
    position: 'absolute',
    alignItems: 'center',
  },
  container: {
    flex: 1,
    justifyContent: 'flex-end',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#f0f8ff',
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
    position: 'absolute', // Allow overlapping
    zIndex: 1, // Ensure overlapping is in order of the cards
  },
  listContent: {
    // alignItems: 'center',
    height: '100%',
  },
  topPlayer: {
    top: 20,
    alignItems: 'center',
    flexDirection: 'row', // Layout hand and avatar/name side-by-side
    transform: [{ rotate: '180deg' }],
  },
  bottomPlayer: {
    bottom: 20,
    flexDirection: 'row', // Layout hand and avatar/name side-by-side
    alignItems: 'center',
  },
  leftPlayer: {
    left: 20,
    justifyContent: 'center',
    transform: [{ rotate: '90deg' }],
  },
  rightPlayer: {
    right: 20,
    justifyContent: 'center',
    transform: [{ rotate: '-90deg' }],
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    marginBottom: 5, // Space between avatar and hand
  },
  playerName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#222222',
    marginBottom: 5, // Space between name and avatar
    textAlign: 'center',
  },
  avatarNameContainer: {
    marginLeft: 10, // Space between hand and avatar/name
    alignItems: 'center', // Center-align avatar and name
  },
});

export default GameTable;
