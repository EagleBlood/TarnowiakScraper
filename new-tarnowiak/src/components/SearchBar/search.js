import React, { useEffect, useState, useRef } from 'react';

function SearchBar() {
  const [carData, setCarData] = useState([]);
  const [searchQuery, setSearchQuery] = useState(''); // State for search query
  const sectionBarRef = useRef(null);

  useEffect(() => {
    // Fetch initial car data
    fetch('http://localhost:4000/api/carData')
      .then(response => response.json())
      .then(data => {
        console.log('Fetched data:', data);
        setCarData(data);
      })
      .catch(error => console.error('Error fetching data:', error));

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
      const item = sectionBarRef.current.querySelector('.sectionBarItem');
      if (item) {
        const itemWidth = item.clientWidth;
        const scrollAmount = itemWidth + 30;
        const scrollLeft = sectionBarRef.current.scrollLeft;
        sectionBarRef.current.scrollTo({
          left: scrollLeft + scrollAmount * delta,
          behavior: 'smooth'
        });
      }
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

  // Handle search input change
  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  // Filter car data based on search query
  const filteredCarData = carData.filter(car => 
    car.carName.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="sectionBody">
      <h2>Search Bar</h2>
      <input 
        type="text" 
        placeholder="Search for a car" 
        value={searchQuery} 
        onChange={handleSearchChange}  
      />
      <div className="sectionBar" ref={sectionBarRef}>
        {filteredCarData.length === 0 ? (
          <p>No cars available</p>
        ) : (
          filteredCarData.slice().reverse().map(car => (
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

export default SearchBar;