import { useEffect, useState, useCallback } from 'react';
import { PlayerMap, PlayerMapContext } from './Player';
import {Team} from './Team';
import { Tabs } from './Tabs';
import logo from './logo.svg';
import './App.css';
import { Login, UserContext, User, defaultUser } from './Login';
import {Default} from './Default';

interface PlayersState {
   players: PlayerMap | null,
   loading: boolean
}

function App() {

   const [tabSelected, setTabSelected] = useState<string>('default');
   const [{players, loading}, setPlayers] = useState<PlayersState>({players: null, loading: true});
   const [user, setUser] = useState<User>(defaultUser);

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
      setPlayers(state => ({ players: state.players, loading: true}));
      fetch('/api/players', {
         method: 'GET'
      }).then(res => res.json()).then(data => {
         setPlayers({players: data.players, loading: false});
      });
   }, []);

   const tabs = ['default', 'team', 'about', 'login'];

   return (
      <div className="App">
         <header className="App-header">
            <img src={logo} className="App-logo" alt="logo" />
            {loading && 'loading'}
            <UserContext.Provider value={user}>
               <Tabs selected={tabSelected} setSelected={setTabCallback} tabs={tabs} />
               <PlayerMapContext.Provider value={players}>
                  {tabSelected === 'team' && <Team />}
                  {tabSelected === 'login' && <Login setUser={setUserCallback} />}
                  {tabSelected === 'default' && <Default />}
               </PlayerMapContext.Provider>
            </UserContext.Provider>
         </header>
      </div>
   );
}

export default App;
