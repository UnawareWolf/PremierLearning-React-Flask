import React, { useEffect, useState, useCallback, FC } from 'react';
import { PlayerMap } from './Player';
import {Team} from './Team';
import { TransferMap, TransferList } from './Transfer';
import { Tabs } from './Tabs';
import logo from './logo.svg';
import './App.css';

export type TabCallback = (tab: string) => void;

function App() {

   const [tabSelected, setTabSelected] = useState<string>('default');
   const [players, setPlayers] = useState<PlayerMap>();
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
      fetch('/api/players', {
         method: 'GET'
      }).then(res => res.json()).then(data => {
         setPlayers(data.players);
      });
   }, []);

   // const handleSubmit = (e: any) => {
   //    e.preventDefault();
   //    fetch('/api/optimise/login', {
   //       method: 'POST',
   //       headers: {
   //          'Accept': 'application/json',
   //          'Content-Type': 'application/json'
   //       },
   //       body: JSON.stringify({
   //          'username': email,
   //          'password': password
   //       })
   //    }).then(res => res.json()).then(data => {
   //       setTransfers(data.transfers);
   //    });
   // }

   const tabs = ['default', 'team', 'about'];



   return (
      <div className="App">
         <Tabs setSelected={setTabCallback} tabs={tabs} />
         {tabSelected == 'team' && <Team />}
         <header className="App-header">
            <img src={logo} className="App-logo" alt="logo" />
            {/* <form onSubmit={handleSubmit}>
               <div><input type="text" name="email" placeholder="email" onChange={event => setEmail(event.target.value)} value={email} /></div>
               <div><input type="password" name="password" placeholder="password" onChange={event => setPassword(event.target.value)} value={password} /></div>
               <div><button type="submit">Submit</button></div>
            </form> */}
            {/* <div> */}
               {/* {players !== undefined && transfers !== undefined && <TransferList players={players} transfers={transfers} />} */}
            {/* </div> */}
         </header>
      </div>
   );
}

export default App;
