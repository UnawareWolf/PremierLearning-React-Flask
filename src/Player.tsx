import { createContext, FC } from 'react';
import { SetSelectedPlayerCallback } from './Team';
import './Player.scss';

interface Match {
   minutes: number,
   points: number,
   gameweek: number
}

interface Player {
   id: number,
   first_name: string,
   last_name: string,
   team_id: number,
   current_cost: number,
   position: number,
   matches: Match[],
   future_matches: Match[]
}

export interface PlayerMap {
   [id: number]: Player
}

export const PlayerMapContext = createContext<PlayerMap | null>(null);

interface PlayerProps {
   player: Player,
   selected: boolean,
   setSelected: SetSelectedPlayerCallback | null
}

export const PlayerFC: FC<PlayerProps> = ({ player, selected, setSelected }) => {

   const handleClick = () => {
      console.log(player.id);
      if (setSelected === null) return;
      selected ? setSelected(null) : setSelected(player.id);
   }

   return (
      <button className={selected ? 'player playerSelected' : 'player'} onClick={handleClick} >
         {player.last_name}
      </button>
   );
}

export const PlayerName: FC<PlayerProps> = ({ player, selected, setSelected }) => {
   const handleClick = () => {
      console.log(player.id);
      if (setSelected === null) return;
      selected ? setSelected(null) : setSelected(player.id);
   }
   return (
      <span className='playerName' onClick={handleClick} >
         {player.last_name}
      </span>
   );
}

interface PlayerListProps {
   players: PlayerMap
}

export const PlayerList: FC<PlayerListProps> = ({ players }) => {
   let playerRenders = [];
   for (let i in players) {
      if (i in players) {
         playerRenders.push(<PlayerFC player={players[i]} selected={false} setSelected={null} />);
      }
   }
   return (
      <div>
         {playerRenders}
      </div>
   );
}

interface PlayerDetailProps {
   player: Player
}

export const PlayerDetail: FC<PlayerDetailProps> = ({ player }) => {
   return (
      <div id='selected'>
         <button className='player playerSelected' >
            <div>{player.first_name}</div>
            <div>{player.last_name}</div>
            <div>{player.current_cost}</div>
            <div>{JSON.stringify(player.future_matches)}</div>
         </button>
      </div>
   );
}
