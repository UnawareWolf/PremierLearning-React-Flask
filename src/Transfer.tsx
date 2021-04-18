import { FC } from 'react';
import { PlayerMap, PlayerName, } from './Player';
import './Transfer.scss';
import { SetSelectedPlayerCallback } from './Team';

interface Transfer {
   id_out: number,
   id_in: number
}

export interface TransferMap {
   [gameweek: number]: Transfer[]
}

interface TransferProps {
   players: PlayerMap,
   transfer: Transfer,
   setSelectedPlayer: SetSelectedPlayerCallback
}

const TranserFC: FC<TransferProps> = ({ players, transfer, setSelectedPlayer }) => {
   return (
      <div className='transfer' >
         {/* <span> */}
            <PlayerName player={players[transfer.id_out]} selected={false}
               setSelected={setSelectedPlayer} />
            {' > '}
            <PlayerName player={players[transfer.id_in]} selected={false}
               setSelected={setSelectedPlayer} />
         {/* </span> */}
         {/* <div>
            Out <PlayerName player={players[transfer.id_out]} selected={false} setSelected={null} />
         </div>
         <div>
            In <PlayerName player={players[transfer.id_in]} selected={false} setSelected={null} />
         </div> */}
      </div>
   );
}

interface TransferListProps {
   players: PlayerMap,
   transfers: TransferMap,
   setSelectedPlayer: SetSelectedPlayerCallback
}

export const TransferList: FC<TransferListProps> = ({ players, transfers, setSelectedPlayer }) => {
   let transferRenders = [];
   for (let i in transfers) {
      transferRenders.push(<div>{'Gameweek ' + i}</div>);
      for (let j in transfers[i]) {
         transferRenders.push(
            <TranserFC players={players} transfer={transfers[i][j]} 
               setSelectedPlayer={setSelectedPlayer} />
         );
      }
   }
   return (
      <div>
         {transferRenders}
      </div>
   );
}