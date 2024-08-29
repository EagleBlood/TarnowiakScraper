import React from 'react';
import './App.css';
import Tarnowiak from './components/Tarnowiak/Tarnowiak';

function App() {
  return (
    <div className="body">
      <div className="menu">
        <div className="menu-item">Menu</div>
        <div className="menu-item">menu-option</div>
        <div className="menu-item">menu-option</div>
      </div>
      <div className="app">
        <Tarnowiak />
      </div>
    </div>
  );
}

export default App;