import { useEffect, useState, useCallback, createContext } from 'react';
import { PlayerMap, PlayerMapContext } from './Player';
import { TeamPage, TeamMap } from './Team';
import { Tabs } from './Tabs';
import './App.scss';
import { Login } from './Login';
import { Default } from './Default';
import { TransferMap } from './Transfer';
import {UserIcon} from './UserIcon';

export interface User {
   name: string,
   loggedIn: boolean
}

export interface TeamInfo {
   sellingPrices: Map<number, number> | null,
   value: number,
   bank: number
}

export interface UserTeam {
   teamIDs: number[] | null,
   teamInfo: TeamInfo | null,
   suggestedTeams: TeamMap | null,
   transfers: TransferMap | null,
   loading: boolean
}

export const defaultUser: User = {
   name: '',
   loggedIn: false
}

export const defaultUserTeam: UserTeam = {
   teamIDs: null,
   teamInfo: null,
   suggestedTeams: null,
   transfers: null,
   loading: false
}

interface TeamArray {
   [team_id: number]: string;
}

export const TeamsContext = createContext<TeamArray>([]);

export const UserTeamContext = createContext<UserTeam>(defaultUserTeam);

export const GWContext = createContext<number>(0);

export const UserContext = createContext<User>(defaultUser);

export type SetUserTeamCallback = (userteam: UserTeam) => void;

interface PlayersState {
   players: PlayerMap | null,
   loading: boolean
}

const getNextGW = (game_events: any[]): number => {
   for (let event_id in game_events) {
      if (game_events[event_id].is_next) {
         return game_events[event_id].id;
      }
   }
   return 0;
}

function App() {

   const [tabSelected, setTabSelected] = useState<string>('default');
   const [{ players, loading }, setPlayers] = useState<PlayersState>({ players: null, loading: true });
   const [user, setUser] = useState<User>(defaultUser);
   const [userTeam, setUserTeam] = useState<UserTeam>(defaultUserTeam);
   const [gw, setNextGW] = useState<number>(0);
   const [teams, setTeams] = useState<TeamArray>([]);

   const setUserTeamCallback = useCallback(
      userTeam => {
         setUserTeam(userTeam);
      },
      [setUserTeam]
   );

   const setUserCallback = useCallback(
      user => {
         setUser(user);
      },
      [setUser]
   );

   const setTabCallback = useCallback(
      tab => {
         setTabSelected(tab);
      },
      [setTabSelected]
   );

   useEffect(() => {
      setPlayers(state => ({ players: state.players, loading: true }));
      fetch('api/general', {
         method: 'GET'
      }).then(res => res.json()).then(data => {
         let apiTeams: TeamArray = [];
         for (let i in data.teams) {
            apiTeams[data.teams[i].id] = data.teams[i].short_name;
         }
         setTeams(apiTeams);
         setNextGW(getNextGW(data.events));
      });
      fetch('/api/players', {
         method: 'GET'
      }).then(res => res.json()).then(data => {
         setPlayers({ players: data.players, loading: false });
      });
   }, []);

   const tabs = ['default', 'team', 'about', 'login'];

   return (
      <div className="App">
         <UserContext.Provider value={user}>
            <div id='top'>
               <Tabs selected={tabSelected} setSelected={setTabCallback} tabs={tabs} />
               {user.loggedIn && <UserIcon setTab={setTabCallback} />}
            </div>
            <div id='bottom'>
               {loading && 'loading'}
               <PlayerMapContext.Provider value={players}>
                  <GWContext.Provider value={gw}>
                     <UserTeamContext.Provider value={userTeam}>
                        {tabSelected === 'team' &&
                           <TeamPage userTeam={userTeam}
                              setUserTeam={setUserTeamCallback}
                              setTab={setTabCallback} />}
                     </UserTeamContext.Provider>
                     {tabSelected === 'login' && <Login setUser={setUserCallback} setUserTeam={setUserTeamCallback} setTab={setTabCallback} />}
                     <TeamsContext.Provider value={teams}>
                        {tabSelected === 'default' && <Default />}
                     </TeamsContext.Provider>
                  </GWContext.Provider>
                  {tabSelected === 'about' && 'Player point predictions are 100% guaranteed to be accurate.'}
               </PlayerMapContext.Provider>
            </div>
         </UserContext.Provider>
      </div>
   );
}

export default App;
