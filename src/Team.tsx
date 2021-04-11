import { FC, useContext } from 'react';
import { SetUserTeamCallback, UserContext, UserTeam } from './App';
import { PlayerMapContext, PlayerFC } from './Player';
import { TransferList } from './Transfer';
import { SetTabCallback } from './Login';
import './Team.scss';
import { idText } from 'typescript';

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

export const TeamPage: FC<TeamPageProps> = ({ userTeam, setUserTeam, setTab }) => {
   const players = useContext(PlayerMapContext);
   const user = useContext(UserContext);

   const transfersRequest = (e: any) => {
      e.preventDefault();
      setUserTeam({
         ...userTeam,
         transfers: null,
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
         {/* <button className='general' onClick={lineupsRequest}>Optimise Lineup</button> */}
         <button className='general' onClick={transfersRequest}>Optimise Team</button>
         <div id='teamPage'>
            <TeamFC gw={31} suggestedTeams={userTeam.suggestedTeams} />
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

interface TeamProps {
   gw: number,
   suggestedTeams: TeamMap | null
}

interface Formation {
   [position: number]: string[]
}

const TeamFC: FC<TeamProps> = ({ gw, suggestedTeams }) => {
   const players = useContext(PlayerMapContext);
   if (suggestedTeams == null || players == null) return (<div>null</div>);

   let formation : Formation = {
      1: [],
      2: [],
      3: [],
      4: []
   };
   suggestedTeams[gw].starters.map((id) => (
      formation[players[id].position].push('player' + id.toString())
   ));

   let renderList = [];
   for (let i = 1; i <= 4; i++) {
      let currentRow: any = [];
      let rowFRs = '';
      for (let j in formation[i]) {
         rowFRs += '1fr ';
         currentRow.push(
            <div id={formation[i][j]} style={{gridArea: formation[i][j]}}>
               {formation[i][j]}
            </div>
         );
      }
      let templateStyle: string = '\'' + formation[i].join(' ') + '\'';
      console.log(templateStyle);
      renderList.push(
         <div id={'row' + i.toString()} style={{display: 'grid', gridTemplateAreas: templateStyle, gridTemplateColumns: rowFRs}}>
            {currentRow}
         </div>
      );
   }

   console.log(formation);

   return (
      <div id='suggestedTeams'>
         {renderList}
         {/* <div id=''>

         </div>
         <div id='p1'>{suggestedTeams[gw].starters[0]}</div>
         <div id='p2'>p2</div>
         <div id='p3'>p3</div>
         <div id='p4'>p4</div> */}
      </div>
   );
}