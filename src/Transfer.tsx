import { FC } from 'react';
import { getPoints, PlayerMap, PlayerName, Player } from './Player';
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
   const getPlayerTransferCells = (player: Player): JSX.Element[] => {
      let transferItem: JSX.Element[] = [];
      transferItem.push(
         <td>
            <PlayerName player={player} selected={false}
               setSelected={setSelectedPlayer} />
         </td>
      );
      transferItem.push(
         <td>£{(player.current_cost / 10).toFixed(1)}</td>
      );
      transferItem.push(
         <td>{getPoints(player.future_matches[gw]).toFixed(2)}</td>
      );
      return transferItem;
   }
   
   return (
      <tr className='transfer'>
         <td>
            {gw}
         </td>
         {getPlayerTransferCells(players[transfer.id_out])}
         {getPlayerTransferCells(players[transfer.id_in])}
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
                  <th>Player Out</th>
                  <th>→</th>
                  <th>→</th>
                  <th>Player In</th>
                  <th>←</th>
                  <th>←</th>
               </tr>
               {transferRenders}
            </tbody>
         </table>
      </div>
   );
}