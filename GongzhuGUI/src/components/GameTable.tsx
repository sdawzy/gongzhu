import React, { useState, useEffect } from 'react';
import { View, Text, Button, StyleSheet, Image, Modal, FlatList, TouchableOpacity  } from 'react-native';
import Card from '../components/Card';
import Hand from '../components/Hand';
import { CardInterface, PlayerInterface } from '../types';

interface GameTableProps {
  initialPlayers: PlayerInterface[]; // Array of arrays of cards for each player
  currentPlayerIndex: number;
  setCurrentPlayerIndex: Function;
}

const GameTable: React.FC<GameTableProps> = ({ initialPlayers, currentPlayerIndex, setCurrentPlayerIndex }) => {
    const [players, setPlayers] = useState<PlayerInterface[]>(initialPlayers);  
    const [selectedPlayer, setSelectedPlayer] = useState<PlayerInterface | null>(null);
    const [selectedCard, setSelectedCard] = useState<CardInterface | null>(null);
    const [firstPlayerIndex, setFirstPlayerIndex] = useState(0);
    const [roundCount, setRoundCount] = useState(0);
    const maxRounds = 13;

    const [logs, setLogs] = useState<string[]>([]);
    const [isLogExpanded, setIsLogExpanded] = useState<boolean>(false);

    const addLog = (message: string) => {
        setLogs(prevLogs => [message, ...prevLogs]);
    }

    const toggleLog = () => {
        setIsLogExpanded(!isLogExpanded);
      };

    const handleNextTurn = () => {
        if (isEndEpisode) {
            endEpisode();
        } else if (isEndOneRound) {
            endOneRound();
        } else if (isYourTurn) {
            handlePlaySelectedCard();
        } else {
            handleNextPlayer();
        }
    }
    
    const handleShowCollectedCards = (player: PlayerInterface) => {
        setSelectedPlayer(player);
    };

    const handleCloseModal = () => {
        setSelectedPlayer(null);
    };


    const playACard = (player: PlayerInterface, card?: CardInterface) =>  {
        // Logic to play a card from the player's hand.
        const index = card === undefined ? 0 : player.hand.findIndex((item) => item.id === card.id);
        card = player.hand[index];
        if (index != -1) {
            player.currentPlayedCard = card;
            player.playedCards.push(card);
            player.hand.splice(index, 1);
        }
        addLog(`Round ${roundCount+1}: ` + `${player.name} played ${card.rank} of ${card.suit}.`);
    }

    const handleNextPlayer = () => {
        // Logic to move to the next player, for example, using a round-robin approach.
        playACard(players[currentPlayerIndex]);
        setCurrentPlayerIndex((currentPlayerIndex + 1) % players.length);
    };

    const handlePlaySelectedCard = () => {
        // Logic to play the selected card. You can implement this as per the game rules.
        if (selectedCard === null) {
            console.warn('No card selected to play');
            return;
        }
        const currentPlayedCard = selectedCard;
        setSelectedCard(null);

        playACard(players[0], currentPlayedCard);
        setCurrentPlayerIndex((currentPlayerIndex + 1) % players.length);
    };

    const endOneRound = () => {
        // Figure out the largest of this round based on the played cards
        setRoundCount(roundCount + 1);
        let largestIndex = Math.floor(Math.random() * 4);
        for (let i = 0; i < players.length; i++) {
            players[largestIndex].collectedCards.push(players[i].currentPlayedCard);
            players[i].currentPlayedCard = null;
        }
        // If not reaching the maximum rounds, move to the next player
        if ( roundCount < maxRounds) {
            setFirstPlayerIndex(largestIndex);
            setCurrentPlayerIndex(largestIndex);
        } else {
            setFirstPlayerIndex(-1);
            setCurrentPlayerIndex(-1);
        }
    }

    const endEpisode = () => {
        // Episode end logic here
        console.log('Episode ended');
    }

    const isEndOneRound = players[0].currentPlayedCard != null &&
    players[1].currentPlayedCard != null &&
    players[2].currentPlayedCard != null &&
    players[3].currentPlayedCard != null;
    const isEndEpisode = roundCount === maxRounds;
    const isYourTurn = (currentPlayerIndex === 0); // Assuming player 0 is at the bottom
    
    const bottonTitle = "Show Cards & Declaration";

    if (isEndOneRound) {
        setCurrentPlayerIndex(-1);
    }

    // Add hotkey for the center button
    useEffect(() => {
        const handleKeyPress = (event: KeyboardEvent) => {
            if (event.key.toLowerCase() === 'n') {
                handleNextTurn(); // Trigger the button action when 'N' is pressed
            }
        };

        window.addEventListener('keydown', handleKeyPress);
        return () => {
            window.removeEventListener('keydown', handleKeyPress);
        };
    }, [players, selectedCard, currentPlayerIndex]);

    return (
        <View style={styles.tableContainer}>
        {/* Top Player */}
        <View style={[styles.playerContainer, styles.topPlayer]}>
            <Hand hand={players[2].hand} rotation={0} visible={false} />
            <View style={[styles.avatarNameContainer, 
            currentPlayerIndex===2 && styles.currentPlayerWrapper, { transform: [{ rotate: '180deg' }, 
                ] }]}>
            <Image source={players[2].avatar} style={styles.avatar} />
            <Text style={styles.playerName}>{players[2].name}</Text>
            <Button
                title={bottonTitle}
                onPress={() => handleShowCollectedCards(players[2])}
            />
            </View>
        </View>
        {/* Played card of Top Player */}
        <View style={[styles.playedCardContainer, { top: 180 }]}>
            {players[2].currentPlayedCard != null && (
            <Card card={players[2].currentPlayedCard} rotation={180} />
        )}
        </View>
        {/* Left Player */}
        <View style={[styles.playerContainer, styles.leftPlayer]}>
            <View style={[styles.avatarNameContainer,
            currentPlayerIndex===3 && styles.currentPlayerWrapper]}>
                <Image source={players[3].avatar} style={styles.avatar} />
                <Text style={styles.playerName}>{players[3].name}</Text>
            </View>
            <Button
            title={bottonTitle}
            onPress={() => handleShowCollectedCards(players[3])}
            />
            <Hand hand={players[3].hand} rotation={0} visible={false} />
        </View>
        {/* Played card of Left Player */}
        <View style={[styles.playedCardContainer, { left: 450 }]}>
            {players[3].currentPlayedCard != null && (
            <Card card={players[3].currentPlayedCard} rotation={180} />
        )}
        </View>
        {/* Right Player */}
        <View style={[styles.playerContainer, styles.rightPlayer]}>
            <View style={[styles.avatarNameContainer, 
            currentPlayerIndex===1 && styles.currentPlayerWrapper]}>
                <Image source={players[1].avatar} style={styles.avatar} />
                <Text style={styles.playerName}>{players[1].name}</Text>
            </View>
            <Button
            title={bottonTitle}
            onPress={() => handleShowCollectedCards(players[1])}
            />
            <Hand hand={players[1].hand} rotation={0} visible={false} />
        </View>

        {/* Played card of Right Player */}
        <View style={[styles.playedCardContainer, { right: 450 }]}>
            {players[1].currentPlayedCard != null && (
            <Card card={players[1].currentPlayedCard} rotation={180} />
        )}
        </View>
        {/* Bottom Player */}
        <View style={[styles.playerContainer, styles.bottomPlayer]}>
            <Hand hand={players[0].hand} rotation={0} visible={true} 
                selectedCard={selectedCard} setSelectedCard={setSelectedCard}/>
            <View style={[styles.avatarNameContainer, 
                currentPlayerIndex===0 && styles.currentPlayerWrapper,]} >
            <Image source={players[0].avatar} style={styles.avatar} />
            <Text style={styles.playerName}>{players[0].name}</Text>
            <Button
                title={bottonTitle}
                onPress={() => handleShowCollectedCards(players[0])}
            />
            </View>
        </View>
        {/* Played card of Bottom Player */}
        <View style={[styles.playedCardContainer, { bottom: 180 }]}>
            {players[0].currentPlayedCard != null && (
            <Card card={players[0].currentPlayedCard} rotation={180} />
        )}


        </View>
        {/* Modal for Collected Cards */}
        {selectedPlayer && (
            <Modal
            visible={true}
            animationType="none"
            transparent={true}
            onRequestClose={handleCloseModal}
            >
            <View style={styles.modalContainer}>
                <Text style={styles.modalTitle}>
                {selectedPlayer.name}'s Cards & Declaration
                </Text>
                {/* Collected Cards */}
                <Text style={styles.sectionTitle}>Collected Cards:</Text>
                <FlatList
                data={selectedPlayer.collectedCards}
                keyExtractor={(item) => item.id}
                renderItem={({ item }) => (
                    <Card card={item} />
                )}
                horizontal={true}
                contentContainerStyle={styles.cardsContainer}
                />
                {/* Played Cards */}
                <Text style={styles.sectionTitle}>Played Cards:</Text>
                <FlatList
                data={selectedPlayer.playedCards}
                keyExtractor={(item) => item.id}
                renderItem={({ item }) => (
                    <Card card={item} />
                )}
                horizontal={true}
                contentContainerStyle={styles.cardsContainer}
                />

                {/* Declared Cards */}
                <Text style={styles.sectionTitle}>Close Declared Cards:</Text>
                <FlatList
                data={selectedPlayer.closeDeclaredCards}
                keyExtractor={(item) => item.card.id}
                renderItem={({ item }) => (
                    <Card card={item.card} visible={item.visible}/>
                )}
                horizontal={true}
                contentContainerStyle={styles.cardsContainer}
                />
                <Text style={styles.sectionTitle}>Open Declared Cards:</Text>
                <FlatList
                data={selectedPlayer.openDeclaredCards}
                keyExtractor={(item) => item.id}
                renderItem={({ item }) => (
                    <Card card={item} />
                )}
                horizontal={true}
                contentContainerStyle={styles.cardsContainer}
                />


                <Button title="Close" onPress={handleCloseModal} />
            </View>
            </Modal>
        )}

        {/* Modal for Full Log */}
        <Modal
            visible={isLogExpanded}
            animationType="none"
            transparent={true}
            onRequestClose={toggleLog}
        >
            <View style={styles.modalContainer}>
            <Text style={styles.modalTitle}>Full Log</Text>
            <FlatList
                data={logs}
                keyExtractor={(item, index) => index.toString()}
                renderItem={({ item }) => <Text style={styles.modalLogText}>{item}</Text>}
            />
            <Button title="Close" onPress={toggleLog} />
            </View>
        </Modal>
            {/* Conditional Button */}
            {isEndEpisode? 
                <Button title="Show Result (n)" onPress={handleNextTurn} /> : 
            isEndOneRound ? 
                <Button title="End this Round (n)" onPress={handleNextTurn} /> : 
            (isYourTurn ? (
                <Button title="Play Selected Card (n)" onPress={handleNextTurn} />
            ) : (
                <Button title="Next (n)" onPress={handleNextTurn} />
            ))}
            {/* Log Section */}
            <View style={styles.logSection}>
                <Text style={styles.logTitle}>Logs:</Text>
                <FlatList
                data={logs}
                keyExtractor={(item, index) => index.toString()}
                renderItem={({ item }) => <Text style={styles.logText}>{item}</Text>}
                />
                <TouchableOpacity style={styles.expandButton} onPress={toggleLog}>
                    <Text style={styles.expandButtonText}>Expand</Text>
                </TouchableOpacity>
            </View>
        </View>
        
    );
};

const styles = StyleSheet.create({
  tableContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    width: '100%',
  },
  playerContainer: {
    position: 'absolute',
    alignItems: 'center',
  },
  topPlayer: {
    top: 20,
    flexDirection: 'row',
    transform: [{ rotate: '180deg' }],
  },
  bottomPlayer: {
    bottom: 20,
    flexDirection: 'row',
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
    marginBottom: 5,
  },
  playerName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#222222',
    marginBottom: 5,
  },
  avatarNameContainer: {
    marginLeft: 10,
    alignItems: 'center',
  },
  currentPlayerWrapper: {
    borderWidth: 5,
    borderColor: '#FFD700', // Highlight color (gold in this case)
    borderRadius: -5,
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    padding: 20,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 10,
  },
  cardsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 2,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFD700',
    // marginVertical: 50,
  },
  playedCardContainer: {
    position: 'absolute',
    zIndex: 2,
  },
  logSection: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    width: '23%', // Adjust width as needed
    maxHeight: '14%', // Adjust height as needed
    backgroundColor: '#222',
    padding: 10,
    borderTopRightRadius: 10,
    borderBottomRightRadius: 0,
    borderTopLeftRadius: 0,
    borderBottomLeftRadius: 10,
    overflow: 'hidden',
  },
  logTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  logText: {
    color: '#ccc',
    fontSize: 14,
  },
  modalLogText: {
    color: '#fff',
    fontSize: 14,
    marginBottom: 5,
  },
  expandButton: {
    marginTop: 10,
    padding: 5,
    backgroundColor: '#444',
    alignItems: 'center',
    borderRadius: 5,
  },
  expandButtonText: {
    color: '#fff',
    fontSize: 14,
  },
});

export default GameTable;
