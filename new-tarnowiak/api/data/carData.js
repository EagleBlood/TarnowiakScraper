import Car from './car.js';

class CarData {
    constructor() {
        this.cars = [];
    }
    
    addCar(car) {
        this.cars.push(car);
    }
    
    getCar(id) {
        return this.cars.find(car => car.id === id);
    }
    
    getAllCars() {
        return this.cars;
    }
    
    updateCar(id, car) {
        const index = this.cars.findIndex(c => c.id === id);
        if (index !== -1) {
            this.cars[index] = car;
        }
    }
    
    deleteCar(id) {
        this.cars = this.cars.filter(car => car.id !== id);
    }
}

export default CarData;