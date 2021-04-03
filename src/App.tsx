import React, { useState } from 'react';
import logo from './logo.svg';
import './App.css';

function Transfer(transfer: any) {
  return (
    <div>{JSON.stringify(transfer)}</div>
  );
}

function Transfers(transfers: any) {
  let transfersRenderList = [];
  for (let i in transfers) {
    transfersRenderList.push(Transfer(transfers[i]));
  }
  return (
    <div>
      {transfersRenderList}
    </div>
  );
}

function App() {

  const [transfers, setTransfers] = useState();
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');

  const handleSubmit = (e: any) => {
    e.preventDefault();
    fetch('/api/time/', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        'username': email,
        'password': password
      })
    }).then(res => res.json()).then(data => {
      setTransfers((data.transfers));
    });
  }

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <form onSubmit={handleSubmit}>
          <div><input type="text" name="email" placeholder="email" onChange={event => setEmail(event.target.value)} value={email} /></div>
          <div><input type="password" name="password" placeholder="password" onChange={event => setPassword(event.target.value)} value={password} /></div>
          <div><button type="submit">Submit</button></div>
        </form>
        <div>
          {Transfers(transfers)}
        </div>
      </header>
    </div>
  );
}

export default App;
