// src/components/MainContent.js
import React, { useState } from 'react';
import PromptInput from './PromptInput';
import Chat from './Chat';
import axios from 'axios';

function MainContent({ isSidebarOpen }) {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (message) => {
    setMessages([...messages, { text: message, type: 'user' }]);
    setIsLoading(true);

    // Request to model
    const url = "http://localhost:8000/run-model";
    const postData = { session_id: "abc1", user_id: "user123", input_text: message };

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

  return (
    <div className={`flex-grow flex flex-col ${isSidebarOpen ? 'ml-64' : 'ml-20'} transition-all duration-300 font-sans`}>
      <Chat messages={messages} isLoading={isLoading} />
      <PromptInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
}

export default MainContent;
