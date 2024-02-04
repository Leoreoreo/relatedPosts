import KeywordSearch from './components/KeywordSearch';
import Navbar from './components/Navbar';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';

function App() {
    const url = 'http://127.0.0.1:5000';    // backend URL
  return (
    <Router>
      <div className="App">
        <Navbar />
        <div className="content">
          <Switch>
            <Route exact path="/KeywordSearch">
               <KeywordSearch url = {url}/>
            </Route>
          </Switch>
        </div>
      </div>
    </Router>
  );
}

export default App;