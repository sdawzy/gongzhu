// Special cards in Gongzhu
import { CardInterface } from '../types';

const PIG : CardInterface = {
    suit: 'spade',
    rank: '12',
    id: 'spade_12'
}

const SHEEP: CardInterface = {
    suit: 'diamond',
    rank: '11',
    id: 'diamond_11'
}

const DOUBLER: CardInterface = {
    suit: 'club',
    rank: '10',
    id: 'club_10'
}

const BLOOD: CardInterface = {
    suit: 'heart',
    rank: '14',
    id: 'heart_14'
}

export { PIG, SHEEP, DOUBLER, BLOOD };