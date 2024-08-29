import React, { useEffect, useState, useRef } from 'react';

function Otomoto() {
  const [carData, setCarData] = useState([]);
  const sectionBarRef = useRef(null); // Define the ref

  useEffect(() => {
    // Fetch initial car data
    fetch('http://localhost:4000/api/carData')
      .then(response => response.json())
      .then(data => {
        const filteredData = data.filter(car => car.siteName === 'Otomoto');
        setCarData(filteredData);
      });


    // Set up EventSource to listen for updates
    const eventSource = new EventSource('http://localhost:4000/api/updates');

    eventSource.onmessage = function(event) {
      const newCar = JSON.parse(event.data);
      if (newCar.siteName === 'Otomoto') {
        setCarData(prevCarData => [...prevCarData, newCar]);
      }
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
      <h2>Otomoto</h2>
      <div className="sectionBar" ref={sectionBarRef}>
        {carData.length === 0 ? (
          <p>No cars available</p> // Display message if no cars are available
        ) : (
          carData.slice().reverse().map(car => (
            <div className="sectionBarItem" key={car.id}>
              <a href={car.carLink} target="_blank" rel="noopener noreferrer">
                <img src={car.carImg} alt={car.carName} className="img" />
              </a>
              <div className="sectionBarItemInfo">
                <p>{car.carName}</p>
                <strong>{car.carDate ? car.carDate : "Brak daty"}</strong>
                <p>Cena: {car.carPrice}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Otomoto;