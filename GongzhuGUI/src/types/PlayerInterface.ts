import { CardInterface } from "./CardInterface";
import { ImageSourcePropType } from 'react-native';

export interface PlayerInterface {
    id?: string;
    name?: string;
    avatar?: ImageSourcePropType;

    hand: CardInterface[];
    collected: CardInterface[];

    playedCards: CardInterface[];
    currentPlayedCard: CardInterface | null;

    score?: number;
    closeDeclaredCards?: CardInterface[] | null;
    openDeclaredCards?: CardInterface[] | null;
}