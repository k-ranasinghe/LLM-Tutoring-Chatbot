// src/components/MainContent.js
import React, { useState, useEffect, useRef } from 'react';
import PromptInput from './PromptInput';
import Chat from './Chat';
import axios from 'axios';

function MainContent({ isSidebarOpen, chatId }) {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef(null);

  const handleSendMessage = async (message) => {
    setMessages([...messages, { text: message, type: 'user' }]);
    setIsLoading(true);

    // Request to model
    const url = "http://localhost:8000/run-model";
    const postData = { ChatID: chatId, UserID: "user123", input_text: message };

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

  const loadChat = async (selectedChatId) => {
    try {
      const response = await axios.get(`http://localhost:8000/get-chat?chat_id=${selectedChatId}`);
      const chatHistory = response.data.messages; // Assuming the chat messages are returned
  
      // Iterate through each message in the chat history and add it to the state
      chatHistory.forEach((msg) => {
        if (msg.type === 'human') {
          setMessages((prevMessages) => [
            ...prevMessages,
            { text: [msg.content], type: 'user' }, // Wrap the user message in an array
          ]);
        } else if (msg.type === 'ai') {
          // If the bot message contains context, ensure it’s added correctly
          const botMessage = msg.content;
          const botContext = msg.response_metadata["context"];
  
          setMessages((prevMessages) => [
            ...prevMessages,
            { text: [botMessage, ...botContext], type: 'bot' }, // Combine bot message and context
          ]);
        }
      });
  
    } catch (error) {
      console.error('Error loading chat:', error);
    }
  };

  // UseEffect to load chat messages when chatId changes
  useEffect(() => {
    if (chatId) {
      setMessages([]);
      loadChat(chatId);
    }
  }, [chatId]);

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
