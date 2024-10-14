// src/components/Header.js
import React from 'react';

function Header({ navItem, isAdmin }) {
  return (
    <header style={{ backgroundColor: "#2f2f2f11" }} className="shadow-xl pb-0.5 w-full font-sans">
      <div style={{ backgroundColor: "#2f2f2f" }} className="container mx-auto flex justify-between items-center">
        <div className="flex-grow flex justify-center">
          <h1 style={{ fontFamily: "Shadows Into Light" }} className="text-6xl font-bold tracking-wide uppercase text-transparent bg-clip-text bg-gradient-to-r from-blue-700 via-sky-500 to-purple-500 shadow-lg hover:shadow-2xl transition-shadow duration-300">
            obo tutor
          </h1>
        </div>
        <nav>
          <ul className="flex space-x-6 mr-10">
            {/* Conditionally render the "Admin" link if the user is an admin */}
            {isAdmin && (
              <li className="text-lg bg-customtxt font-medium transition duration-300 transform hover:scale-105 p-2 rounded-2xl">
                <a href="/upload" className="text-custombg font-bold hover:text-gray-700">
                  Admin Panel
                </a>
              </li>
            )}
            {/* Display the navItem link if it exists */}
            {navItem && (
              <li className="text-lg bg-customtxt font-medium transition duration-300 transform hover:scale-105 p-2 rounded-2xl">
                <a href={navItem.route} className="text-custombg font-bold hover:text-gray-700">
                  {navItem.label}
                </a>
              </li>
            )}
          </ul>
        </nav>
      </div>
    </header>
  );
}

export default Header;
