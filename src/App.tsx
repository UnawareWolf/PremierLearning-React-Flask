import { useEffect, useState, useCallback, createContext } from 'react';
import { PlayerMap, PlayerMapContext } from './Player';
import { TeamPage, StructuredTeam, TeamMap } from './Team';
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

export interface UserTeam {
   teamIDs: number[] | null,
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
   suggestedTeams: null,
   transfers: null,
   loading: false
}

export const UserContext = createContext<User>(defaultUser);

export type SetUserTeamCallback = (userteam: UserTeam) => void;

interface PlayersState {
   players: PlayerMap | null,
   loading: boolean
}

function App() {

   const [tabSelected, setTabSelected] = useState<string>('default');
   const [{ players, loading }, setPlayers] = useState<PlayersState>({ players: null, loading: true });
   const [user, setUser] = useState<User>(defaultUser);
   const [userTeam, setUserTeam] = useState<UserTeam>(defaultUserTeam);

   const setUserTeamCallback = useCallback(
      userTeam => {
         setUserTeam(userTeam);
      },
      [setUserTeam]
   )

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
                  {tabSelected === 'team' && <TeamPage userTeam={userTeam} setUserTeam={setUserTeamCallback} setTab={setTabCallback} />}
                  {tabSelected === 'login' && <Login setUser={setUserCallback} setUserTeam={setUserTeamCallback} setTab={setTabCallback} />}
                  {tabSelected === 'default' && <Default />}
                  {tabSelected === 'about' && 'Player point predictions are 100% guaranteed to be accurate.'}
               </PlayerMapContext.Provider>
            </div>
         </UserContext.Provider>
      </div>
   );
}

export default App;
