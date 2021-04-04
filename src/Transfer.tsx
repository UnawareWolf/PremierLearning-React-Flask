import React, { useEffect, useState, FC } from 'react';
import { PlayerMap, PlayerFC, } from './Player';

interface Transfer {
   id_out: number,
   id_in: number
}

export interface TransferMap {
   [gameweek: number]: Transfer[]
}

interface TransferProps {
   players: PlayerMap,
   transfer: Transfer
}

const TranserFC: FC<TransferProps> = ({ players, transfer }) => {
   return (
      <div>
         <div>
            Out <PlayerFC player={players[transfer.id_out]} />
         </div>
         <div>
            In <PlayerFC player={players[transfer.id_in]} />
         </div>
      </div>
   );
}

interface TransferListProps {
   players: PlayerMap,
   transfers: TransferMap
}

export const TransferList: FC<TransferListProps> = ({ players, transfers }) => {
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