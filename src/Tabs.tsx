import { FC } from 'react';
import './Tabs.scss';

type TabCallback = (tab: string) => void;

type TabsProps = {
   selected: string,
   tabs: string[],
   setSelected: TabCallback
}

export const Tabs: FC<TabsProps> = ({ selected, tabs, setSelected }) => {
   console.log('render tabs');
   return (
      <div className='flexHouse'>
         <div className='tabline'/>
         <div className='tabsolute'>
            {tabs.map((tab) => (
               <button className={tab === selected ? 'tab selected' : 'tab'} onClick={() => setSelected(tab)} >
                  {tab}
               </button>
            ))}
         </div>
      </div>
   );
}