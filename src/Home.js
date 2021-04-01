import React, { useState, } from 'react';
import App from './App';

function Page() {
  const [tabSelected, setTab] = useState('home');

  if (tabSelected === 'login') {
    return (<App />);
  }

  return (
  <div>
    <button onClick={setTab('home')}>home</button><button onClick={setTab('login')}>login</button>
  </div>
  );
}

export default Page;