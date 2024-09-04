import React, { useEffect, useState, useRef } from 'react';

function CarBar({ siteName, apiUrl, updateUrl }) {
  const [carData, setCarData] = useState([]);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);
  const sectionBarRef = useRef(null);

  useEffect(() => {
    // Fetch initial car data
    fetch(apiUrl)
      .then(response => response.json())
      .then(data => {
        const filteredData = data.filter(car => car.siteName === siteName);
        setCarData(filteredData);
      })
      .catch(error => console.error('Error fetching data:', error));

    // Set up EventSource to listen for updates
    const eventSource = new EventSource(updateUrl);

    eventSource.onmessage = function(event) {
      const newCar = JSON.parse(event.data);
      if (newCar.siteName === siteName) {
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
  }, [apiUrl, updateUrl, siteName]);

  // Scroll functionality
  const handleScroll = (event) => {
    if (sectionBarRef.current) {
      const delta = Math.sign(event.deltaY);
      const itemWidth = sectionBarRef.current.querySelector('.sectionBarItem').clientWidth;
      const scrollAmount = itemWidth + 30;
      const scrollLeft = sectionBarRef.current.scrollLeft;
      sectionBarRef.current.scrollTo({
        left: scrollLeft + scrollAmount * delta,
        behavior: 'smooth'
      });
    }
  };

  const scrollToStart = () => {
    if (sectionBarRef.current) {
      sectionBarRef.current.scrollTo({
        left: 0,
        behavior: 'smooth'
      });
    }
  };

  const scrollToEnd = () => {
    if (sectionBarRef.current) {
      sectionBarRef.current.scrollTo({
        left: sectionBarRef.current.scrollWidth,
        behavior: 'smooth'
      });
    }
  };

  const updateArrowVisibility = () => {
    if (sectionBarRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = sectionBarRef.current;
      setShowLeftArrow(scrollLeft > 0);
      setShowRightArrow(scrollLeft + clientWidth < scrollWidth);
    }
  };

  useEffect(() => {
    const sectionBar = sectionBarRef.current;
    if (sectionBar) {
      sectionBar.addEventListener('wheel', handleScroll);
      sectionBar.addEventListener('scroll', updateArrowVisibility);
      updateArrowVisibility();
    }
    return () => {
      if (sectionBar) {
        sectionBar.removeEventListener('wheel', handleScroll);
        sectionBar.removeEventListener('scroll', updateArrowVisibility);
      }
    };
  }, [carData]);

  return (
    <div className="sectionBody">
      <h2>{siteName}</h2>
      <div className="sectionBar" ref={sectionBarRef}>
        {showLeftArrow && <div className="box" onClick={scrollToStart}><p>&lt;</p></div>}
        {showRightArrow && <div className="boxBack" onClick={scrollToEnd}><p>&gt;</p></div>}
        {carData.length === 0 ? (
          <p>No cars available</p>
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
    </div>
  );
}

export default CarBar;