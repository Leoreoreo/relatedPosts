import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Sankey from './Sankey.tsx';

const RelationGraph = (props) => {
  const [selectedNumber, setSelectedNumber] = useState(1);
  const [flaskOutput, setFlaskOutput] = useState([]);

  const handleNumberChange = (e) => {
    setSelectedNumber(parseInt(e.target.value, 10));
  };

  const handleSendRequest = async () => {
    try {
      setFlaskOutput([]);
      const response = await axios.post(props.url + '/RelationGraph/', {
        selectedNumber,
      });

      const data = response.data;
      setFlaskOutput(data.output);
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
          <button onClick={handleSendRequest}>Generate Relation Graph</button>
        </div>
      </div>
      <div className="content">
        { flaskOutput && flaskOutput.links && (
          <Sankey width={600} height={600} data={flaskOutput} personID={selectedNumber} url={props.url}/>
        )}
      </div>
    </div>
  );
};

export default RelationGraph;
