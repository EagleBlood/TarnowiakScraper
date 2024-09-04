import React, { useEffect } from 'react';
import './App.css';
import Tarnowiak from './components/Tarnowiak/tarnowiak';
import Otomoto from './components/Otomoto/otomoto';
import OLX from './components/OLX/olx';
import SearchBar from './components/SearchBar/search';
import Sprzedajemy from './components/Sprzedajemy/sprzedajemy';
import CarBar from './components/CarBar/carBar';
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
        <div className="menu-item-title"><h1>Car Scraper</h1></div>
        <div className="menu-item">menu-option</div>
        <div className="menu-item">menu-option</div>
      </div>
      <div className="app">
        {/* <Tarnowiak />
        <OLX />
        <Otomoto />
        <Sprzedajemy />
        <SearchBar /> */}

        <CarBar
          siteName="Tarnowiak"
          apiUrl="http://localhost:4000/api/carData"
          updateUrl="http://localhost:4000/api/updates"
        />
        <CarBar
          siteName="OLX"
          apiUrl="http://localhost:4000/api/carData"
          updateUrl="http://localhost:4000/api/updates"
        />
        <CarBar
          siteName="Otomoto"
          apiUrl="http://localhost:4000/api/carData"
          updateUrl="http://localhost:4000/api/updates"
        />
        <CarBar
          siteName="Sprzedajemy"
          apiUrl="http://localhost:4000/api/carData"
          updateUrl="http://localhost:4000/api/updates"
        />
        <SearchBar /> 
      </div>
    </div>
  );
}

export default App;