import React, { useState } from 'react';


const KeywordSearch = (props) => {
  const [userInput, setUserInput] = useState('');
  const [selectedNumber, setSelectedNumber] = useState(1); // Default value
  const [flaskOutput, setFlaskOutput] = useState('');

  const handleInputChange = (e) => {
    setUserInput(e.target.value);
  };

  const handleNumberChange = (e) => {
    setSelectedNumber(parseInt(e.target.value, 10));
  };

  const handleSendRequest = async () => {
    try {
      const response = await fetch(props.url + '/KeywordSearch/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userInput,
          selectedNumber,
        }),
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
        <label>PID:</label>
        <select value={selectedNumber} onChange={handleNumberChange}>
          <option value={1}>1</option>
          <option value={2}>2</option>
          <option value={3}>3</option>
        </select>
      </div>
      <div>
        <label>Keyword:</label>
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
