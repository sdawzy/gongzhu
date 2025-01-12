export interface CardInterface {
    suit: string;
    rank: string;
    id? : string;
}

export interface HandInterface {
    cards: CardInterface[];
}

export interface closeDeclaredCard {
    card: CardInterface;
    visible?: boolean;
}