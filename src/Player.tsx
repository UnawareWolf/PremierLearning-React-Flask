import { createContext, FC, useContext, useState, useCallback } from 'react';
import { SetSelectedPlayerCallback } from './Team';
import './Player.scss';
import { UserTeam, UserTeamContext, GWContext } from './App';

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
   code: number,
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
      <div className={selected ? 'playerSelected' : 'player'} onClick={handleClick} >
         {`${trimName(player.first_name)}  ${trimName(player.last_name)}`}
         {isCaptain(userTeam, player.id, gw) && '\n(C)'}
         {isViceCaptain(userTeam, player.id, gw) && '\n(V)'}
         {/* {'\n' + getPoints(player.future_matches[gw]).toFixed(2)} */}
      </div>
   );
}

export const PlayerCard: FC<PlayerProps> = ({ player, selected, setSelected, gw }) => {
   const userTeam = useContext(UserTeamContext);

   const handleClick = () => {
      if (setSelected === null) return;
      selected ? setSelected(null) : setSelected(player.id);
   }

   return (
      <div className='cardHouse'>
         <div className='imgContainer'>
            <img className='center card' src={'https://resources.premierleague.com/premierleague/photos/players/110x140/p' + player.code + '.png'} alt='' />
         </div>
         <div className={selected ? 'cardSelected' : 'playerCard'} onClick={handleClick} >
            {`${trimName(player.last_name)}`}
            {isCaptain(userTeam, player.id, gw) && '\n(C)'}
            {isViceCaptain(userTeam, player.id, gw) && '\n(V)'}
            {/* {'\n' + getPoints(player.future_matches[gw]).toFixed(2)} */}
         </div>
         <div className='pointsCard'>
            {'\n' +
               getPoints(player.future_matches[gw]).toFixed(2) + ' ' +
               listOpponents(player.future_matches[gw])}
         </div>
      </div>
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

   let playerRenders = [];
   for (let i in players) {
      if (i in players && passFilter(players[i], filterText)) {
         if (selectedPlayer !== null && selectedPlayer === players[i].id) {
            playerRenders.push(<PlayerDetail key={players[i].id}
               player={players[i]} setSelected={setSelectedPlayer} />)
         }
         else {
            playerRenders.push(<PlayerFC key={players[i].id} player={players[i]}
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

interface MatchRowProps {
   gw: string,
   opponent: string,
   points: string,
   minutes: string,
   played: string
}

const MatchRow: FC<MatchRowProps> = (props: MatchRowProps) => {
   return(
      <tr>
         <td>{props.gw}</td>
         <td>{props.opponent}</td>
         <td>{props.points}</td>
         <td>{props.minutes}</td>
         <td>{props.played}</td>
      </tr>
   );
}

const getMatchesInGW = (player: Player, gw: number): JSX.Element[] => {
   let matchesInGw = [];
   let atLeastOne: boolean = false;
   for (let match in player.matches[gw]) {
      matchesInGw.push(
         <MatchRow
            gw={atLeastOne ? '' : gw.toString()} 
            opponent={player.matches[gw][match].opponent}
            points={player.matches[gw][match].points.toString()}
            minutes={player.matches[gw][match].minutes.toString()}
            played='✓'
         />
      );
      atLeastOne = true;
   }
   for (let match in player.future_matches[gw]) {
      matchesInGw.push(
         <MatchRow
            gw={atLeastOne ? '' : gw.toString()} 
            opponent={player.future_matches[gw][match].opponent}
            points={player.future_matches[gw][match].points.toFixed(2).toString()}
            minutes={player.future_matches[gw][match].minutes.toFixed(0).toString()}
            played='-'
         />
      );
      atLeastOne = true;
   }
   if (!atLeastOne) {
      matchesInGw.push(
         <MatchRow
            gw={gw.toString()}
            opponent='-'
            points='-'
            minutes='-'
            played='-'
         />
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
   const gw: number = useContext(GWContext);

   const handleClick = () => {
      setSelected(null);
   }

   let statTable: JSX.Element[] = [];
   for (let i: number = 1; i <= 38; i++) {
      Array.prototype.push.apply(statTable, getMatchesInGW(player, i));
   }
   Array.prototype.push.apply(statTable, getMatchesInGW(player, 0));

   return (
      <div id='selected'>
         <div className='player playerSelected' >
            <table id='playerName'>
               <tbody>
                  <tr>
                     <th>{player.first_name}</th>
                     <th rowSpan={2} id='hideDetail' onClick={handleClick}>X</th>
                  </tr>
                  <tr>
                     <th>{player.last_name}</th>
                  </tr>
               </tbody>
            </table>
            
            <img className='center' src={'https://resources.premierleague.com/premierleague/photos/players/110x140/p' + player.code + '.png'} alt='' />

            <table id='playerInfo'>
               <tbody>
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
                     <td>{getPoints(player.future_matches[gw]).toFixed(2)}</td>
                  </tr>
               </tbody>
            </table>

            <table id='playerStats'>
               <tbody>
                  <tr>
                     <td>GW</td>
                     <td>OPP</td>
                     <td>Pts</td>
                     <td>Mins</td>
                     <td>Played</td>
                  </tr>
                  {statTable}
               </tbody>
            </table>
         </div>
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

const listOpponents = (matches: Match[]): string => {
   if (matches === undefined || matches.length === 0) {
      return '(-)';
   }
   let opps: string = '(';
   for (let match in matches) {
      opps += matches[match].opponent + ', ';
   }
   opps = opps.substring(0, opps.length - 2);
   opps += ')';
   return opps;
}