import React, { useState } from 'react';
import useFetch from './useFetch';

const KeywordSearch = (props) => {
  const [userInput, setUserInput] = useState('');
  const [flaskOutput, setFlaskOutput] = useState('');

  const handleInputChange = (e) => {
    setUserInput(e.target.value);
  };


  const handleSendRequest = async () => {
    try {
      const response = await fetch('http://localhost:5000/process_input', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ userInput }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      setFlaskOutput(data.output);
    } catch (error) {
      console.error('Error:', error);
    }
  };


  return (
    <div>
    <div>
      <label>Type something:</label>
      <input type="text" value={userInput} onChange={handleInputChange} />
      <button onClick={handleSendRequest}>Send</button>
    </div>
    <div>
      <h2>Flask Output:</h2>
      <p>{flaskOutput}</p>
    </div>
  </div>
  );
};

export default KeywordSearch;
