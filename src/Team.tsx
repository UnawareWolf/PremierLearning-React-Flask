import { FC, useCallback, useContext, useState } from 'react';
import { SetUserTeamCallback, UserContext, UserTeam } from './App';
import { PlayerMapContext, PlayerFC } from './Player';
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

export const TeamPage: FC<TeamPageProps> = ({ userTeam, setUserTeam, setTab }) => {
   const players = useContext(PlayerMapContext);
   const user = useContext(UserContext);
   const [selectedGw, setSelectedGw] = useState<number>(0);

   const setGwCallback = useCallback(
      gw => {
         setSelectedGw(gw);
      },
      [selectedGw]
   );

   const transfersRequest = (e: any) => {
      e.preventDefault();
      setUserTeam({
         ...userTeam,
         transfers: null,
         loading: true
      });
      fetch('/api/opt', { method: 'GET' }).then(res => res.json()).then(data => {
         setUserTeam({
            ...userTeam,
            transfers: data.transfers,
            suggestedTeams: data.suggestedTeams,
            loading: false
         });
         userTeam.suggestedTeams !== null && setSelectedGw(+ Object.keys(userTeam.suggestedTeams)[0]);
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
         {/* <button className='general' onClick={lineupsRequest}>Optimise Lineup</button> */}
         <button className='general' onClick={transfersRequest}>Optimise Team</button>
         <div id='teamPage'>
            <div id='suggestedTeamsWrapper'>
               {userTeam.suggestedTeams !== null &&
                  <GwSelector gameweeks={Object.keys(userTeam.suggestedTeams).map(Number)}
                     gw={selectedGw} setGw={setGwCallback} />}
               <TeamFC gw={selectedGw} suggestedTeams={userTeam.suggestedTeams} />
            </div>

            {/* <div id='suggestedTeams'>

               <div id='p1'>p1</div>
               <div id='p2'>p2</div>
               <div id='p3'>p3</div>
               <div id='p4'>p4</div>
            </div> */}
            <div id='suggestedTransfers'>Transfers</div>
         </div>
         {/* {players != null && userTeam.teamIDs != null && userTeam.teamIDs.map((id) => (
            <PlayerFC player={players[id]} />
         ))}
         {userTeam.loading && 'loading'}
         {players != null && userTeam.transfers != null && <TransferList players={players} transfers={userTeam.transfers} />} */}
      </div>
   );
}

interface GwSelectorProps {
   gameweeks: number[],
   gw: number,
   setGw: SetGwCallback
}

const GwSelector: FC<GwSelectorProps> = ({ gameweeks, gw, setGw }) => {

   let canDecrease: boolean = gameweeks.includes(gw - 1);
   let canIncrease: boolean = gameweeks.includes(gw + 1);

   const increase = () => { setGw(gw + 1); }
   const decrease = () => { setGw(gw - 1); }

   return (
      <div className='gwSelector'>
         {canDecrease && <button className='general gwToggle' onClick={decrease}>{'<'}</button>}
         {'gameweek: ' + gw}
         {canIncrease && <button className='general gwToggle' onClick={increase}>{'>'}</button>}
      </div>
   );
}

interface TeamProps {
   gw: number,
   suggestedTeams: TeamMap | null
}

interface Formation {
   [position: number]: number[]
}

const divID = (id: number) => {
   return 'player' + id.toString();
}

export type SetSelectedPlayerCallback = (selectedPlayer: number | null) => void;

const TeamFC: FC<TeamProps> = ({ gw, suggestedTeams }) => {
   const players = useContext(PlayerMapContext);
   const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);

   const setSelectedPlayerCallback = useCallback(
      selectedPlayer => {
         setSelectedPlayer(selectedPlayer);
      },
      [selectedPlayer]
   );

   if (suggestedTeams === null || players === null || gw === 0) return (<div />);

   let formation: Formation = {
      1: [],
      2: [],
      3: [],
      4: []
   };

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
                  setSelected={setSelectedPlayerCallback}
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
               setSelected={setSelectedPlayerCallback}
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
      </div>
   );
}