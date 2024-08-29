import React, { useEffect, useState, useRef } from 'react';

function Tarnowiak() {
  const [carData, setCarData] = useState([]);
  const sectionBarRef = useRef(null); // Define the ref

  useEffect(() => {
    // Fetch initial car data
    fetch('http://localhost:4000/api/carData')
      .then(response => response.json())
      .then(data => setCarData(data));

    // Set up EventSource to listen for updates
    const eventSource = new EventSource('http://localhost:4000/api/updates');

    eventSource.onmessage = function(event) {
      const newCar = JSON.parse(event.data);
      setCarData(prevCarData => [...prevCarData, newCar]);
    };

    eventSource.onerror = function(err) {
      console.error('EventSource failed:', err);
      eventSource.close();
    };

    // Clean up EventSource on component unmount
    return () => {
      eventSource.close();
    };
  }, []);

  // Scroll functionality
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

  return (
    <div className="sectionBody">
      <h2>Tarnowiak</h2>
      <div className="sectionBar" ref={sectionBarRef}>
        {carData.slice().reverse().map(car => (
          <div className="sectionBarItem" key={car.id}>
            <a href={car.carLink} target="_blank" rel="noopener noreferrer">
              <img src={car.carImg} alt={car.carName} className="img" />
            </a>
            <div className="sectionBarItemInfo">
              <p>{car.carName}</p>
              <strong>{car.carDate}</strong>
              <p>Cena: {car.carPrice}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Tarnowiak;