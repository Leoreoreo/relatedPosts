import './Navbar.css';
import { Link } from 'react-router-dom';
import React, { useState, useEffect } from 'react';

const Navbar = () => {
    const [activeLink, setActiveLink] = useState('/KeywordSearch');

    // Set the active link when the component mounts
    useEffect(() => {
        setActiveLink('/KeywordSearch');
    }, []);

    return ( 
        <nav className="navbar">
            <div className="links">
                <Link to="/KeywordSearch" className={activeLink === '/KeywordSearch' ? 'active' : ''} onClick={() => setActiveLink('/KeywordSearch')}>Keyword Search</Link>     
                <Link to="/RelationGraph" className={activeLink === '/RelationGraph' ? 'active' : ''} onClick={() => setActiveLink('/RelationGraph')}>Relation Graph</Link>         
            </div>
        </nav>
    );
}
 
export default Navbar;
