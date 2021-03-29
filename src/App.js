import React, { useState, useEffect, useReducer } from 'react';
import logo from './logo.svg';
import './App.css';

function App() {

	const [transfers, setTransfers] = useState();
  const [password, setPassword] = useState();
  const [email, setEmail] = useState();
  const [managerID, setManagerID] = useState();

  const handleSubmit = (e) => {
    e.preventDefault();
    fetch('/api/time/', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        'manager_id': managerID,
        'username': email,
        'password': password
      })
    }).then(res => res.json()).then(data => {
      setTransfers(data.transfers);
		});
  }

	// useEffect(() => {
	// 	fetch('/api/time/', {
  //     method: 'POST',
  //     headers: {
  //       'Accept': 'application/json',
  //       'Content-Type': 'application/json'
  //     },
  //     body: JSON.stringify({
  //       'username': 'h',
  //       'password': 'a'
  //     })
  //   }).then(res => res.json()).then(data => {
	// 		setCurrentTime(data.time);
	// 	});
	// }, []);

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <form onSubmit={handleSubmit}>
          <p>manager id <input type="number" onChange={event => setManagerID(event.target.value)} value={managerID} /></p>
          <p>username <input type="text" onChange={event => setEmail(event.target.value)} value={email} /></p>
          <p>password <input type="password" onChange={event => setPassword(event.target.value)} value={password} /></p>
          
          <p><button type="submit">Submit</button></p>
        </form>
        <div>
          {/* {transfers.map()} */}
        </div>
	      <p>{transfers}</p>
      </header>
    </div>
  );
}

export default App;
