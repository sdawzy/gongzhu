// Game table component
import React, { useState, useEffect} from 'react';
import { View, Text, Button, StyleSheet, Image, Modal, FlatList, TouchableOpacity  } from 'react-native';
import Card from '../components/Card';
import {PIG, SHEEP, BLOOD, DOUBLER} from '../components/specialCards';
import Hand from '../components/Hand';
import Declaration from './Declaration';
import { CardInterface, PlayerInterface, DeclarationsInterface } from '../types';
import axios from 'axios';

interface GameTableProps {
  initialPlayers: PlayerInterface[]; 
  online: boolean; 
  ai: String; 
  gameMode: String; 
  enable_declarations: boolean; 
};

const defaultAvatars = [
    require('../../assets/images/avatars/You.png'),
    require('../../assets/images/avatars/Panda.png'),
    require('../../assets/images/avatars/Penguin.png'),
    require('../../assets/images/avatars/Elephant.png')
];

const GameTable: React.FC<GameTableProps> = ({ initialPlayers, online, ai = "normal", gameMode, enable_declarations }) => {
    const maxRounds = 13;
    const bottonTitle = "Show Cards & Declaration";

    const [players, setPlayers] = useState<PlayerInterface[]>(online ? [] : initialPlayers);  
    const [selectedPlayer, setSelectedPlayer] = useState<PlayerInterface | null>(null);
    const [selectedCard, setSelectedCard] = useState<CardInterface | null>(null);
    const [firstPlayerIndices, setFirstPlayerIndices] = useState<number[]>([]);
    const [history, setHistory] = useState<CardInterface[]>([]);
    const [firstPlayerIndex, setFirstPlayerIndex] = useState(0);
    const [readyToLog, setReadyToLog] = useState<boolean>(false);
    const [currentPlayerIndex, setCurrentPlayerIndex] = useState(0);
    const [roundCount, setRoundCount] = useState(0);
    const [gameId, setGameId] = useState<String | null> (null); 
    const [cardsPlayedThisRound, setCardsPlayedThisRound] = useState<CardInterface[]>([]);
    const [logs, setLogs] = useState<string[]>([]);
    const [isLogExpanded, setIsLogExpanded] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(online ? true : false);
    const [started, setStarted] = useState<boolean>(false);
    const [error, setError] = useState<String | null>(null);
    const [isDeclarationPhase, setDeclarationPhase] = useState<boolean>(false);
    const [declarations, setDeclarations] = useState<DeclarationsInterface> ({
        "pig" : 'no',
        'sheep': 'no',
        "doubler": 'no',
        "blood": 'no'
    });
    const [actionValue, setActionValue] = useState<number | null>(null);
    // If deployed, use the api from the environment variable
    // const API_URL = Constants.expoConfig?.extra?.apiUrl;
    // const API_URL = "http://0.0.0.0:8000";
    const API_URL = "https://gongzhuapi.onrender.com";
    const addLog = (message: string) => {
        setLogs(prevLogs => [message, ...prevLogs]);
    }

    const toggleLog = () => {
        setIsLogExpanded(!isLogExpanded);
    };

    // console.log(API_URL);
    const handleNextTurn = () => {
        // If the game mode is set to be full, then display each turn
        if (gameMode == "full") {
            if (isEndOneRound) {
                endOneRound();
                return;
            } else if (isEndEpisode) {
                endEpisode();
            } else if (isYourTurn) {
                if (isDeclarationPhase) {
                    handleDeclarations();
                } else {
                    handlePlaySelectedCard();
                }
            } else {
                handleNextPlayer();
            }
        } else { // If not, only display the state when the player needs to take actions
            if (isEndEpisode) {
                endEpisode();
            } else {
                handleStep();
            }
        }
    }

    // Fetch the log based on history and first players
    const fetchLogs = async () => {
        setLogs([]);
        // If there is a declaration phase
        if (enable_declarations) {
            addLog('---Declaration phase---');
            for (let i = 0; i < 4; i++) {
                const player = players[(i + firstPlayerIndices[0]) % 4];
                addDeclarationsLog(player.name,
                {
                    "closed_declarations" : player.closedDeclaredCards,
                    "open_declarations" : player.openDeclaredCards,
                });
            }
            if (!isDeclarationPhase) {
                addLog('---End Declaration phase---');
            }
        }
        // 
        for (let r = 0; r < roundCount; r++) {
            addLog(`---Round ${r+1}---`);
            for (let i = 0; i < 4; i++) {
                const player = players[(i + firstPlayerIndices[r]) % 4];
                const move = history[r * 4 + i];
                addLog(`Round ${r+1}: ` + `${player.name} played ${move.rank} of ${move.suit}.`);
            }
            const largest_player = players[firstPlayerIndices[r+1]];
            addLog(`${largest_player.name} was the largest.`);
            addLog(`---End Round ${r+1}---`);
        }
        //
        if (!isDeclarationPhase)  {
            addLog(`---Round ${roundCount+1}---`);
        }
        for (let i = 0; i < cardsPlayedThisRound.length; i++) {
            const player = players[(i + firstPlayerIndices[roundCount]) % 4];
            const move = history[roundCount * 4 + i];
            addLog(`Round ${roundCount+1}: ` + `${player.name} played ${move.rank} of ${move.suit}.`);            
        }
        // console.log('History: ', history);
    }

    // Convert declarations to api request format
    const convertToDeclarationRequest = () => {
        let closedDeclaredCards: CardInterface[] = [];
        let openDeclaredCards: CardInterface[] = [];
        if (declarations['pig'] != 'no') {
            if (declarations['pig'] == 'open') {
                openDeclaredCards.push(PIG);
            } else {
                closedDeclaredCards.push(PIG);
            }
        }
        if (declarations['sheep'] != 'no') {
            if (declarations['sheep'] == 'open') {
                openDeclaredCards.push(SHEEP);
            } else {
                closedDeclaredCards.push(SHEEP);
            }
        }
        if (declarations['blood'] != 'no') {
            if (declarations['blood'] == 'open') {
                openDeclaredCards.push(BLOOD);
            } else {
                closedDeclaredCards.push(BLOOD);
            }
        }
        if (declarations['doubler'] != 'no') {
            if (declarations['doubler'] == 'open') {
                openDeclaredCards.push(DOUBLER);
            } else {
                closedDeclaredCards.push(DOUBLER);
            }
        }
        return {
            'id' : gameId,
            'closed_declarations' : closedDeclaredCards,
            'open_declarations' : openDeclaredCards
        }
    }

    const handleStep = () => {
        // Logic to play the selected card. You can implement this as per the game rules.
        if (isDeclarationPhase) {
            const requestData = convertToDeclarationRequest(); // request
            // console.log(requestData);
            axios.post(API_URL + '/step', requestData).then((response) => {
                // const data = response.data;
                const statusCode = response.status;
                // addDeclarationsLog("You", requestData)
                if (statusCode === 400) {
                    addLog("Invalid declaration by you. Please try again.");
                    return;
                }
                // addLog(`Round ${roundCount+1}: ` + `you played ${currentPlayedCard.rank} of ${currentPlayedCard.suit}.`);
                fetchGameStates(gameId);
                // setCurrentPlayerIndex((currentPlayerIndex + 1) % players.length);
            }).catch((error) => {
                if (error.status === 400 ) {
                    // addLog("Invalid move by you. Please try again.");
                    return;
                }
                console.error('Error fetching playing card: ', error);
            });
        }
        if (selectedCard === null) {
            console.warn('No card selected to play');
            return;
        }
        const currentPlayedCard = selectedCard;
        setSelectedCard(null);

        if (online) {
            const requestData = {
                'id' : gameId,
                'suit' : currentPlayedCard.suit,
                'rank' : currentPlayedCard.rank,
            }
            axios.post(API_URL + '/step', requestData).then((response) => {
                // const data = response.data;
                const statusCode = response.status;
                if (statusCode === 400) {
                    addLog("Invalid move by you. Please try again.");
                    return;
                }
                // addLog(`Round ${roundCount+1}: ` + `you played ${currentPlayedCard.rank} of ${currentPlayedCard.suit}.`);
                fetchGameStates(gameId);
                // setCurrentPlayerIndex((currentPlayerIndex + 1) % players.length);
            }).catch((error) => {
                if (error.status === 400 ) {
                    addLog("Invalid move by you. Please try again.");
                    return;
                }
                console.error('Error fetching playing card: ', error);
            });
        } else if ( playACard(players[0], currentPlayedCard) ) {
            setCurrentPlayerIndex((currentPlayerIndex + 1) % players.length);
        }
    }
    
    const handleShowCollectedCards = (player: PlayerInterface) => {
        setSelectedPlayer(player);
    };

    const handleCloseModal = () => {
        setSelectedPlayer(null);
    };

    const isValidMove = (card: CardInterface) : boolean   => {  
        // Deprecated method
        // Now use api to determine whether a move is valid
        return true; 
    };

    const playACard = (player: PlayerInterface, card?: CardInterface) : boolean =>  {
        // Logic to play a card from the player's hand.
        const index = card === undefined ? 0 : player.hand.findIndex((item) => item.id === card.id);
        card = player.hand[index];
        // check if this card is valid
        if (isValidMove(card)) {
            player.currentPlayedCard = card;
            player.playedCards.push(card);
            player.hand.splice(index, 1);
            setCardsPlayedThisRound(prevCards => [card, ...prevCards]);
            // addLog(`Round ${roundCount+1}: ` + `${player.name} played ${card.rank} of ${card.suit}.`);
            return true;
        } else {
            addLog(`Round ${roundCount+1}: Invalid move by ${player.name}.`);
            return false;
        }
    }
    
    // Add declarations to logs
    const addDeclarationsLog = (name: string | undefined, declarations) => {
        for(const card of declarations["open_declarations"]) {
            if (card.id == PIG.id) {
                addLog(`${name} openly declared Pig!`);
            }
            if (card.id == SHEEP.id) {
                addLog(`${name} openly declared Sheep!`);
            }
            if (card.id == BLOOD.id) {
                addLog(`${name} openly declared Blood!`);
            }
            if (card.id == DOUBLER.id) {
                addLog(`${name} openly declared Doubler!`);
            }
        }
        if (name == 'You') {
            for(const card of declarations["closed_declarations"]) {
                if (card.id == PIG.id) {
                    addLog(`${name} secretly declared Pig!`);
                }
                if (card.id == SHEEP.id) {
                    addLog(`${name} secretly declared Sheep!`);
                }
                if (card.id == BLOOD.id) {
                    addLog(`${name} secretly declared Blood!`);
                }
                if (card.id == DOUBLER.id) {
                    addLog(`${name} secretly declared Doubler!`);
                }
            }
        } else {
            if (declarations["closed_declarations"].length > 0) {
                addLog(`${name} secretly declared ${declarations["closed_declarations"].length} card(s)!`);
            }
        }
    }

    const handleNextPlayer = () => {
        // Logic to move to the next player, for example, using a round-robin approach.
        if (online) {
            axios.post(API_URL + '/next_player', {'id' : gameId}).then((response) => {
                const data = response.data;
                const move = data.move;
                // if (isDeclarationPhase) {
                //     // addDeclarationsLog(players[currentPlayerIndex].name, move)
                // } else {
                //     // addLog(`Round ${roundCount+1}: ` + `${players[currentPlayerIndex].name} played ${move.rank} of ${move.suit}.`);
                // }
                fetchGameStates(gameId);
                // setCurrentPlayerIndex((currentPlayerIndex + 1) % players.length);
            }).catch((error) => {
                console.error('Error fetching next player: ', error);
            });
        } else if (playACard(players[currentPlayerIndex])) {
            setCurrentPlayerIndex((currentPlayerIndex + 1) % players.length);
        }
    };

    // Play selected card
    const handlePlaySelectedCard = () => {
        // Logic to play the selected card. You can implement this as per the game rules.
        if (selectedCard === null) {
            console.warn('No card selected to play');
            return;
        }
        const currentPlayedCard = selectedCard;
        setSelectedCard(null);

        if ( online) {
            const requestData = {
                'id' : gameId,
                'suit' : currentPlayedCard.suit,
                'rank' : currentPlayedCard.rank,
            }
            axios.post(API_URL + '/play_card', requestData).then((response) => {
                // const data = response.data;
                const statusCode = response.status;
                if (statusCode === 400) {
                    addLog("Invalid move by you. Please try again.");
                    return;
                }
                // addLog(`Round ${roundCount+1}: ` + `you played ${currentPlayedCard.rank} of ${currentPlayedCard.suit}.`);
                fetchGameStates(gameId);
                // setCurrentPlayerIndex((currentPlayerIndex + 1) % players.length);
            }).catch((error) => {
                if (error.status === 400 ) {
                    addLog("Invalid move by you. Please try again.");
                    return;
                }
                console.error('Error fetching playing card: ', error);
            });
        } else if ( playACard(players[0], currentPlayedCard) ) {
            setCurrentPlayerIndex((currentPlayerIndex + 1) % players.length);
        }
    };

    const endOneRound = async () => {
        try {
            // Figure out the largest of this round based on the played cards
            let largestIndex;
            if (online) {
                const response = await axios.post(API_URL + '/next_round', { 'id': gameId });
                const data = response.data;
                largestIndex = data.largestIndex;
    
                // addLog(`Round ${roundCount + 1}: ` + `${players[largestIndex].name} was largest.`);
                await fetchGameStates(gameId); // Ensure the game state is fetched before proceeding
            } else {
                largestIndex = Math.floor(Math.random() * 4); // Randomly choose the largest player offline
                // Update the round count
                setRoundCount((prevCount) => prevCount + 1);
            }

            // Process collected cards for the largest player
            for (let i = 0; i < players.length; i++) {
                players[largestIndex].collectedCards.push(players[i].currentPlayedCard);
                players[i].currentPlayedCard = null;
            }
    
            // Decide the next step based on the round count
            if (roundCount < maxRounds) { // Use `roundCount + 1` because `setRoundCount` is asynchronous
                setCardsPlayedThisRound([]);
                setFirstPlayerIndex(largestIndex);
                setCurrentPlayerIndex(largestIndex);
                // console.log(`Round ${roundCount + 1} ended.`);
            } else {
                setFirstPlayerIndex(-1);
                setCurrentPlayerIndex(-1);
            }
        } catch (error) {
            console.error('Error in endOneRound: ', error);
        }
    };
    
    const handleDeclarations = () => {
        const requestData = convertToDeclarationRequest(); // request
        // console.log(requestData);
        axios.post(API_URL + '/make_declarations', requestData).then((response) => {
            // const data = response.data;
            const statusCode = response.status;
            addDeclarationsLog("You", requestData)
            if (statusCode === 400) {
                addLog("Invalid declaration by you. Please try again.");
                return;
            }
            // addLog(`Round ${roundCount+1}: ` + `you played ${currentPlayedCard.rank} of ${currentPlayedCard.suit}.`);
            fetchGameStates(gameId);
            // setCurrentPlayerIndex((currentPlayerIndex + 1) % players.length);
        }).catch((error) => {
            if (error.status === 400 ) {
                addLog("Invalid move by you. Please try again.");
                return;
            }
            console.error('Error fetching playing card: ', error);
        });
    }
    
    const startGame = () => {
        axios.post(API_URL + '/start_game', {"ai": ai, "auto": gameMode != 'full', "declaration": enable_declarations})
            .then(response => {
                // console.log(response.data);
                fetchGameStates(response.data.id);
                setDeclarations({
                    "pig" : 'no',
                    'sheep': 'no',
                    "doubler": 'no',
                    "blood": 'no'
                })
            })
            .catch(error => {
                console.error("There was an error starting the game!", error);
            });
    }

    const endEpisode = () => {
        // console.log('Episode ended. New Game started.');
        startGame();
    }

    const fetchGameStates = async (id: String | null) => {
        // if (loading) {
        //     return; // Return early if already loading
        // }
        try {
            setLoading(true); // Start loading
            const response = await axios.post(API_URL + '/get_game_state', {'id' : id});
            const game_state = response.data.game_state;
            setPlayers(game_state.players); // Update state with player data
            setFirstPlayerIndex(game_state.firstPlayerIndex); // Update state with the index of the first player
            setRoundCount(game_state.roundCount); // Update state with the current round count
            setCurrentPlayerIndex(game_state.currentPlayerIndex); // Update state with the index of the current player
            setCardsPlayedThisRound(game_state.cardsPlayedThisRound); // Update state with the cards played this round
            setDeclarationPhase(game_state.isDeclarationPhase); // Set the declaration
            setGameId(id);
            setFirstPlayerIndices(game_state.firstPlayerIndices);
            // setHistory(game_state.history);
            setHistory([...game_state.history]); 
            setReadyToLog(true);
        } catch (err) {
            console.error("Failed to fetch game states:", err);
            setError("Failed to load player data.");
        } finally {
            setLoading(false); 
            setStarted(true); // Game started
            // fetchLogs();
        }
    };

    if (online) {
        useEffect(() => {
            startGame();
        }, []); 
    }

    let isEndOneRound = false; 
    // Check if every player has played some card
    if (players.length > 0) {
        isEndOneRound = players[0].currentPlayedCard != null &&
        players[1].currentPlayedCard != null &&
        players[2].currentPlayedCard != null &&
        players[3].currentPlayedCard != null;
    } 
    // const isEndOneRound = false;
    const isEndEpisode = (roundCount === maxRounds && !isEndOneRound);
    const isYourTurn = (currentPlayerIndex === 0); // Assuming player 0 is at the bottom
    if (isEndOneRound && currentPlayerIndex != -1) {
        setCurrentPlayerIndex(-1);
        // console.log('End of one round');
    }

    // const isFetching = useRef(false);

    useEffect(() => {
        if (readyToLog) {
            fetchLogs();
            setReadyToLog(false);
        }
    }, [readyToLog]); 

    // Update esimated action value
    useEffect(() => {
        if (selectedCard == null) {
            setActionValue(null)
        } else {
            // Request estimated action value
            const requestData = {
                'id' : gameId,
                'suit' : selectedCard.suit,
                'rank' : selectedCard.rank,
            }
            axios.post(API_URL + '/evaluate', requestData).then((response) => {
                const statusCode = response.status;
                if (statusCode === 400) {
                    // addLog("Invalid move by you. Please try again.");
                    return;
                }
                const data = response.data;
                const evaluation = data.evaluation;
                setActionValue(evaluation);
                // addLog(`Round ${roundCount+1}: ` + `you played ${currentPlayedCard.rank} of ${currentPlayedCard.suit}.`);
                // fetchGameStates(gameId);
                // setCurrentPlayerIndex((currentPlayerIndex + 1) % players.length);
            }).catch((error) => {
                // if (error.status === 400 ) {
                //     addLog("Invalid move by you. Please try again.");
                //     return;
                // }
                // console.error('Error fetching playing card: ', error);
            });            
        }
    }, [selectedCard]);
    

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

    if (!started) {
        return (
            <View style={styles.loadingContainer}>
                <Text style={styles.loadingText}>Loading Game...</Text>
                <Text style={styles.subText}>(This may take a minute in first loading)</Text>
            </View>
        );
    }
    return (
    <View style={styles.tableContainer}>
        {/* Top Player */}
        <View style={[styles.playerContainer, styles.topPlayer]}>
            <Hand hand={players[2].hand} rotation={0} visible={false} />
            <View style={[styles.avatarNameContainer, 
            currentPlayerIndex===2 && styles.currentPlayerWrapper, { transform: [{ rotate: '180deg' }, 
                ] }]}>
            <Image source={players[2].avatar ? players[2].avatar : defaultAvatars[2]} style={styles.avatar} />
            <Text style={styles.playerName}>{players[2].name}</Text>
            <Text style={styles.playerName}>Score : {players[2].score}</Text>
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
                <Image source={players[3].avatar ? players[3].avatar : defaultAvatars[3]} style={styles.avatar} />
                <Text style={styles.playerName}>{players[3].name}</Text>
                <Text style={styles.playerName}>Score : {players[3].score}</Text>
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
                <Image source={players[1].avatar ? players[1].avatar : defaultAvatars[1]} style={styles.avatar} />
                <Text style={styles.playerName}>{players[1].name}</Text>
                <Text style={styles.playerName}>Score : {players[1].score}</Text>
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
                selectable={isYourTurn && !isDeclarationPhase}
                selectedCard={isYourTurn ? selectedCard : null}
                setSelectedCard={setSelectedCard}/>
            <View style={[styles.avatarNameContainer, 
                currentPlayerIndex===0 && styles.currentPlayerWrapper,]} >
                
                <Image source={players[0].avatar ? players[0].avatar : defaultAvatars[0]} style={styles.avatar} />
                <Text style={styles.playerName}>{players[0].name}</Text>
                <Text style={styles.playerName}>Score : {players[0].score}</Text>
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

        {/* Modal for Collected Cards */}
        </View>
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
                data={selectedPlayer.closedDeclaredCards}
                keyExtractor={(item) => item.id}
                renderItem={({ item }) => (
                    <Card card={item} visible={item.known}/>
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
            <Text style={styles.playerName}>Estimated Action Value : {actionValue}</Text>
            {loading?
             <Text>Loading...</Text> : 
             isEndEpisode? 
                <Button title="New Game (n)" onPress={handleNextTurn} /> : 
            isEndOneRound ? 
                <Button title="End this Round (n)" onPress={handleNextTurn} /> : 
            (isYourTurn ? ( isDeclarationPhase ? 
                <View>
                    <Declaration 
                        hand={players[0].hand} 
                        declarations={declarations}
                        setDeclarations={setDeclarations}
                    />
                    <Button title="Finish Declaration (n)" onPress={handleNextTurn} />
                </View> :
                <Button title="Play Selected Card (n)" onPress={handleNextTurn} /> 
            ):
                <Button title="Next (n)" onPress={handleNextTurn} />
            )}

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
    borderColor: '#FFD700', 
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
  },
  playedCardContainer: {
    position: 'absolute',
    zIndex: 2,
  },
  logSection: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    width: '23%', 
    maxHeight: '14%', 
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
  loadingContainer: {
    flex: 1, // Optional: if you want the container to fill the screen
    justifyContent: 'center', // Center children vertically within the container
    alignItems: 'center', // Center children horizontally within the container
    padding: 20, // Add some padding around the content
  },
  loadingText: {
    fontSize: 24, // Increased font size for the main text
    fontWeight: 'bold', // Optional: make it bold
    textAlign: 'center', // Ensure text itself is centered if it wraps
    marginBottom: 10, // Add some space below the main text
  },
  subText: {
    fontSize: 16, // Increased font size for the subtext (smaller than main)
    color: 'grey', // Optional: change color to make it less prominent
    textAlign: 'center', // Ensure text itself is centered
  },
});
  

export default GameTable;
