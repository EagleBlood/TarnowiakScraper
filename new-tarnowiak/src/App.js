import React, { useEffect } from 'react';
import './App.css';
import Tarnowiak from './components/Tarnowiak/tarnowiak';
import Otomoto from './components/Otomoto/otomoto';
import OLX from './components/OLX/olx';
import SearchBar from './components/SearchBar/search';

function App() {
  useEffect(() => {
    const handleWheel = (event) => {
      if (event.deltaX !== 0) {
        event.preventDefault();
        event.currentTarget.scrollLeft += event.deltaX;
      }
      if (event.deltaY !== 0) {
        event.preventDefault();
      }
    };

    const sectionBars = document.querySelectorAll('.sectionBar');
    sectionBars.forEach((bar) => {
      bar.addEventListener('wheel', handleWheel);
    });

    return () => {
      sectionBars.forEach((bar) => {
        bar.removeEventListener('wheel', handleWheel);
      });
    };
  }, []);

  return (
    <div className="body">
      <div className="menu">
        <div className="menu-item">Menu</div>
        <div className="menu-item">menu-option</div>
        <div className="menu-item">menu-option</div>
      </div>
      <div className="app">
        <Tarnowiak />
        <OLX />
        <Otomoto />
        <SearchBar />
      </div>
    </div>
  );
}

export default App;