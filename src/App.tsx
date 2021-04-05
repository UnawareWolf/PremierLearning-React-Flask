import { useEffect, useState, useCallback } from 'react';
import { PlayerMap } from './Player';
import {Team} from './Team';
import { Tabs } from './Tabs';
import logo from './logo.svg';
import './App.css';

export type TabCallback = (tab: string) => void;

interface PlayersState {
   players: PlayerMap | null,
   loading: boolean
}

function App() {

   const [tabSelected, setTabSelected] = useState<string>('default');
   const [{players, loading}, setPlayers] = useState<PlayersState>({players: null, loading: true});
   // const [transfers, setTransfers] = useState<TransferMap>();
   // const [password, setPassword] = useState('');
   // const [email, setEmail] = useState('');

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

   const tabs = ['default', 'team', 'about'];

   return (
      <div className="App">
         <header className="App-header">
            <Tabs selected={tabSelected} setSelected={setTabCallback} tabs={tabs} />
            <img src={logo} className="App-logo" alt="logo" />
            {loading && 'loading'}
            {tabSelected == 'team' && <Team players={players} />}
         </header>
      </div>
   );
}

export default App;
