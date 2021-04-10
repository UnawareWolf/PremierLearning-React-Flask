import { FC, useContext } from 'react';
import { UserContext } from './App';
import './UserIcon.scss';
import {SetTabCallback} from './Login';

interface UserIconProps {
   setTab: SetTabCallback
}

export const UserIcon: FC<UserIconProps> = ({ setTab }) => {
   const user = useContext(UserContext)
   const handleClick = () => {
      setTab('login');
   }

   return (
      <div id='userStamp' onClick={handleClick}>{user.name}</div>
   );
}