import { CardInterface } from "./CardInterface";

export interface PlayerInterface {
    id: string;
    name: string;

    hand: CardInterface[];

    closeDeclared: CardInterface[];
    openDeclared: CardInterface[];
    collected: CardInterface[];

    playedCards: CardInterface[];
    currentPlayedCard: CardInterface | null;

    score: number;
}