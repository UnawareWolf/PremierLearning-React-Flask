import { FC, useContext, useState, useCallback, KeyboardEvent } from 'react';
import { PlayerMapContext, PlayerList, PlayerMap } from './Player';
import './Default.scss';

export const Default: FC = () => {
   const players = useContext(PlayerMapContext);
   return (<div>{players != null && <SearchZone players={players} />}</div>);
}

interface SearchProps {
   players: PlayerMap
}

type SetFilterTextCallback = (filterText: string) => void;

const SearchZone: FC<SearchProps> = ({ players }) => {

   const [filterText, setFilterText] = useState<string>("");

   const setFilterTextCallback = useCallback(
      filterText => {
         setFilterText(filterText);
      },
      []
   );

   return (
      <div className='searchZone'>
         <SearchBox setFilterText={setFilterTextCallback} />
         <PlayerList players={players} filterText={filterText} />
      </div>
   )
}

interface SearchBoxProps {
   setFilterText: SetFilterTextCallback
}

const SearchBox: FC<SearchBoxProps> = ({ setFilterText }) => {
   const [inputText, setInputText] = useState<string>('');

   const handleClick = () => {
      setFilterText(inputText);
   }

   const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
      if (event.key === 'Enter') {
         handleClick();
      }
   }

   return (
      <div className='searchBox'>
         <input type='text' id='searchTextBox' value={inputText} onKeyDown={handleKeyDown} onChange={e => setInputText(e.target.value)}/>
         <div id='searchIcon' onClick={handleClick} />
      </div>
   )
}