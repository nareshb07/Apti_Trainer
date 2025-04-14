import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';


import { BrowserRouter } from 'react-router-dom';
import { TrainerProvider } from './context/TrainerContext';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <TrainerProvider>
        <App />
      </TrainerProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
