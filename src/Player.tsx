import { createContext, FC, useContext } from 'react';
import { SetSelectedPlayerCallback } from './Team';
import './Player.scss';
import { UserTeam, UserTeamContext } from './App';

const trimName = (nameIn : string) : string => {
   const maxLen : number = 10;
   let nameText : string;
   nameIn.length > maxLen ? nameText = nameIn.substring(0, maxLen - 1) + ".." : nameText = nameIn;
   return nameText;
}

interface Match {
   minutes: number,
   points: number,
   gameweek: number
}

interface MatchMap {
   [gameweek: number]: Match[]
}

interface Player {
   id: number,
   first_name: string,
   last_name: string,
   team_id: number,
   current_cost: number,
   position: number,
   matches: MatchMap,
   future_matches: MatchMap
}

export interface PlayerMap {
   [id: number]: Player
}

export const PlayerMapContext = createContext<PlayerMap | null>(null);

const isCaptain = (userTeam: UserTeam, playerId: number, gameweek: number): boolean => {
   if (userTeam.suggestedTeams === null) return false;
   return userTeam.suggestedTeams[gameweek].captain === playerId;
}

const isViceCaptain = (userTeam: UserTeam, playerId: number, gameweek: number): boolean => {
   if (userTeam.suggestedTeams === null) return false;
   return userTeam.suggestedTeams[gameweek].vc === playerId;
}

interface PlayerProps {
   player: Player,
   selected: boolean,
   setSelected: SetSelectedPlayerCallback | null,
   gw: number
}

export const PlayerFC: FC<PlayerProps> = ({ player, selected, setSelected, gw }) => {
   const userTeam = useContext(UserTeamContext);

   const handleClick = () => {
      if (setSelected === null) return;
      selected ? setSelected(null) : setSelected(player.id);
   }

   return (
      <button className={selected ? 'player playerSelected' : 'player'} onClick={handleClick} >
         {`${trimName(player.first_name)}  ${trimName(player.last_name)}`}
         {isCaptain(userTeam, player.id, gw) && '\n(C)'}
         {isViceCaptain(userTeam, player.id, gw) && '\n(V)'}
         {/* {'\n' + getPoints(player.future_matches[gw]).toFixed(2)} */}
      </button>
   );
}

interface PlayerNameProps {
   player: Player,
   selected: boolean,
   setSelected: SetSelectedPlayerCallback | null
}

export const PlayerName: FC<PlayerNameProps> = ({ player, selected, setSelected }) => {
   const handleClick = () => {
      if (setSelected === null) return;
      selected ? setSelected(null) : setSelected(player.id);
   }
   return (
      <span className='playerName' onClick={handleClick} >
         {trimName(player.last_name)}
      </span>
   );
}

interface PlayerListProps {
   players: PlayerMap,
   filterText: string
}

const passFilter = (player: Player, filterText: string): boolean => {
   const name: string = player.first_name + ' ' + player.last_name;
   console.log(name + ' ' + filterText)
   return name.includes(filterText);
}

export const PlayerList: FC<PlayerListProps> = ({ players, filterText }) => {
   console.log(filterText);
   let playerRenders = [];
   for (let i in players) {
      if (i in players && passFilter(players[i], filterText)) {
         playerRenders.push(<PlayerFC player={players[i]} selected={false}
            setSelected={null} gw={0} />);
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

export const getPoints = (matches: Match[]): number => {
   let sum: number = 0;
   for (let match in matches) {
      sum += matches[match].points;
   }
   return sum;
}