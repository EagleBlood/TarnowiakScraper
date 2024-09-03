import React, { useEffect, useState, useRef } from 'react';

function Otomoto() {
  const [carData, setCarData] = useState([]);
  const sectionBarRef1 = useRef(null); // Define the ref for the first sectionBar
  const sectionBarRef2 = useRef(null); // Define the ref for the second sectionBar

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

  // Scroll functionality for the first sectionBar
  const handleScroll1 = (event) => {
    if (sectionBarRef1.current) {
      const delta = Math.sign(event.deltaY);
      const sectionBarItem = sectionBarRef1.current.querySelector('.sectionBarItem');
      if (sectionBarItem) {
        const itemWidth = sectionBarItem.clientWidth; // 30 is the gap between items
        const scrollAmount = itemWidth + 30;
        const scrollLeft = sectionBarRef1.current.scrollLeft;
        sectionBarRef1.current.scrollTo({
          left: scrollLeft + scrollAmount * delta,
          behavior: 'smooth'
        });
      }
    }
  };

  const scrollToStart1 = () => {
    if (sectionBarRef1.current) {
      sectionBarRef1.current.scrollTo({
        left: 0,
        behavior: 'smooth'
      });
    }
  };

  const scrollToEnd1 = () => {
    if (sectionBarRef1.current) {
      sectionBarRef1.current.scrollTo({
        left: sectionBarRef1.current.scrollWidth,
        behavior: 'smooth'
      });
    }
  };

  useEffect(() => {
    const sectionBar = sectionBarRef1.current;
    if (sectionBar) {
      sectionBar.addEventListener('wheel', handleScroll1);
    }
    return () => {
      if (sectionBar) {
        sectionBar.removeEventListener('wheel', handleScroll1);
      }
    };
  }, []);

  // Scroll functionality for the second sectionBar
  const handleScroll2 = (event) => {
    if (sectionBarRef2.current) {
      const delta = Math.sign(event.deltaY);
      const sectionBarItem = sectionBarRef2.current.querySelector('.sectionBarItem');
      if (sectionBarItem) {
        const itemWidth = sectionBarItem.clientWidth; // 30 is the gap between items
        const scrollAmount = itemWidth + 30;
        const scrollLeft = sectionBarRef2.current.scrollLeft;
        sectionBarRef2.current.scrollTo({
          left: scrollLeft + scrollAmount * delta,
          behavior: 'smooth'
        });
      }
    }
  };

  const scrollToStart2 = () => {
    if (sectionBarRef2.current) {
      sectionBarRef2.current.scrollTo({
        left: 0,
        behavior: 'smooth'
      });
    }
  };

  const scrollToEnd2 = () => {
    if (sectionBarRef2.current) {
      sectionBarRef2.current.scrollTo({
        left: sectionBarRef2.current.scrollWidth,
        behavior: 'smooth'
      });
    }
  };

  useEffect(() => {
    const sectionBar = sectionBarRef2.current;
    if (sectionBar) {
      sectionBar.addEventListener('wheel', handleScroll2);
    }
    return () => {
      if (sectionBar) {
        sectionBar.removeEventListener('wheel', handleScroll2);
      }
    };
  }, []);

  return (
    <div className="sectionBody">
      <h2>Otomoto</h2>
      <div className="sectionBar" ref={sectionBarRef1}>
        <div className="box" onClick={scrollToStart1}><p>&lt;</p></div>
        <div className="boxBack" onClick={scrollToEnd1}><p>&gt;</p></div>
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

      <h2>Otomoto Preluda</h2>
      <div className="sectionBar" ref={sectionBarRef2}>
        <div className="box" onClick={scrollToStart2}><p>&lt;</p></div>
        <div className="boxBack" onClick={scrollToEnd2}><p>&gt;</p></div>
        {carData.length === 0 ? (
          <p>No cars available</p> // Display message if no cars are available
        ) : (
          carData
            .filter(car => car.url.includes('honda/prelude'))
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

export default Otomoto;