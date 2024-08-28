import express from "express";
import cors from "cors";

const app = express();
const port = 4000;

app.use(cors());

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

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});