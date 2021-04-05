import { FC } from 'react';
import './Tabs.css';

type TabCallback = (tab: string) => void;

type TabsProps = {
   selected: string,
   tabs: string[],
   setSelected: TabCallback
}

export const Tabs: FC<TabsProps> = ({ selected, tabs, setSelected }) => {
   console.log('render tabs');
   return (
      <div>
         <ul id='Tabs'>
            {tabs.map((tab) => (
               <li>
                  <button className={tab === selected ? 'selected' : 'unselected'} onClick={() => setSelected(tab)} >
                     {tab}
                  </button>
               </li>
            ))}
         </ul>
      </div>
   );
}