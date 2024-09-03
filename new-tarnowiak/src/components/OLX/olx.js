import React, { useEffect, useState, useRef } from 'react';

function OLX() {
  const [carData, setCarData] = useState([]);
  const sectionBarRef = useRef(null); // Ref for OLX section
  const preludaSectionBarRef = useRef(null); // Ref for OLX Preluda section

  useEffect(() => {
    // Fetch initial car data
    fetch('http://localhost:4000/api/carData')
      .then(response => response.json())
      .then(data => {
        console.log('Fetched data:', data); // Debugging: log fetched data
        const filteredData = data.filter(car => car.siteName === 'OLX');
        console.log('Filtered data:', filteredData); // Debugging: log filtered data
        setCarData(filteredData);
      })
      .catch(error => console.error('Error fetching data:', error)); // Debugging: log fetch error

    // Set up EventSource to listen for updates
    const eventSource = new EventSource('http://localhost:4000/api/updates');

    eventSource.onmessage = function(event) {
      const newCar = JSON.parse(event.data);
      if (newCar.siteName === 'OLX') {
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
  const handleScroll = (event, ref) => {
    if (ref.current) {
      const delta = Math.sign(event.deltaY);
      const sectionBarItem = ref.current.querySelector('.sectionBarItem');
      if (sectionBarItem) {
        const itemWidth = sectionBarItem.clientWidth; // 30 is the gap between items
        const scrollAmount = itemWidth + 30;
        const scrollLeft = ref.current.scrollLeft;
        ref.current.scrollTo({
          left: scrollLeft + scrollAmount * delta,
          behavior: 'smooth'
        });
      }
    }
  };

  const scrollToStart = (ref) => {
    if (ref.current) {
      ref.current.scrollTo({
        left: 0,
        behavior: 'smooth'
      });
    }
  };

  const scrollToEnd = (ref) => {
    if (ref.current) {
      ref.current.scrollTo({
        left: ref.current.scrollWidth,
        behavior: 'smooth'
      });
    }
  };

  useEffect(() => {
    const sectionBar = sectionBarRef.current;
    const preludaSectionBar = preludaSectionBarRef.current;
    if (sectionBar) {
      sectionBar.addEventListener('wheel', (event) => handleScroll(event, sectionBarRef));
    }
    if (preludaSectionBar) {
      preludaSectionBar.addEventListener('wheel', (event) => handleScroll(event, preludaSectionBarRef));
    }
    return () => {
      if (sectionBar) {
        sectionBar.removeEventListener('wheel', (event) => handleScroll(event, sectionBarRef));
      }
      if (preludaSectionBar) {
        preludaSectionBar.removeEventListener('wheel', (event) => handleScroll(event, preludaSectionBarRef));
      }
    };
  }, []);

  return (
    <div className="sectionBody">
      <h2>OLX</h2>
      <div className="sectionBar" ref={sectionBarRef}>
        <div className="box" onClick={() => scrollToStart(sectionBarRef)}><p>&lt;</p></div>
        <div className="boxBack" onClick={() => scrollToEnd(sectionBarRef)}><p>&gt;</p></div>
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
                <strong>{car.carDate}</strong>
                <p>Cena: {car.carPrice}</p>
              </div>
            </div>
          ))
        )}
      </div>

      <h2>OLX Preluda</h2>
      <div className="sectionBar" ref={preludaSectionBarRef}>
        <div className="box" onClick={() => scrollToStart(preludaSectionBarRef)}><p>&lt;</p></div>
        <div className="boxBack" onClick={() => scrollToEnd(preludaSectionBarRef)}><p>&gt;</p></div>
        {carData.length === 0 ? (
          <p>No cars available</p> // Display message if no cars are available
        ) : (
          carData
            .filter(car => car.url.includes('q-honda-prelude'))
            .slice().reverse().map(car => (
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

export default OLX;