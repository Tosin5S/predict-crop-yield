import React, { useState } from 'react';

function PredictPage() {
  const [cropData, setCropData] = useState('');
  const [yieldPrediction, setYieldPrediction] = useState(null);

  const handlePredictYield = (event) => {
    event.preventDefault();
    fetch('https://yield-d77y.onrender.com/predict/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ [cropData]: 3 }),
    })
      .then((response) => response.json())
      .then((data) => setYieldPrediction(data['fresh root yield|CO_334:0000013']));
  };

  return (
    <div>
      <section>
        <h2>Yield Prediction Input</h2>
        <form onSubmit={handlePredictYield}>
          <label>
            Crop Data:
            <input
              type="text"
              name="cropData"
              value={cropData}
              onChange={(event) => setCropData(event.target.value)}
            />
          </label>
          <button>Predict Yield</button>
        </form>
        {yieldPrediction && (
          <p>Predicted Yield: {yieldPrediction}</p>
        )}
      </section>
      <section>
        <h2>Yield Prediction Visualization</h2>
      </section>
      <section>
        <h2>Chatbot</h2>
      </section>
    </div>
  );
}

export default PredictPage;
