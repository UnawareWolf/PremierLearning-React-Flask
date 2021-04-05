import { FC, createContext, useContext, useState } from 'react';

export interface User {
   name: string,
   loggedIn: boolean
}

export const defaultUser: User = {
   name: '',
   loggedIn: false
}

export const UserContext = createContext<User>(defaultUser);

type LoginCallback = (user: User) => void;

interface LoginProps {
   setUser: LoginCallback
}

export const Login: FC<LoginProps> = ({ setUser }) => {
   const user: User = useContext(UserContext);

   return (
      <div>
         {user.loggedIn ? <Me teamName={user.name} /> : <LoginForm setUser={setUser} />}
      </div>
   );
}

interface MeProps {
   teamName: string
}

const Me: FC<MeProps> = ({ teamName }) => {
   return (
      <div>
         <div>
            Logged in as: {teamName}
         </div>
         <button>log out</button>
      </div>
   );
}

const LoginForm: FC<LoginProps> = ({ setUser }) => {
   const [password, setPassword] = useState<string>('');
   const [email, setEmail] = useState<string>('');
   const [loginFail, setLoginFail] = useState<boolean>(false);

   const handleSubmit = (e: any) => {
      e.preventDefault();
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
         console.log(JSON.stringify(data.user))
         setUser(data.user);
         if (!data.user.loggedIn) {
            setLoginFail(true);
         }
         else {
            // set tab to 'team' or something
         }
      });
   }

   return (
      <div>
         {loginFail && 'credentials invalid, try again'}
         <form onSubmit={handleSubmit}>
            <div><input type="text" name="email" placeholder="email" onChange={event => setEmail(event.target.value)} value={email} /></div>
            <div><input type="password" name="password" placeholder="password" onChange={event => setPassword(event.target.value)} value={password} /></div>
            <div><button type="submit">Log in</button></div>
         </form>
      </div>
   );
}
