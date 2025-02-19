// Special cards in Gongzhu
import { CardInterface } from '../types';

const PIG : CardInterface = {
    suit: 'spade',
    rank: 'Queen',
    id: '49'
}

const SHEEP: CardInterface = {
    suit: 'diamond',
    rank: 'Jack',
    id: '22'
}

const DOUBLER: CardInterface = {
    suit: 'club',
    rank: '10',
    id: '8'
}

const BLOOD: CardInterface = {
    suit: 'heart',
    rank: 'Ace',
    id: '38'
}

const BlOODS : CardInterface[] = [
    { suit : "heart", rank : "2", id : "heart_02"},
    { suit : "heart", rank : "3", id : "heart_03"},
    { suit : "heart", rank : "4", id : "heart_04"},
    { suit : "heart", rank : "5", id : "heart_05"},
    { suit : "heart", rank : "6", id : "heart_06"},
    { suit : "heart", rank : "7", id : "heart_07"},
    { suit : "heart", rank : "8", id : "heart_08"},
    { suit : "heart", rank : "9", id : "heart_09"},
    { suit : "heart", rank : "10", id : "heart_10"},
    { suit : "heart", rank : "Jack", id : "heart_11"},
    { suit : "heart", rank : "Queen", id : "heart_12"},
    { suit : "heart", rank : "King", id : "heart_13"},
    { suit : "heart", rank : "Ace", id : "heart_14"},
  ]

const SPECIAL_CARDS: CardInterface[] = [PIG, SHEEP, BLOOD, DOUBLER]
export { PIG, SHEEP, DOUBLER, BLOOD, BlOODS, SPECIAL_CARDS };