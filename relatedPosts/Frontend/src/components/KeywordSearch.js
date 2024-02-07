import React, { useState } from 'react';
import axios from 'axios';

const KeywordSearch = (props) => {
  const [userInput, setUserInput] = useState('');
  const [selectedNumber, setSelectedNumber] = useState(1);
  const [flaskOutput, setFlaskOutput] = useState([]);
  const [similarSearches, setSimilarSearches] = useState([]);

  const handleInputChange = (e) => {
    setUserInput(e.target.value);
  };

  const handleNumberChange = (e) => {
    setSelectedNumber(parseInt(e.target.value, 10));
  };

  const handleSendRequest = async () => {
    try {
      // Clear existing search results
      setFlaskOutput([]);
      const response = await axios.post(props.url + '/KeywordSearch/', {
        userInput,
        selectedNumber,
      });

      const data = response.data;
      if (data.similarSearches && data.similarSearches.length > 0) {
        setSimilarSearches(data.similarSearches);
      } else {
        setFlaskOutput(data.output);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleViewExistingSearch = async (pid, keyword) => {
    try {
      const response = await axios.post(props.url + '/ViewExistingSearch/', {
        userInput: keyword,
        selectedNumber: pid,
      });

      const data = response.data;
      setFlaskOutput(data.output);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleNewSearch = async () => {
    try {
      // Clear existing search results
      setFlaskOutput([]);
      const response = await axios.post(props.url + '/RelevantSearch/', {
        userInput,
        selectedNumber,
      });

      const data = response.data;
      if (data.output) {
        setFlaskOutput(data.output);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div>
      <div className="search-container">
        <div className="input-group">
          <label>PID:</label>
          <select value={selectedNumber} onChange={handleNumberChange}>
            <option value={1}>1</option>
            <option value={2}>2</option>
            <option value={3}>3</option>
          </select>
          <input 
            type="text" 
            placeholder="Keyword" 
            value={userInput} 
            onChange={handleInputChange} 
          />
          <button onClick={handleSendRequest}>Search</button>
        </div>
      </div>
      {similarSearches.length > 0 && (
      <div>
        <h2>Similar Searches Found:</h2>
        <ul className="similar-searches">
          {similarSearches.map((search, index) => (
            <li key={index}>
              <button onClick={() => handleViewExistingSearch(search[0], search[1])}>View</button>
              {`${search[1]}`}{' '}
            </li>
          ))}
        </ul>
        <br></br>
        <h2> OR... <button onClick={handleNewSearch}>Search Anyway</button></h2>
      </div>
      )}
      <div>
        <br></br>
        <h2>Search Results:</h2>
        <div className="text-container">
          {flaskOutput && flaskOutput.map(([dataType, id, content]) => (
            <div key={`${dataType}-${id}`} className="text-item">
              <strong>{dataType} {id}:</strong> {content}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default KeywordSearch;
