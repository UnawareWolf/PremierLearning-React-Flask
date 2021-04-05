import { FC, useState } from 'react';
import { PlayerMap } from './Player';
import { TransferMap, TransferList } from './Transfer';

interface TeamProps {
   players: PlayerMap | null
}

interface TransfersState {
   transfers: TransferMap | null,
   loading: boolean
}

export const Team: FC<TeamProps> = ({ players }) => {
   console.log('render team page');
   const [{ transfers, loading }, setTransfers] = useState<TransfersState>({ transfers: null, loading: false });
   const [password, setPassword] = useState('');
   const [email, setEmail] = useState('');

   const handleSubmit = (e: any) => {
      e.preventDefault();
      setTransfers(state => ({ transfers: state.transfers, loading: true}));
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
         setTransfers({ transfers: data.transfers, loading: false});
      });
   }
   return (
      <div>
         <form onSubmit={handleSubmit}>
            <div><input type="text" name="email" placeholder="email" onChange={event => setEmail(event.target.value)} value={email} /></div>
            <div><input type="password" name="password" placeholder="password" onChange={event => setPassword(event.target.value)} value={password} /></div>
            <div><button type="submit">Submit</button></div>
         </form>
         {loading && 'loading'}
         {players != null && transfers != null && <TransferList players={players} transfers={transfers} />}
      </div>
   );
}