import React from 'react';
import ReactDOM from 'react-dom/client';
import { Router, Route, Switch } from 'react-router-dom';
import './index.css';
import App from './App';
import PredictPage from './components/PredictPage'; 
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Router>
       <Switch>
            <Route path="/" element={<App />} />
            <Route path="/predict" element={<PredictPage />} />
       </Switch>
    </Router>
  </React.StrictMode>
);

reportWebVitals();
