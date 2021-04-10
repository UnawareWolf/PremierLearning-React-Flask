import { FC, useContext } from 'react';
import { SetUserTeamCallback, UserContext, UserTeam } from './App';
import { PlayerMapContext, PlayerFC } from './Player';
import { TransferList } from './Transfer';

interface TeamProps {
   userTeam: UserTeam,
   setUserTeam: SetUserTeamCallback
}

export const TeamFC: FC<TeamProps> = ({ userTeam, setUserTeam }) => {
   const players = useContext(PlayerMapContext);
   const user = useContext(UserContext);

   const handleSubmit = (e: any) => {
      e.preventDefault();
      setUserTeam({
         ...userTeam,
         transfers: null,
         loading: true
      });
      fetch('/api/optimise', {
         method: 'GET',
      }).then(res => res.json()).then(data => {
         setUserTeam({
            ...userTeam,
            transfers: data.transfers,
            loading: false
         })
      });
   }

   return (
      <div>
         {user.loggedIn && <button className='general' onClick={handleSubmit}>Get Transfer Suggestions</button>}
         {players != null && userTeam.teamIDs != null && userTeam.teamIDs.map((id) => (
            <PlayerFC player={players[id]} />
         ))}
         {userTeam.loading && 'loading'}
         {players != null && userTeam.transfers != null && <TransferList players={players} transfers={userTeam.transfers} />}
      </div>
   );
}