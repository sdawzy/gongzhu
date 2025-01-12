import { CardInterface, CloseDeclaredCard } from "./CardInterface";
import { ImageSourcePropType } from 'react-native';

export interface PlayerInterface {
    id?: string;
    name?: string;
    avatar?: ImageSourcePropType;

    hand: CardInterface[];
    collectedCards: CardInterface[];

    playedCards?: CardInterface[];
    currentPlayedCard?: CardInterface | null;

    score?: number;
    closeDeclaredCards?: CloseDeclaredCard[] | null;
    openDeclaredCards?: CardInterface[] | null;
}