// src/components/Chat.js
import React from 'react';
import ChatMessage from './ChatMessage';
import LoadingAnimation from './LoadingAnimation';

function Chat({messages,isLoading}) {  
  return (
    <div className="flex-grow flex flex-col p-4 overflow-y-auto">
      {messages.map((msg, index) => (
        <ChatMessage key={index} text={msg.text} type={msg.type} />
      ))}
      {isLoading && <LoadingAnimation />}
    </div>
  );
}

export default Chat;
