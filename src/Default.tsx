import { FC, useContext, useState, KeyboardEvent, useReducer, useCallback } from 'react';
import { PlayerMapContext, PlayerList, PlayerMap, getPosition } from './Player';
import './Default.scss';
import './Filter.scss';
import { TeamsContext } from './App';

export const Default: FC = () => {
   const players = useContext(PlayerMapContext);
   return (<div>{players != null && <SearchZone players={players} />}</div>);
}

interface SearchProps {
   players: PlayerMap
}

export const SortOptions = {
   Default: 'Default',
   Cost: 'Cost',
   PointsGW: 'Points Next GW',
   PointsFutureAvg: 'Future Point Avg'
 } as const;
 export type SortOption = typeof SortOptions[keyof typeof SortOptions];

type DispatchFilterCallback = (filterOptions: FilterActions) => void;

type FilterActions = 
   { type: "text"; text: string }
   | { type: "team"; team: string; on: boolean }
   | { type: "pos"; pos: number; on: boolean }
   | { type: "reset" };

export interface FilterOptions {
   text: string | null,
   teams: string[],
   positions: number[]
};

const defaultFilterOptions: FilterOptions = {
   text: null,
   teams: [],
   positions: []
};

const removeFromArray = (arr: any[], item: any): any[] => {
   let idx = arr.indexOf(item);
   while (idx !== -1) {
      arr = [...arr.slice(0, idx), ...arr.slice(idx + 1)];
      idx = arr.indexOf(item);
   }
   return arr;
}

const FilterReducer = (state: FilterOptions, action: FilterActions) => {
   switch (action.type) {
      case "text":
         return { ...state, text: action.text };
      case "team":
         return action.on ?
            {...state, teams: [...state.teams, action.team]} :
            {...state, teams: removeFromArray(state.teams, action.team)};
      case "pos":
         return action.on ?
            {...state, positions: [...state.positions, action.pos]} :
            { ...state, positions: removeFromArray(state.positions, action.pos) };
      case "reset":
         return { ...state, teams: [], positions: [] };
      default:
         return state;
   }
}

export type SetSortCallback = (sortOption: SortOption) => void;

const SearchZone: FC<SearchProps> = ({ players }) => {
   const [sortBy, setSortBy] = useState<SortOption>(SortOptions.Default);
   const [filter, dispatchFilter] = useReducer(FilterReducer, defaultFilterOptions);

   const setSortCallback = useCallback(
      sortOption => {
         setSortBy(sortOption);
      },
      [setSortBy]
   );

   return (
      <div className='searchZone'>
         <SearchBox dispatchFilter={dispatchFilter} />
         <FilterBox filter={filter} dispatchFilter={dispatchFilter}
            sort={sortBy} setSort={setSortCallback} />
         <PlayerList players={players} filter={filter} sortBy={sortBy} />
      </div>
   );
}

interface FilterBoxProps {
   filter: FilterOptions,
   dispatchFilter: DispatchFilterCallback,
   sort: SortOption,
   setSort: SetSortCallback
}

const FilterBox: FC<FilterBoxProps> = ({ filter, dispatchFilter, sort, setSort }) => {
   const [expand, setExpand] = useState<boolean>(false);
   const teams = useContext(TeamsContext);

   let teamTags = [];
   let posTags = [];
   let sortTags = [];
   if (expand) {
      for (let i = 1; i <= 20; i++) {
         let alreadySet = filter.teams.includes(teams[i]);
         teamTags.push(<div className={alreadySet ? 'teamFilter selected' : 'teamFilter'}
            onClick={() => dispatchFilter({"type": "team", team: teams[i], on: !alreadySet})}>{teams[i]}</div>);
      }
      for (let i = 1; i <= 4; i++) {
         let alreadySet = filter.positions.includes(i);
         posTags.push(<div className={alreadySet ? 'posFilter selected' : 'posFilter'}
            onClick={() => dispatchFilter({"type": "pos", pos: i, on: !alreadySet})}>{getPosition(i)}</div>);
      }
      for (const sOpt of Object.values(SortOptions)) {
         let alreadySet = sort === sOpt;
         sortTags.push(<div className={alreadySet ? 'sortOption selected' : 'sortOption'}
            onClick={() => setSort(sOpt)}>{sOpt}</div>);
      }
   }

   return (
      <div>
         {!expand &&
            <div id='filterHouse'>
               <div id="filter" onClick={() => setExpand(true)}>...</div>
            </div>
         }
         {expand &&
            <div id="expandedFilter">
               <div className='close' onClick={() => setExpand(false)}>X</div>
               <div className='filterHeading'>FILTERS</div>
               Teams
               <div className='teamGrid'>{teamTags}</div>
               Positions
               <div className='posGrid'>{posTags}</div>
               <div className='filterHeading'>SORT</div>
               <div className='sortGrid'>{sortTags}</div>
               <div className='reset' onClick={() => dispatchFilter({type: 'reset'})}>reset</div>
            </div>
         }
      </div>
   );
}

interface SearchBoxProps {
   dispatchFilter: DispatchFilterCallback
}

const SearchBox: FC<SearchBoxProps> = ({ dispatchFilter }) => {
   const [inputText, setInputText] = useState<string>('');
   console.log('rendering searchBox');
   const handleClick = () => {
      dispatchFilter({ type: "text", text: inputText });
   };

   const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
      if (event.key === 'Enter') {
         handleClick();
      }
   };

   return (
      <div className='searchBox'>
         <input type='text' id='searchTextBox' value={inputText}
            onKeyDown={handleKeyDown} onChange={e => setInputText(e.target.value)}/>
         <div id='searchIcon' onClick={handleClick} />
      </div>
   );
}