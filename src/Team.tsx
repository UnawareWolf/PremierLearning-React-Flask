import { FC, useState } from 'react';
import {TransferMap} from './Transfer';


export const Team: FC = () => {

   const [transfers, setTransfers] = useState<TransferMap>();
   const [password, setPassword] = useState('');
   const [email, setEmail] = useState('');
   
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
   return (<form onSubmit={handleSubmit}>
      <div><input type="text" name="email" placeholder="email" onChange={event => setEmail(event.target.value)} value={email} /></div>
      <div><input type="password" name="password" placeholder="password" onChange={event => setPassword(event.target.value)} value={password} /></div>
      <div><button type="submit">Submit</button></div>
   </form>);
}