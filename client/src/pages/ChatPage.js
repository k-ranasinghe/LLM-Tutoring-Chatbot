import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import MainContent from '../components/MainContent';
import Header from '../components/Header';
import Footer from '../components/Footer';
import Disclaimer from '../components/Disclaimer';
import axios from 'axios';
import Cookies from 'js-cookie';

function ChatPage() {
  const location = useLocation();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [chatId, setChatId] = useState("");
  const [showDisclaimer, setShowDisclaimer] = useState(false);
  const userId = Cookies.get('userId');
  const isAdmin = Cookies.get('isAdmin') === '1';

  useEffect(() => {
    if (!userId) {
      window.location.href = '/login';
    } else {
      fetchPastChats(userId);

      const shouldShowDisclaimer = location.state && location.state.fromLogin && Cookies.get('showDisclaimer') === 'true';
      if (shouldShowDisclaimer) {
        // Set a timeout to delay showing the disclaimer
        const timeoutId = setTimeout(() => {
          setShowDisclaimer(true);
          Cookies.set('showDisclaimer', 'false'); // Update the cookie so it won't show again
        }, 500); // Adjust the delay as needed (300ms here)

        // Clear timeout on unmount
        return () => clearTimeout(timeoutId);
      }
    }
  }, [userId, location.state]);

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

  return (
    <div className="flex flex-col h-screen">
      {showDisclaimer && <Disclaimer onClose={() => setShowDisclaimer(false)} />}
      <div className="flex flex-grow overflow-hidden">
        <Sidebar className="fixed top-16 left-0 bottom-0 w-64" isOpen={isSidebarOpen} toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} chatId={chatId} setChatId={setChatId} userId={userId} />
        <div className="flex flex-col flex-grow">
          <Header isAdmin={isAdmin} className="h-16" />
          <div className="flex flex-col flex-grow">
            <MainContent isSidebarOpen={isSidebarOpen} chatId={chatId} userId={userId} />
          </div>
          <Footer />
        </div>
      </div>
    </div>
  );
}

export default ChatPage;