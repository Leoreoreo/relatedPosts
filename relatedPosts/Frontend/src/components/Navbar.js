import { Link } from 'react-router-dom';

const Navbar = () => {
    return ( 
        <nav className="navbar">
            <h1>Persona Relations</h1>
            <div className="links">
                <Link to="/KeywordSearch">Keyword Search</Link>            
            </div>
        </nav>
    );
}
 
export default Navbar;