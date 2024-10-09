// src/components/Chat.js
import React from 'react';
import ChatMessage from './ChatMessage';
import LoadingAnimation from './LoadingAnimation';

function Chat({messages,isLoading, userId, chatId}) {  
  return (
    <div className="flex-grow flex flex-col p-4 overflow-y-auto">
      {messages.map((msg, index) => (
        <ChatMessage key={index} text={msg.text} type={msg.type} shouldStream={msg.shouldStream} mediaType={msg.mediaType} fileName={msg.fileName} inputUserQuery={msg.userQuery} userId={userId} chatId={chatId}/>
      ))}
      {isLoading && <LoadingAnimation />}
    </div>
  );
}

export default Chat;
