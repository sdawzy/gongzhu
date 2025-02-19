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

const SPECIAL_CARDS: CardInterface[] = [PIG, SHEEP, DOUBLER, BLOOD]
export { PIG, SHEEP, DOUBLER, BLOOD, SPECIAL_CARDS };