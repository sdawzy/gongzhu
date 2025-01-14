export interface CardInterface {
    suit: string;
    rank: string;
    id? : string;
    known?: boolean;
}

export interface HandInterface {
    cards: CardInterface[];
}