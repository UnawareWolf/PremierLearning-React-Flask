import { FC, useContext, useEffect, useState } from 'react';
import { UserContext } from './Login';
import { PlayerMapContext, PlayerFC } from './Player';
import { TransferMap, TransferList } from './Transfer';

interface TransfersState {
   transfers: TransferMap | null,
   loading: boolean
}

interface TeamIDs {
   ids: number[] | null
}

export const Team: FC = () => {
   console.log('render team page');
   const [{ transfers, loading }, setTransfers] = useState<TransfersState>({ transfers: null, loading: false });
   const [teamIDs, setTeamIDs] = useState<TeamIDs>({ ids: null });
   const players = useContext(PlayerMapContext);
   const user = useContext(UserContext);

   useEffect(() => {
      fetch('/api/teamids', {
         method: 'GET'
      }).then(res => res.json()).then(data => {
         console.log(data.teamIDs);
         setTeamIDs({ ids: data.teamIDs });
      });
   }, [user]);

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
         {players != null && teamIDs.ids != null && teamIDs.ids.map((id) => (
            <PlayerFC player={players[id]} />
         ))}
         {loading && 'loading'}
         {players != null && transfers != null && <TransferList players={players} transfers={transfers} />}
      </div>
   );
}