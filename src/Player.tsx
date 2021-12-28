import { createContext, FC, useContext, useState, useCallback } from 'react';
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
   gameweek: number,
   opponent: string
}

interface MatchMap {
   [gameweek: number]: Match[]
}

interface Player {
   id: number,
   first_name: string,
   last_name: string,
   team_id: number,
   team: string,
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
   return name.toLowerCase().includes(filterText.toLowerCase());
}

export const PlayerList: FC<PlayerListProps> = ({ players, filterText }) => {
   const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);

   const setSelectedPlayerCallback = useCallback(
      selectedPlayer => {
         setSelectedPlayer(selectedPlayer);
      },
      []
   );

   console.log(filterText);
   let playerRenders = [];
   for (let i in players) {
      if (i in players && passFilter(players[i], filterText)) {
         if (selectedPlayer !== null && selectedPlayer === players[i].id) {
            playerRenders.push(<PlayerDetail player={players[i]} setSelected={setSelectedPlayer} />)
         }
         else {
            playerRenders.push(<PlayerFC player={players[i]}
               selected={false}
               setSelected={setSelectedPlayerCallback} gw={0} />);
         }
      }
   }
   return (
      <div>
         {playerRenders}
      </div>
   );
}

interface PlayerDetailProps {
   player: Player,
   setSelected: SetSelectedPlayerCallback,
}

const getMatchesInGW = (player: Player, gw: number): JSX.Element[] => {
   let matchesInGw = [];
   let atLeastOne: boolean = false;
   for (let match in player.matches[gw]) {
      matchesInGw.push(
         <tr>
            <td>{!atLeastOne && gw}</td>
            <td>{player.matches[gw][match].opponent}</td>
            <td>{player.matches[gw][match].points}</td>
            <td>{player.matches[gw][match].minutes}</td>
            <td>✓</td>
         </tr>
      );
      atLeastOne = true;
   }
   for (let match in player.future_matches[gw]) {
      matchesInGw.push(
         <tr>
            <td>{!atLeastOne && gw}</td>
            <td>{player.future_matches[gw][match].opponent}</td>
            <td>{player.future_matches[gw][match].points.toFixed(2)}</td>
            <td>{player.future_matches[gw][match].minutes.toFixed(0)}</td>
            <td>-</td>
         </tr>
      );
      atLeastOne = true;
   }
   if (!atLeastOne) {
      matchesInGw.push(
         <tr>
            <td>{gw}</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
         </tr>
      );
   }
   return matchesInGw;
}

const getPosition = (posId: number): string => {
   switch(posId){
      case 1: return 'GKP'
      case 2: return 'DEF'
      case 3: return 'MID'
      default: return 'ATT'
   }
}

const sumPoints = (player: Player): number => {
   let sum: number = 0;
   for (let gw in player.matches) {
      sum += getPoints(player.matches[gw]);
   }
   return sum;
}

export const PlayerDetail: FC<PlayerDetailProps> = ({ player, setSelected }) => {
   const handleClick = () => {
      setSelected(null);
   }

   let statTable: JSX.Element[] = [];
   for (let i: number = 1; i <= 32; i++) {
      Array.prototype.push.apply(statTable, getMatchesInGW(player, i));
   }
   Array.prototype.push.apply(statTable, getMatchesInGW(player, 0));

   return (
      <div id='selected'>
         <button className='player playerSelected' >
            <table id='playerName'>
               <tr>
                  <th>{player.first_name}</th>
                  <th rowSpan={2} id='hideDetail' onClick={handleClick}>X</th>
               </tr>
               <tr>
                  <th>{player.last_name}</th>
               </tr>
            </table>

            <table id='playerInfo'>
               <tr>
                  <th>Team</th>
                  <th>Position</th>
                  <th>Total</th>
                  <th>Price</th>
                  <th>Pred</th>
               </tr>
               <tr>
                  <td>{player.team}</td>
                  <td>{getPosition(player.position)}</td>
                  <td>{sumPoints(player)}</td>
                  <td>£{(player.current_cost/10).toFixed(1)}</td>
                  <td>{getPoints(player.future_matches[0]).toFixed(2)}</td>
               </tr>
            </table>

            <table id='playerStats'>
               <tr>
                  <td>GW</td>
                  <td>OPP</td>
                  <td>Pts</td>
                  <td>Mins</td>
                  <td>Played</td>
               </tr>
               {statTable}
            </table>
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