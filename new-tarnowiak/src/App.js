import React, { useRef, useEffect, useState } from 'react';
import './App.css';

function App() {
  const sectionBarRef = useRef(null);

  const handleScroll = (event) => {
    if (sectionBarRef.current) {
      const delta = Math.sign(event.deltaY);
      const itemWidth = sectionBarRef.current.querySelector('.sectionBarItem').clientWidth; // 30 is the gap between items
      const scrollAmount = itemWidth + 30;
      const scrollLeft = sectionBarRef.current.scrollLeft;
      sectionBarRef.current.scrollTo({
        left: scrollLeft + scrollAmount * delta,
        behavior: 'smooth'
      });
    }
  };

  useEffect(() => {
    const sectionBar = sectionBarRef.current;
    if (sectionBar) {
      sectionBar.addEventListener('wheel', handleScroll);
    }
    return () => {
      if (sectionBar) {
        sectionBar.removeEventListener('wheel', handleScroll);
      }
    };
  }, []);

  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('http://localhost:4000/api/data')
      .then(response => response.json())
      .then(data => setData(data))
      .catch(error => console.error('Error fetching data:', error));
  }, []);


  return (
    <div className="body">
      <div className="menu">
        <div className="menu-item">Menu</div>
        <div className="menu-item">menu-option</div>
        <div className="menu-item">menu-option</div>
      </div>
      
      <div className="app">
        
        
        <div className="sectionBody">
          <strong>Section1</strong>
          <div className="sectionBar" ref={sectionBarRef}>
            {Array.from({ length: 10 }).map((_, index) => (
              <div className="sectionBarItem" key={index}>
                <p className="img">img</p>
                <div className="sectionBarItemInfo">
                  <p>name</p>
                  <p>date</p>
                  <p>price</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="sectionBody">
          <strong>Section2</strong>
          <div className="sectionBar">
            {data ? (
              <div>
                <p>{data.message}</p>
                <ul>
                  {data.items.map(item => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              ) : (
                <p>Loading...</p>
              )}
          </div>
        </div>
      </div>


    </div>
  );
}

export default App;