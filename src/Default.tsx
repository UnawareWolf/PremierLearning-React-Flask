import { FC, useContext } from 'react';
import { PlayerMapContext, PlayerList } from './Player';

export const Default: FC = () => {
   const players = useContext(PlayerMapContext)
   return (<div>{players != null && <PlayerList players={players} />}</div>);
}