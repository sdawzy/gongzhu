import { CardInterface } from "./CardInterface";
import { ImageSourcePropType } from 'react-native';

export interface PlayerInterface {
    id?: string;
    name?: string;
    avatar?: ImageSourcePropType;

    hand: CardInterface[];
    collectedCards: CardInterface[];

    playedCards: CardInterface[];
    currentPlayedCard?: CardInterface | null;

    score?: number;
    numClosedDeclarations?: number;
    closedDeclaredCards?: CardInterface[] | null;
    openDeclaredCards?: CardInterface[] | null;
}