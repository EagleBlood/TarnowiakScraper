import React, { useEffect, useState, useRef } from 'react';

function SearchBar() {
  const [carData, setCarData] = useState([]);
  const [searchQuery, setSearchQuery] = useState(''); // State for car name search query
  const [searchQueryCity, setSearchQueryCity] = useState(''); // State for city name search query
  const [searchQueryPrice, setSearchQueryPrice] = useState(''); // State for max price search query
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);
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

  // Handle search input changes
  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  const handleSearchChangeCity = (event) => {
    setSearchQueryCity(event.target.value);
  };

  const handleSearchChangePrice = (event) => {
    setSearchQueryPrice(event.target.value);
  };

  // Filter car data based on search queries
  const filteredCarData = carData.filter(car => {
    const carPrice = parseFloat(car.carPrice.replace(/[^0-9.-]+/g, "")); // Convert price to number
    const maxPrice = parseFloat(searchQueryPrice);
    return (
      car.carName.toLowerCase().includes(searchQuery.toLowerCase()) &&
      (!searchQueryCity || (car.carDate && car.carDate.toLowerCase().includes(searchQueryCity.toLowerCase()))) &&
      (!searchQueryPrice || carPrice <= maxPrice)
    );
  });

  return (
    <div className="sectionBody">
      <h2>Search Bar</h2>
      <input 
        type="text" 
        placeholder="Search for a car" 
        value={searchQuery} 
        onChange={handleSearchChange}  
      />
      <input 
        type="text" 
        placeholder="Search by city name" 
        value={searchQueryCity} 
        onChange={handleSearchChangeCity}  
      />
      <input 
        type="number" 
        placeholder="Search by max price" 
        value={searchQueryPrice} 
        onChange={handleSearchChangePrice}  
      />
      <div className="sectionBar" ref={sectionBarRef}>
        {showLeftArrow && <div className="box" onClick={scrollToStart}><p>&lt;</p></div>}
        {showRightArrow && <div className="boxBack" onClick={scrollToEnd}><p>&gt;</p></div>}
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