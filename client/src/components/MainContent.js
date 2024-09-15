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
    setMessages([...messages, { text: message.text, type: 'user', shouldStream: false, mediaType: message.mediaType, fileName: message.fileName }]);
    setIsLoading(true);

    // Prepare form data
    const formData = new FormData();
    formData.append("ChatID", chatId);
    formData.append("UserID", "user123");
    formData.append("input_text", message.text);
    formData.append("mediaType", message.mediaType);
    formData.append("fileName", message.fileName);

    // Check if there is a file and append it
    if (message.file) {
      formData.append("file", message.file);
    }

    try {
      // Send the message and file to the backend
      const response = await axios.post("http://localhost:8000/run-model", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
  
      console.log(response);
      const botMessage = response.data['response'];
      const botContext = response.data['context'];

      setMessages((prevMessages) => [
        ...prevMessages,
        { text: [botMessage, ...botContext], type: 'bot', shouldStream: true, mediaType: 'text', fileName:'text' },
      ]);

    } catch (error) {
      console.error(error);
    }

    setIsLoading(false);
  };

  const loadChat = async (selectedChatId) => {
    try {
      const response = await axios.get(`http://localhost:8000/get-chat?chat_id=${selectedChatId}`);
      const chatHistory = response.data.messages; 
  
      // Iterate through each message in the chat history and add it to the state
      chatHistory.forEach((msg) => {
        if (msg.type === 'human') {
          const mediaType = msg.response_metadata["mediaType"];
          const fileName = msg.response_metadata["fileName"];
          
          setMessages((prevMessages) => [
            ...prevMessages,
            { text: [msg.content], type: 'user', shouldStream: false, mediaType: mediaType, fileName:fileName }, // Wrap the user message in an array
          ]);
        } else if (msg.type === 'ai') {
          // If the bot message contains context, ensure it’s added correctly
          const botMessage = msg.content;
          const botContext = msg.response_metadata["context"];
  
          setMessages((prevMessages) => [
            ...prevMessages,
            { text: [botMessage, ...botContext], type: 'bot', shouldStream: false, mediaType: 'text', fileName:'text' }, // Combine bot message and context
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
    const scrollToBottom = () => {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    };
    setTimeout(scrollToBottom, 100);
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
