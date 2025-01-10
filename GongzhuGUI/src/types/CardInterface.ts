export interface CardInterface {
    suit: string;
    rank: string;
    id : string;
}

export interface HandInterface {
    cards: CardInterface[];
}