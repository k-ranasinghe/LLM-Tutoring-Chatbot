// src/components/PromptInput.js
import React, { useState } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/outline';

function PromptInput({ onSendMessage, isLoading }) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  // Enter Key should send the message
  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="bg-white p-4 shadow-md flex items-center border-t border-gray-300 font-sans">
      <input 
        type="text" 
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type your prompt..." 
        className="flex-grow p-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        disabled={isLoading}
      />
      <button 
        onClick={handleSend}
        className={`text-white p-2 rounded-r-lg hover:bg-blue-600 ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
        style={{backgroundColor:"#042f47"}}
        disabled={isLoading}
      >
        <PaperAirplaneIcon className="h-6 w-6 transform -rotate-45" />
      </button>
    </div>
  );
}

export default PromptInput;
