import { FC, useCallback, useContext, useEffect, useState } from 'react';
import { SetUserTeamCallback, UserContext, UserTeam } from './App';
import { PlayerMapContext, PlayerFC, PlayerDetail, getPoints } from './Player';
import { TransferList } from './Transfer';
import { SetTabCallback } from './Login';
import './Team.scss';
// import { idText } from 'typescript';

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
         console.log(JSON.stringify(data.suggestedTeams));
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
            <div id='suggestedTransfers'>
               {players != null && userTeam.transfers != null &&
                  <TransferList
                     players={players}
                     transfers={userTeam.transfers}
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

   const increase = () => { setGw(gw + 1); }
   const decrease = () => { setGw(gw - 1); }

   return (
      <div className='gwSelector'>
         <button className={canDecrease ? selectorStyle : selectorStyle + ' hide'} onClick={decrease}>{'<'}</button>
         {'Gameweek ' + gw}
         <button className={canIncrease ? selectorStyle : selectorStyle + ' hide'} onClick={increase}>{'>'}</button>
         <div>{points.toFixed(2)}</div>
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

   let renderList = [];
   for (let i = 1; i <= 4; i++) {
      let currentRow: any = [];
      let rowFRs = '';
      for (let j in formation[i]) {
         rowFRs += '1fr ';
         currentRow.push(
            <div id={divID(formation[i][j])} style={{ gridArea: divID(formation[i][j]) }}>
               <PlayerFC
                  player={players[formation[i][j]]}
                  selected={selectedPlayer === formation[i][j]}
                  setSelected={setSelectedPlayer}
                  gw={gw}
               />
            </div>
         );
      }
      let templateStyle: string = '\'player' + formation[i].join(' player') + '\'';
      renderList.push(
         <div id={'team' + i.toString()} style={{ display: 'grid', gridTemplateAreas: templateStyle, gridTemplateColumns: rowFRs }}>
            {currentRow}
         </div>
      );
   }
   let subRow: any = [];
   for (let i in suggestedTeams[gw].bench) {
      subRow.push(
         <div id={divID(suggestedTeams[gw].bench[i])} style={{ gridArea: divID(suggestedTeams[gw].bench[i]) }}>
            <PlayerFC
               player={players[suggestedTeams[gw].bench[i]]}
               selected={selectedPlayer === suggestedTeams[gw].bench[i]}
               setSelected={setSelectedPlayer}
               gw={gw}
            />
         </div>
      );
   }
   let templateStyle: string = '\'player' + suggestedTeams[gw].bench.join(' player') + '\'';
   renderList.push(
      <div id='subs' style={{ display: 'grid', gridTemplateAreas: templateStyle, gridTemplateColumns: 'fr fr fr fr' }}>
         {subRow}
      </div>
   );

   return (
      <div id='suggestedTeams'>
         {renderList}
         {selectedPlayer !== null && <PlayerDetail player={players[selectedPlayer]} setSelected={setSelectedPlayer} />}
      </div>
   );
}