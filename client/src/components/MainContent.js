// src/components/MainContent.js
import React, { useState, useEffect, useRef } from 'react';
import PromptInput from './PromptInput';
import Chat from './Chat';
import axios from 'axios';

function MainContent({ isSidebarOpen }) {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef(null);

  const handleSendMessage = async (message) => {
    setMessages([...messages, { text: message, type: 'user' }]);
    setIsLoading(true);

    // Request to model
    const url = "http://localhost:8000/run-model";
    const postData = { ChatID: "abc1", UserID: "user123", input_text: message };

    try {
      const response = await axios.post(url, postData);
      console.log(response);
      const botMessage = response.data['response'];
      const botContext = response.data['context']; // Assuming this is an array of strings

      setMessages((prevMessages) => [
        ...prevMessages,
        { text: [botMessage, ...botContext], type: 'bot' }, // Pass as an array
      ]);

    } catch (error) {
      console.error(error);
    }

    setIsLoading(false);
  };

  useEffect(() => {
    // Scroll to the bottom when messages change
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className={`flex-grow flex flex-col ${isSidebarOpen ? 'ml-64' : 'ml-20'} transition-all duration-300 font-sans h-[calc(80vh-4rem)]`}>
      {/* Adjust the height according to the combined height of Header and Footer */}
      <div className="flex flex-col flex-grow overflow-hidden">
        <div
          className="flex-grow overflow-y-auto p-4"
          style={{
            scrollbarWidth: 'none', /* For Firefox */
            msOverflowStyle: 'none', /* For Internet Explorer and Edge */
          }}
        >
          <style>  {/* For Chrome, Safari, and Opera */}
            {`
              .hide-scrollbar::-webkit-scrollbar {
                display: none;
              }
            `}
          </style>
          <Chat messages={messages} isLoading={isLoading} />
          <div ref={chatEndRef} /> {/* Scroll to this ref */}
        </div>
        <PromptInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}

export default MainContent;
