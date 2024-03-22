import KeywordSearch from './components/KeywordSearch';
import Navbar from './components/Navbar';
import RelationGraph from './components/RelationGraph';
import { HashRouter as Router, Route, Switch } from 'react-router-dom';

function App() {
  const url = 'http://127.0.0.1:5000';    // backend URL
  return (
    <Router>
      <div className="App">
        <Navbar />
        <Switch>
          <Route exact path="/KeywordSearch">
              <KeywordSearch url={url}/>
          </Route>
          <Route exact path="/RelationGraph">
              <RelationGraph url={url}/>
          </Route> 
        </Switch>
      </div>
    </Router>
  );
}

export default App;
