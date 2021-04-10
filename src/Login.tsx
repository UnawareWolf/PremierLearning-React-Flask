import { FC, useContext, useState } from 'react';
import { User, UserContext, defaultUserTeam, SetUserTeamCallback } from './App';

type SetUserCallback = (user: User) => void;

export type SetTabCallback = (tab: string) => void;

interface LoginProps {
   setUser: SetUserCallback,
   setUserTeam: SetUserTeamCallback,
   setTab: SetTabCallback
}

export const Login: FC<LoginProps> = ({ setUser, setUserTeam, setTab }) => {
   const user: User = useContext(UserContext);

   return (
      <div>
         {user.loggedIn ? <Me teamName={user.name} setUser={setUser} setUserTeam={setUserTeam} /> :
            <LoginForm setUser={setUser} setUserTeam={setUserTeam} setTab={setTab} />}
      </div>
   );
}

interface MeProps {
   teamName: string,
   setUser: SetUserCallback,
   setUserTeam: SetUserTeamCallback
}

const Me: FC<MeProps> = ({ teamName, setUser, setUserTeam }) => {
   const handleLogout = (e: any) => {
      e.preventDefault();
      fetch('/api/logout', { method: 'GET' });
      setUser({
         name: '',
         loggedIn: false
      });
      setUserTeam(defaultUserTeam);
   }

   return (
      <div>
         <div>
            Your name is {teamName}
         </div>
         <button className='general' onClick={handleLogout}>log out</button>
      </div>
   );
}

interface LoginState {
   fail: boolean,
   loggingIn: boolean
}

const LoginForm: FC<LoginProps> = ({ setUser, setUserTeam, setTab }) => {
   const [password, setPassword] = useState<string>('');
   const [email, setEmail] = useState<string>('');
   const [loginState, setLoginState] = useState<LoginState>({
      fail: false,
      loggingIn: false
   });

   const handleSubmit = (e: any) => {
      e.preventDefault();
      setLoginState({
         fail: false,
         loggingIn: true
      })
      fetch('/api/login', {
         method: 'POST',
         headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
         },
         body: JSON.stringify({
            'username': email,
            'password': password
         })
      }).then(res => res.json()).then(data => {
         console.log(JSON.stringify(data.user));
         setLoginState({
            ...loginState,
            loggingIn: false
         });
         setUser({
            name: data.user.name,
            loggedIn: data.user.loggedIn
            
         });
         if (!data.user.loggedIn) {
            setLoginState({
               ...loginState,
               fail: true
            });
            setPassword('');
         }
         else {
            setUserTeam({
               teamIDs: data.user.teamIDs,
               suggestedTeams: null,
               transfers: null,
               loading: false
            });
            setTab('team');
         }
      });
   }

   return (
      <div>
         {loginState.fail && 'credentials invalid, try again'}
         {loginState.loggingIn ? 'logging in' : 
            <form onSubmit={handleSubmit}>
               <div><input type="text" name="email" placeholder="email" onChange={event => setEmail(event.target.value)} value={email} /></div>
               <div><input type="password" name="password" placeholder="password" onChange={event => setPassword(event.target.value)} value={password} /></div>
               <div><button className='general' type="submit">Log in</button></div>
            </form>}
      </div>
   );
}
