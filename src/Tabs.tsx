import { FC, useState, ReactElement } from 'react';
import { TabCallback } from './App';
import './Tabs.css';

type TabsProps = {
   tabs: string[],
   setSelected: TabCallback
}

export const Tabs: FC<TabsProps> = ({ tabs, setSelected }) => {
   return (
      <div>
         <ul id='Tabs'>
            {tabs.map((tab) => (
               <li><button onClick={() => setSelected(tab)} >{tab}</button></li>
            ))}
         </ul>
      </div>
   );
}