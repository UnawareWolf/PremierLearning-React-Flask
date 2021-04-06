import { FC, useContext, useState } from 'react';
import { UserContext } from './Login';
import { PlayerMapContext } from './Player';
import { TransferMap, TransferList } from './Transfer';

interface TransfersState {
   transfers: TransferMap | null,
   loading: boolean
}

export const Team: FC = () => {
   console.log('render team page');
   const [{ transfers, loading }, setTransfers] = useState<TransfersState>({ transfers: null, loading: false });
   const players = useContext(PlayerMapContext);
   const user = useContext(UserContext);

   const handleSubmit = (e: any) => {
      e.preventDefault();
      setTransfers(state => ({ transfers: state.transfers, loading: true}));
      fetch('/api/optimise/login', {
         method: 'GET',
      }).then(res => res.json()).then(data => {
         setTransfers({ transfers: data.transfers, loading: false});
      });
   }
   return (
      <div>
         {user.loggedIn && <button className='general' onClick={handleSubmit}>Get Transfer Suggestions</button>}
         {loading && 'loading'}
         {players != null && transfers != null && <TransferList players={players} transfers={transfers} />}
      </div>
   );
}