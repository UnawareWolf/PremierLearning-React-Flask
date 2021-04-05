import { createContext, FC } from 'react';

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
   player: Player
}

export const PlayerFC: FC<PlayerProps> = ({ player }) => {
   return (
      <div>
         {player.first_name + ' ' + player.last_name + ' ' + player.future_matches[0].points}
      </div>
   );
}

interface PlayerListProps {
   players: PlayerMap
}

export const PlayerList: FC<PlayerListProps> = ({ players }) => {
   let playerRenders = [];
   for (let i in players) {
      if (i in players) {
         playerRenders.push(<PlayerFC player={players[i]} />);
      }
   }
   return (
      <div>
         {playerRenders}
      </div>
   );
}