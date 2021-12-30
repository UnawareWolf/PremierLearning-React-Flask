import { FC } from 'react';
import { getPoints, PlayerMap, PlayerName, } from './Player';
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
   gw: number,
   players: PlayerMap,
   transfer: Transfer,
   setSelectedPlayer: SetSelectedPlayerCallback
}

const TranserFC: FC<TransferProps> = ({ gw, players, transfer, setSelectedPlayer }) => {
   return (
      <tr className='transfer'>
         <td>
            {gw}
         </td>
         <td>
            <PlayerName player={players[transfer.id_out]} selected={false}
               setSelected={setSelectedPlayer} />
         </td>
         <td>
            {getPoints(players[transfer.id_out].future_matches[gw]).toFixed(2)}
         </td>
         <td>
            <PlayerName player={players[transfer.id_in]} selected={false}
               setSelected={setSelectedPlayer} />
         </td>
         <td>
            {getPoints(players[transfer.id_in].future_matches[gw]).toFixed(2)}
         </td>
      </tr>
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
      for (let j in transfers[i]) {
         transferRenders.push(
            <TranserFC gw={Number.parseInt(i)} players={players} transfer={transfers[i][j]} 
               setSelectedPlayer={setSelectedPlayer} />
         );
      }
   }
   return (
      <div className='transferList'>
         Suggested Transfers
         <table className='transferTable'>
            <tbody>
               <tr>
                  <th>GW</th>
                  <th>Player Out →</th>
                  <th></th>
                  <th>Player In ←</th>
                  <th></th>
               </tr>
               {transferRenders}
            </tbody>
         </table>
      </div>
   );
}