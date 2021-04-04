import { FC, useState, ReactElement } from 'react';
import { TabCallback } from './App';
import './Tabs.css';

type TabsProps = {
   selected: string,
   tabs: string[],
   setSelected: TabCallback
}

export const Tabs: FC<TabsProps> = ({ selected, tabs, setSelected }) => {
   return (
      <div>
         <ul id='Tabs'>
            {tabs.map((tab) => (
               <li>
                  <button className={tab == selected ? 'selected' : ''} onClick={() => setSelected(tab)} >
                     {tab}
                  </button>
               </li>
            ))}
         </ul>
      </div>
   );
}