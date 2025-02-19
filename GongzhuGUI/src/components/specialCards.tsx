// Special cards in Gongzhu
import { CardInterface } from '../types';

const PIG : CardInterface = {
    suit: 'spade',
    rank: '12',
    id: '49'
}

const SHEEP: CardInterface = {
    suit: 'diamond',
    rank: '11',
    id: '22'
}

const DOUBLER: CardInterface = {
    suit: 'club',
    rank: '10',
    id: '8'
}

const BLOOD: CardInterface = {
    suit: 'heart',
    rank: '14',
    id: '38'
}

export { PIG, SHEEP, DOUBLER, BLOOD };