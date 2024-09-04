// src/components/Header.js
import React from 'react';
import Logo from "../logo.avif";

function Header() {
  return (
    <header className="bg-white shadow-md w-full font-sans">
      <div className="container mx-auto p-4 flex justify-between items-center">
      <div className="flex items-center space-x-2">
          <img src={Logo} alt="Chat GPT Logo" className="object-contain h-20 w-25 mr-20" />
          <h1 className="text-6xl font-bold font-mono tracking-wide uppercase">obo tutor</h1>
        </div>
        <nav>
          <ul className="flex space-x-4">
            <li><a href="/sign-up" className="text-gray-700 hover:text-black">Sign in</a></li>
          </ul>
        </nav>
      </div>
    </header>
  );
}

export default Header;
