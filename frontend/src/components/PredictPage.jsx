import React from 'react';

function PredictPage() {
  return (
    <div>
      <section>
        <h2>Yield Prediction Input</h2>
        <form>
          <label>
            Crop Data:
            <input type="text" name="cropData" />
          </label>
          <button>Predict Yield</button>
        </form>
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