import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import MainContent from '../components/MainContent';
import Header from '../components/Header';
import Footer from '../components/Footer';
import axios from 'axios';
import Cookies from 'js-cookie';

function ChatPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [chatId, setChatId] = useState("");
  // const userId = "user123";
  const userId = Cookies.get('userId');

// This function fetches past chats for the user and sets the chatId state to the first chat ID.
// Idea is that when page is reloaded, the user will see the most recent chat by default.
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
  }, [userId]);

  return (
    <div className="flex flex-col h-screen">
      
      <div className="flex flex-grow overflow-hidden">
        <Sidebar className="fixed top-16 left-0 bottom-0 w-64" isOpen={isSidebarOpen} toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} chatId={chatId}  setChatId={setChatId} userId={userId} />
        <div className="flex flex-col flex-grow">
          <Header  navItem={{ label: 'Sign Out', route: '/login' }} isAdmin={true} className="h-16" />
          <div className="flex flex-col flex-grow">
            <MainContent isSidebarOpen={isSidebarOpen} chatId={chatId} />
          </div>
          <Footer />
        </div>
      </div>
    </div>
  );
}

export default ChatPage;