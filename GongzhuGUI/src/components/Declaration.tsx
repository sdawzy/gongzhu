// Declaration UI used in GameTable
import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { CardInterface, DeclarationsInterface } from '../types';
import Card from './Card';
import { PIG, SHEEP, BLOOD, DOUBLER} from './specialCards';

const OneDeclaration : React.FC<{
    specialCard: CardInterface,
    specialCardName: string,
    declarations: DeclarationsInterface,
    setDeclarations: Function,
}>= ({specialCard, specialCardName, declarations, setDeclarations}) => {
    // console.log(declarations)
    return (<View>
        <Card card={specialCard}/>
        <View style={{ marginTop: 2, justifyContent: "space-between" }}>
          {["open", "close", "no"].map((option) => (
            <TouchableOpacity
              key={option}
              onPress={() => setDeclarations(prevDecs => ({
                ...prevDecs,  
                [specialCardName]: option // Update only the specific key
            }))}
              style={{
                flexDirection: "row",
                alignItems: "center",
                padding: 5,
                backgroundColor: declarations[specialCardName] === option ? "#007AFF" : "#BBB",
                borderRadius: 3,
                marginVertical: 3,
              }}
            >
              <Text style={{ color: declarations[specialCardName] === option ? "white" : "black" }}>
                {option + " declare"}
              </Text>
            </TouchableOpacity>
          ))}
          </View>
    </View>);
};

const Declaration : React.FC<{
    hand: CardInterface[],
    declarations: DeclarationsInterface,
    setDeclarations: Function,
}>= ({hand, declarations, setDeclarations}) => {
    // console.log(hand)
    let has_pig = false;
    let has_sheep = false;
    let has_blood = false;
    let has_doubler = false;
    
    for (const card of hand) {
        if (card.suit === PIG.suit && card.rank === PIG.rank) {
            has_pig = true;
        }
        if (card.suit === SHEEP.suit && card.rank === SHEEP.rank) {
            has_sheep = true;
        }
        if (card.suit === BLOOD.suit && card.rank === BLOOD.rank) {  
            has_blood = true;
        }
        if (card.suit === DOUBLER.suit && card.rank === DOUBLER.rank) {  
            has_doubler = true;
        }
    }

    if (!has_pig && !has_sheep && !has_blood && !has_doubler) {
        return (
            <View>
                <Text>No Special Card to Declare!</Text>
            </View>
        )
    }

    return (<View style={{ flexDirection: 'row', alignItems: 'center' }}>
        {[
            { condition: has_pig, card: PIG, name: "pig" },
            { condition: has_sheep, card: SHEEP, name: "sheep" },
            { condition: has_blood, card: BLOOD, name: "blood" },
            { condition: has_doubler, card: DOUBLER, name: "doubler" }
        ].map(({ condition, card, name }) => 
            condition && (
                <OneDeclaration 
                    key={name} 
                    specialCard={card} 
                    specialCardName={name} 
                    declarations={declarations} 
                    setDeclarations={setDeclarations} 
                />
            )
        )}
    </View>
    );
};

export default Declaration;
