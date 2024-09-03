import express from "express";
import cors from "cors";
import CarData from "./data/carData.js";
import Car from "./data/car.js";

const app = express(); 
const port = 4000;

const carData = new CarData();
let clients = [];

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.send('Welcome to my server!');
});

app.get('/api/data', (req, res) => {
  const data = {
    message: 'Hello from the server!', 
    items: [1, 2, 3, 4, 5]
  };
  res.json(data);
});

app.post('/api/carData', (req, res) => {
  const { url, site_name, car_name, price, date_added, link, imgLink } = req.body;
  const newCar = new Car(
    carData.cars.length + 1,
    site_name,
    car_name,
    price,
    date_added,
    link,
    imgLink
  );
  carData.addCar(newCar);  
  res.status(201).send('Car added');
  sendSSEUpdate(newCar);
  console.log('Received data:', newCar);  
}); 

app.get('/api/updates', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  clients.push(res);
 
  req.on('close', () => {
    clients = clients.filter(client => client !== res);
  });
}); 

app.get('/api/carData', (req, res) => {
  res.json(carData.getAllCars());
});

app.delete('/api/carData/delete/all', (req, res) => {
  carData.cars = [];
  res.sendStatus(200);
});

app.delete('/api/carData/delete/:id', (req, res) => {
  const id = parseInt(req.params.id);
  carData.deleteCar(id);
  res.sendStatus(200);
});

function sendSSEUpdate(newCar) {
  clients.forEach(client => client.write(`data: ${JSON.stringify(newCar)}\n\n`));
}

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});