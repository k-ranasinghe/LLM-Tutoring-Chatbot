import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import MainContent from '../components/MainContent';
import Header from '../components/Header';
import Footer from '../components/Footer';
import Disclaimer from '../components/Disclaimer';
import { WindowIcon } from '@heroicons/react/24/outline';
import axios from 'axios';
import Cookies from 'js-cookie';


function useWindowDimensions() {
  const [windowDimensions, setWindowDimensions] = useState({
    width: window.innerWidth,
    height: window.innerHeight
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowDimensions({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowDimensions;
}

function ChatPage() {
  const location = useLocation();
  const { width } = useWindowDimensions();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [chatId, setChatId] = useState("");
  const [showDisclaimer, setShowDisclaimer] = useState(false);
  const [showSidebarOnly, setShowSidebarOnly] = useState(false);
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
      {width > 500 ? (
        <div className="flex flex-grow overflow-hidden">
          {!showSidebarOnly && (
            <Sidebar
              className="fixed top-16 left-0 bottom-0 w-64"
              isOpen={isSidebarOpen}
              toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
              chatId={chatId}
              setChatId={setChatId}
              userId={userId}
            />
          )}
          <div className="flex flex-col flex-grow">
            <Header isAdmin={isAdmin} className="h-16" />
            <div className="flex flex-col flex-grow">
              <MainContent isSidebarOpen={isSidebarOpen} chatId={chatId} userId={userId} />
            </div>
            <Footer />
          </div>

          <button
            className="absolute top-28 left-4 z-10 p-2 rounded-3xl bg-customtxt"
            onClick={() => setShowSidebarOnly(prev => !prev)}
          >
            <WindowIcon className="h-8 w-8 text-gray-700 hover:text-sky-700 transform rotate-90 -scale-y-100 hover:scale-125 transition-transform duration-200" />
          </button>
        </div>
      ) : (
        /* Mobile View */
        <div className="flex flex-col h-screen overflow-x-hidden"> {/* Prevent horizontal overflow */}
          {/* Header with slightly reduced height */}
          <Header isAdmin={isAdmin} className="h-10" />
          {!showSidebarOnly && (
            <Sidebar
              className={`fixed top-16 left-0 bottom-0 w-64 z-20 transition-transform duration-300 ${showSidebarOnly ? 'translate-x-0' : '-translate-x-full'}`}
              isOpen={isSidebarOpen}
              toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
              chatId={chatId}
              setChatId={setChatId}
              userId={userId}
            />
          )}
          <button
            className="absolute top-20 left-4 z-10 p-1 rounded-full bg-customtxt"
            onClick={() => setShowSidebarOnly(prev => !prev)}
          >
            <WindowIcon className="h-8 w-8 text-gray-700 transform rotate-90 -scale-y-100 hover:scale-125 transition-transform duration-200" />
          </button>
          {/* Main content should take full width and be centered */}
          <div className="flex flex-col flex-grow justify-center items-center w-full overflow-hidden"> {/* Ensure no horizontal overflow */}
            <MainContent
              className="w-full h-full p-4 overflow-hidden" // Ensure no overflow
              isSidebarOpen={false} // Sidebar not used for mobile
              chatId={chatId}
              userId={userId}
            />
          </div>

          {/* Footer */}
          <Footer />
        </div>
      )}
    </div>
  );
}

export default ChatPage;