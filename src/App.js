import React, { useState, useEffect, useReducer } from 'react';
import logo from './logo.svg';
import './App.css';

function Transfer(transfer) {
  return (
    <div>{transfer}</div>
  );
}

function Transfers(transfers) {
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

  // const [transfers, handleChange] = useTransfers({0: ""});
  // const [transfersMap, setTransfersMap] = useState({gameweek: 0, transfer})
	// const [transfersList, setTransfersList] = useState([transfersMap]);
  const [transfers, setTransfers] = useState([]);
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
      // for (let transfer in data.transfers) {
      //   console.log(data.transfers[transfer]);
      // }
      setTransfers(data.transfers);
      // setTransfers(data.transfers);
      // console.log(JSON.stringify(data.transfers))
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
          <div><input type="number" name="manager id" placeholder="manager id" onChange={event => setManagerID(event.target.value)} value={managerID} /></div>
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
