import { FC, useCallback, useContext, useEffect, useState } from 'react';
import { SetUserTeamCallback, UserContext, UserTeam } from './App';
import { PlayerMapContext, PlayerDetail, getPoints, PlayerCard } from './Player';
import { TransferList } from './Transfer';
import { SetTabCallback } from './Login';
import './Team.scss';

export interface StructuredTeam {
   starters: number[],
   bench: number[],
   captain: number,
   vc: number
}

export interface TeamMap {
   [gameweek: number]: StructuredTeam
}

interface TeamPageProps {
   userTeam: UserTeam,
   setUserTeam: SetUserTeamCallback,
   setTab: SetTabCallback
}

type SetGwCallback = (gw: number) => void;

export type SetSelectedPlayerCallback = (selectedPlayer: number | null) => void;

export const TeamPage: FC<TeamPageProps> = ({ userTeam, setUserTeam, setTab }) => {
   const players = useContext(PlayerMapContext);
   const user = useContext(UserContext);
   const [selectedGw, setSelectedGw] = useState<number>(0);
   const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);
   const [gwPoints, setGwPoints] = useState<number>(0);

   const setSelectedPlayerCallback = useCallback(
      selectedPlayer => {
         setSelectedPlayer(selectedPlayer);
      },
      []
   );

   useEffect(() => {
      if (userTeam.suggestedTeams !== null) setSelectedGw(+ Object.keys(userTeam.suggestedTeams)[0]);
   }, [userTeam.suggestedTeams, userTeam.loading]);

   useEffect(() => {
      if (userTeam.suggestedTeams === null || players === null ||
         userTeam.suggestedTeams[selectedGw] === undefined) {
         setGwPoints(0);
         return;
      }
      let pointSum = 0;
      for (let id of userTeam.suggestedTeams[selectedGw].starters) {
         pointSum += getPoints(players[id].future_matches[selectedGw]);
      }
      pointSum += getPoints(players[userTeam.suggestedTeams[selectedGw].captain].future_matches[selectedGw]);
      setGwPoints(pointSum);
   }, [selectedGw, userTeam.suggestedTeams, players]);

   const setGwCallback = useCallback(
      gw => {
         setSelectedGw(gw);
      },
      []
   );

   const transfersRequest = (e: any) => {
      e.preventDefault();
      setUserTeam({
         ...userTeam,
         loading: true
      });
      fetch('/api/opt', { method: 'GET' }).then(res => res.json()).then(data => {
         setUserTeam({
            ...userTeam,
            transfers: data.transfers,
            suggestedTeams: data.suggestedTeams,
            loading: false
         });
      });
   }

   const loginNav = () => {
      setTab('login');
   }

   if (!user.loggedIn) {
      return (<div><span id='loginSuggestion' onClick={loginNav}>Log in</span> to use this page</div>);
   }

   return (
      <div>
         {userTeam.loading ? <div>loading ...</div> :
            <button className='general' onClick={transfersRequest}>Optimise Team</button>}
         <div id='teamPage'>
            <div id='suggestedTeamsWrapper'>
               {userTeam.suggestedTeams !== null &&
                  <GwSelector
                     gameweeks={Object.keys(userTeam.suggestedTeams).map(Number)}
                     gw={selectedGw}
                     setGw={setGwCallback} 
                     points={gwPoints} />}
               <TeamFC
                  gw={selectedGw}
                  suggestedTeams={userTeam.suggestedTeams}
                  selectedPlayer={selectedPlayer}
                  setSelectedPlayer={setSelectedPlayerCallback} />
            </div>
            {players!= null && selectedPlayer !== null && <PlayerDetail player={players[selectedPlayer]} setSelected={setSelectedPlayer} />}
            {userTeam.teamInfo !== null &&
                  <TeamInfo value={userTeam.teamInfo.value} bank={userTeam.teamInfo.bank} />}
            <div id='suggestedTransfers'>
               {players !== null && userTeam.transfers !== null &&
                  userTeam.teamInfo !== null && userTeam.teamInfo.sellingPrices !== null &&
                  <TransferList
                     players={players}
                     transfers={userTeam.transfers}
                     sellingPrices={userTeam.teamInfo.sellingPrices}
                     setSelectedPlayer={setSelectedPlayerCallback} />}
            </div>
         </div>
      </div>
   );
}

export interface GwSelectorProps {
   gameweeks: number[],
   gw: number,
   setGw: SetGwCallback,
   points: number
}

const selectorStyle = 'general gwToggle';

export const GwSelector: FC<GwSelectorProps> = ({ gameweeks, gw, setGw, points }) => {
   let canDecrease: boolean = gameweeks.includes(gw - 1);
   let canIncrease: boolean = gameweeks.includes(gw + 1);

   const increase = () => { canIncrease && setGw(gw + 1); }
   const decrease = () => { canDecrease && setGw(gw - 1); }

   return (
      <div className='gwSelector'>
         <button className={canDecrease ? selectorStyle : selectorStyle + ' hide'} onClick={decrease}>{'<'}</button>
         {'GW ' + gw}
         <button className={canIncrease ? selectorStyle : selectorStyle + ' hide'} onClick={increase}>{'>'}</button>
         <div className='pointTotal'>{points.toFixed(0) + ' Points'}</div>
      </div>
   );
}

interface TeamInfoProps {
   value: number,
   bank: number
}

const TeamInfo: FC<TeamInfoProps> = ({ value, bank }) => {
   return (
      <div className='teamInfo'>
         <div>Team Info</div>
         <table className='teamInfoTable'>
            <tbody>
               <tr>
                  <th>Squad Value</th>
                  <td>{'£' + value}</td>
               </tr>
               <tr>
                  <th>Budget</th>
                  <td>{'£' + bank}</td>
               </tr>
            </tbody>
         </table>
      </div>
   );
}

interface TeamProps {
   gw: number,
   suggestedTeams: TeamMap | null,
   selectedPlayer: null | number,
   setSelectedPlayer: SetSelectedPlayerCallback
}

interface Formation {
   [position: number]: number[]
}

const divID = (id: number) => {
   return 'player' + id.toString();
}

const TeamFC: FC<TeamProps> = ({ gw, suggestedTeams, selectedPlayer, setSelectedPlayer }) => {
   const players = useContext(PlayerMapContext);

   if (suggestedTeams === null || players === null || gw === 0) return (<div />);

   let formation: Formation = { 1: [], 2: [], 3: [], 4: [] };

   suggestedTeams[gw].starters.map((id) => (formation[players[id].position].push(id)));

   let playerId : number;
   let teamRender = [];
   for (let i = 1; i <= 4; i++) {
      let currentRow: any = [];
      let rowFRs = '';
      for (let j in formation[i]) {
         playerId = formation[i][j];
         rowFRs += '1fr ';
         currentRow.push(
            <div id={divID(playerId)} style={{ gridArea: divID(playerId) }}>
               <PlayerCard
                  key={playerId}
                  player={players[playerId]}
                  selected={selectedPlayer === playerId}
                  setSelected={setSelectedPlayer}
                  gw={gw}
               />
            </div>
         );
      }
      let templateStyle: string = '\'player' + formation[i].join(' player') + '\'';
      teamRender.push(
         <div id={'team' + i.toString()} style={{ display: 'grid', gridTemplateAreas: templateStyle, gridTemplateColumns: rowFRs }}>
            {currentRow}
         </div>
      );
   }
   let subRow: any = [];
   for (let i in suggestedTeams[gw].bench) {
      playerId = suggestedTeams[gw].bench[i];
      subRow.push(
         <div id={divID(playerId)} style={{ gridArea: divID(playerId) }}>
            <PlayerCard
               key={playerId}
               player={players[playerId]}
               selected={selectedPlayer === playerId}
               setSelected={setSelectedPlayer}
               gw={gw}
            />
         </div>
      );
   }
   let templateStyle: string = '\'player' + suggestedTeams[gw].bench.join(' player') + '\'';
   
   let subRender = [];
   subRender.push(
      <div id='subs' style={{ display: 'grid', gridTemplateAreas: templateStyle, gridTemplateColumns: 'fr fr fr fr' }}>
         {subRow}
      </div>
   );

   return (
      <div>
         <div id='suggestedTeams'>
            {teamRender}
         </div>
         <div id='subs'>
            {subRender}
         </div>
      </div>
   );
}