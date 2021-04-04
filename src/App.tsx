import React, { useEffect, useState } from 'react';
import logo from './logo.svg';
import './App.css';

interface Match {
  minutes: number,
  points: number,
  gameweek: number
}

interface Player {
  id: number,
  first_name: string,
  last_name: string,
  team_id: number,
  current_cost: number,
  position: number,
  matches: Match[],
  future_matches: Match[]
}

interface PlayerMap {
  [id: number]: Player
}

interface Transfer {
  id_out: number,
  id_in: number
}

interface TransferMap {
  [gameweek: number]: Transfer[]
}

interface TransferProps {
  players: PlayerMap,
  transfer: Transfer
}

const TranserFC: React.FC<TransferProps> = ({players, transfer}) => {
  return (
    <div>
      <div>
        Out <PlayerFC player={players[transfer.id_out]} />{/*transfer.id_out*/}
      </div>
      <div>
        In <PlayerFC player={players[transfer.id_in]} />{/*transfer.id_in*/}
      </div>
    </div>
  );
}

interface TransferListProps {
  players: PlayerMap,
  transfers: TransferMap
}

const TransferList: React.FC<TransferListProps> = ({players, transfers}) => {
  let transferRenders = [];
  for (let i in transfers) {
    transferRenders.push(<div>{'Gameweek ' + i}</div>);
    for (let j in transfers[i]) {
      transferRenders.push(<TranserFC players={players} transfer={transfers[i][j]} />);
    }
  }
  return (
    <div>
      {transferRenders}
    </div>
  );
}

interface PlayerProps {
  player: Player
}

const PlayerFC : React.FC<PlayerProps> = ({player}) => {
  return (
    <div>
      {player.first_name + ' ' + player.last_name + ' ' + player.future_matches[0].points}
    </div>
  );
}

interface PlayerListProps {
  players: PlayerMap
}

const PlayerList: React.FC<PlayerListProps> = ({players}) => {
  let playerRenders = [];
  for (let i in players) {
    if (i in players) {
      playerRenders.push(<PlayerFC player={players[i]} />);
    }
  }
  return (
    <div>
      {playerRenders}
    </div>
  );
}

function App() {

  const [players, setPlayers] = useState<PlayerMap>();
  const [transfers, setTransfers] = useState<TransferMap>();
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');

  useEffect(() => {
    fetch('/api/players', {
      method: 'GET'
    }).then(res => res.json()).then(data => {
      setPlayers(data.players);
    });
  }, []);

  const handleSubmit = (e: any) => {
    e.preventDefault();
    fetch('/api/optimise/login', {
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
      setTransfers(data.transfers);
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
          {players !== undefined && transfers !== undefined && <TransferList players={players} transfers={transfers} />}
          {/* {players !== undefined && <PlayerList players={players} />} */}
          {/* {JSON.stringify(players)} */}
          {/* {Transfers(transfers)} */}
        </div>
      </header>
    </div>
  );
}

export default App;
