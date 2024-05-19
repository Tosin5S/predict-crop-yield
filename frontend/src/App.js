import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header>
        <h1>Yield Predictor</h1>
      </header>
      <main>
        <section className="hero">
          <h2>Predict your crop yield with ease</h2>
          <p>Use our machine learning model to maximize your harvest</p>
          <button>Start Predicting</button>
        </section>
        <section className="features">
              <h3>Accurate Predictions</h3>
              <p>Our model uses historical data and machine learning algorithms to provide precise yield predictions</p>
        
              <h3>Easy Data Input</h3>
              <p>Simply enter your crop data, and we will take care of the rest</p>
              
              <h3>Actionable Insights</h3>
              <p>Get valuable insights to increase your crop yield</p>
        </section>
      </main>
      <footer>
        <p>Copyright © 2024 Yield Predictor</p>
      </footer>
    </div>
  );
}

export default App;