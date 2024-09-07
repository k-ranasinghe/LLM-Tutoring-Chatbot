import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import MainContent from '../components/MainContent';
import Header from '../components/Header';
import Footer from '../components/Footer';
import axios from 'axios';

function ChatPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [chatId, setChatId] = useState("abc123");
  const userId = "user123";


  const fetchPastChats = async (userId) => {
    try {
      const response = await axios.get(`http://localhost:8000/get-past-chats?userId=${userId}`);
      const pastChats = response.data;
      setChatId(pastChats[0].ChatID);
    } catch (error) {
      console.error('Error fetching past chats:', error);
    }
  };

  useEffect(() => {
    fetchPastChats(userId);
  }, []);

  return (
    <div className="flex flex-col h-screen">
      <Header className="h-16" /> {/* Adjust height to match Header */}
      <div className="flex flex-grow overflow-hidden">
        <Sidebar className="fixed top-16 left-0 bottom-0 w-64" isOpen={isSidebarOpen} toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} chatId={chatId}  setChatId={setChatId} userId={userId} />
        <div className="flex flex-col flex-grow ml-10">
          <MainContent isSidebarOpen={isSidebarOpen} chatId={chatId} />
        </div>
      </div>
      <Footer className="h-16" /> {/* Adjust height to match Footer */}
    </div>
  );
}

export default ChatPage;