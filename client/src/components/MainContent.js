// src/components/MainContent.js
import React, { useState, useEffect, useRef } from 'react';
import PromptInput from './PromptInput';
import Chat from './Chat';
import axios from 'axios';
import { ChatBubbleOvalLeftEllipsisIcon } from '@heroicons/react/24/outline';

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

function MainContent({ isSidebarOpen, chatId, userId }) {
  const { width } = useWindowDimensions();
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [isNotificationPanelOpen, setIsNotificationPanelOpen] = useState(false);
  const [selectedNotification, setSelectedNotification] = useState(null);
  const [unviewedCount, setUnviewedCount] = useState(0);
  const notificationButtonRef = useRef(null);
  const chatEndRef = useRef(null);
  // const userId = "user123";

  const handleSendMessage = async (message) => {
    setMessages([...messages, { text: message.text, type: 'user', shouldStream: false, mediaType: message.mediaType, fileName: message.fileName, userQuery: message.text }]);
    setIsLoading(true);

    // Prepare form data
    const formData = new FormData();
    formData.append("ChatID", chatId);
    formData.append("UserID", userId);
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

      const botMessage = response.data['response'];
      const botContext = response.data['context'];
      const botFiles = response.data['files'];

      setMessages((prevMessages) => [
        ...prevMessages,
        { text: [botMessage, botContext, botFiles], type: 'bot', shouldStream: true, mediaType: 'text', fileName: 'text', userQuery: message.text },
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
            { text: [msg.content], type: 'user', shouldStream: false, mediaType: mediaType, fileName: fileName }, // Wrap the user message in an array
          ]);
        } else if (msg.type === 'ai') {
          // If the bot message contains context, ensure it’s added correctly
          const botMessage = msg.content;
          const botContext = msg.response_metadata["context"];
          const botFiles = msg.response_metadata["files"];

          setMessages((prevMessages) => [
            ...prevMessages,
            { text: [botMessage, botContext, botFiles], type: 'bot', shouldStream: false, mediaType: 'text', fileName: 'text' }, // Combine bot message and context
          ]);
        }
      });

    } catch (error) {
      console.error('Error loading chat:', error);
    }
  };

  const fetchNotifications = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/get-notifications?user_id=${userId}`);
      setNotifications(response.data); // Assume response structure
      
      const unviewedNotifications = response.data.filter((notification) => notification.viewed === 0);
      setUnviewedCount(unviewedNotifications.length);
      console.log(unviewedNotifications.length);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  const handleNotificationsClick = () => {
    fetchNotifications();
    setIsNotificationPanelOpen(!isNotificationPanelOpen); // Toggle panel visibility
  };

  const handleNotificationClick = async (notification) => {
    if (notification.viewed === 0) {
      // Mark as viewed in local state
      const updatedNotifications = notifications.map((notif) =>
        notif.id === notification.id ? { ...notif, viewed: 1 } : notif
      );
      setNotifications(updatedNotifications);
  
      // Decrease unviewed count
      setUnviewedCount((prevCount) => prevCount - 1);
  
      // Send the update to the backend
      try {
        const id = notification.id;
        await axios.post(`http://localhost:8000/update-notification?id=${id}`);

      } catch (error) {
        console.error('Error updating notification:', error);
      }
    }
  
    // Set the selected notification for detailed view
    setSelectedNotification(notification);
  };

  // UseEffect to load chat messages when chatId changes
  useEffect(() => {
    if (chatId) {
      setMessages([]);
      loadChat(chatId);
    }
  }, [chatId]);

  useEffect(() => {
    fetchNotifications();
  }, []);

  useEffect(() => {
    // Scroll to the bottom when messages change
    const scrollToBottom = () => {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    };
    setTimeout(scrollToBottom, 100);
  }, [messages]);

  return width > 500 ? (
    <div className={`flex-grow flex flex-col ${isSidebarOpen ? 'ml-32' : 'ml-20'} transition-all duration-300 font-sans h-[calc(80vh-4rem)]`}>
      <style>
        {`
      ::-webkit-scrollbar {
        width: 20px; /* Width of the scrollbar */
        background: transparent; /* Transparent background */
      }
      ::-webkit-scrollbar-thumb {
        background-color: rgba(90, 90, 90, 0.8); /* Lighter thumb color */
        border-left: 4px solid #212121;
        border-right: 4px solid #212121;
      }
      ::-webkit-scrollbar-thumb:hover {
        background: rgba(90, 90, 90, 1); /* Darker thumb on hover */
      }
    `}
      </style>
      <div className="flex flex-col flex-grow overflow-hidden">
        <div className="flex-grow overflow-y-auto p-4 pr-32">
          <Chat messages={messages} isLoading={isLoading} userId={userId} chatId={chatId} />
          <div ref={chatEndRef} /> {/* Scroll to this ref */}
        </div>
        <div className="pr-32">
          <div className="flex items-center">
            <div className="flex-grow">
              <PromptInput onSendMessage={handleSendMessage} isLoading={isLoading} />
            </div>
            <button
              ref={notificationButtonRef}
              className="relative -mr-16 ml-3 p-2 rounded-full bg-customtxt"
              onClick={handleNotificationsClick}
            >
              <ChatBubbleOvalLeftEllipsisIcon className="h-8 w-8 text-gray-700 hover:text-sky-700 transform hover:scale-125 transition-transform duration-200" />
              {unviewedCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-600 text-white rounded-full h-5 w-5 flex items-center justify-center text-sm">
                  {unviewedCount}
                </span>
              )}
            </button>
          </div>
        </div>
      </div>
      {isNotificationPanelOpen && (
        <div
          className="absolute z-50"
          style={{
            bottom: notificationButtonRef.current
              ? notificationButtonRef.current.getBoundingClientRect().top - 545 // Adjust as needed
              : 0,
            left: notificationButtonRef.current
              ? notificationButtonRef.current.getBoundingClientRect().left - 355
              : 0,
            maxHeight: '500px',
            width: '400px',
            overflowY: 'auto',
          }}
        >
          <div className="bg-custombg p-8 rounded-2xl shadow-lg">
            <h2 className="text-2xl font-bold mb-5 text-customtxt text-center">Notification Panel</h2>
            {notifications.length === 0 ? (
              <p className="text-center text-customtxt">You do not currently have any notifications.</p>
            ) : (
              <ul>
                {notifications.map((notification, index) => (
                  <li
                    key={index}
                    className={`p-2 mb-1 text-customtxt hover:bg-custombg2 cursor-pointer border border-customtxt rounded-3xl ${
                      notification.viewed === 0 ? 'bg-custombg3' : ''
                    }`}
                    onClick={() => handleNotificationClick(notification)}
                  >
                    {notification.query}
                  </li>
                ))}
              </ul>
            )}
            <div className="flex justify-center">
              <button
                className="mt-4 p-3 px-5 bg-customtxt text-custombg font-bold rounded-2xl hover:scale-105 transition-transform duration-200"
                onClick={() => setIsNotificationPanelOpen(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {selectedNotification && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center" onClick={() => setSelectedNotification(null)}>
          <div className="bg-custombg text-customtxt p-8 rounded-2xl shadow-lg w-1/3 space-y-2">
            <h2 className="text-xl font-bold text-center">Notification Details</h2>
            <p><strong>Query:</strong> {selectedNotification.query}</p>
            {/* <p><strong>Chatbot Response:</strong> {selectedNotification.chatbot_response}</p> */}
            <p><strong>Mentor Response:</strong> {selectedNotification.mentor_response}</p>
            <p><strong>Mentor ID:</strong> {selectedNotification.mentorid}</p>
          </div>
        </div>
      )}
    </div>
    ) : (
      /* Mobile View */
      <div className="flex-grow flex flex-col ml-1 transition-all duration-300 font-sans h-[calc(80vh-4rem)]">
      <button
              ref={notificationButtonRef}
              className="absolute top-20 right-4 p-2 rounded-full bg-customtxt"
              onClick={handleNotificationsClick}
            >
              <ChatBubbleOvalLeftEllipsisIcon className="h-6 w-6 text-gray-700 hover:text-sky-700 transform hover:scale-110 transition-transform duration-200" />
              {unviewedCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-600 text-white rounded-full h-4 w-4 flex items-center justify-center text-xs">
                  {unviewedCount}
                </span>
              )}
            </button>
      <div className="flex flex-col flex-grow overflow-hidden">
        <div className="flex-grow overflow-y-auto p-4 overflow-x-hidden w-auto -mr-6 -ml-7">
          <Chat messages={messages} isLoading={isLoading} userId={userId} chatId={chatId} />
          <div ref={chatEndRef} />
        </div>
        <div>
          <div className="flex items-center">
            <div className="flex-grow -ml-0.5">
              <PromptInput onSendMessage={handleSendMessage} isLoading={isLoading} />
            </div>
          </div>
        </div>
      </div>
      {isNotificationPanelOpen && (
  <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
    <div className="bg-custombg p-4 rounded-xl shadow-lg max-w-sm w-full">
      <h2 className="text-lg font-bold mb-3 text-customtxt text-center">Notification Panel</h2>
      {notifications.length === 0 ? (
        <p className="text-center text-customtxt">You do not currently have any notifications.</p>
      ) : (
        <ul>
          {notifications.map((notification, index) => (
            <li
              key={index}
              className={`p-2 mb-1 text-customtxt hover:bg-custombg2 cursor-pointer border border-customtxt rounded-2xl ${
                notification.viewed === 0 ? 'bg-custombg3' : ''
              }`}
              onClick={() => handleNotificationClick(notification)}
            >
              {notification.query}
            </li>
          ))}
        </ul>
      )}
      <div className="flex justify-center">
        <button
          className="mt-4 p-2 px-4 bg-customtxt text-custombg font-bold rounded-xl hover:scale-105 transition-transform duration-200"
          onClick={() => setIsNotificationPanelOpen(false)}
        >
          Close
        </button>
      </div>
    </div>
  </div>
)}

      {selectedNotification && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center" onClick={() => setSelectedNotification(null)}>
          <div className="bg-custombg text-customtxt p-4 rounded-xl shadow-lg w-2/3 space-y-2">
            <h2 className="text-lg font-bold text-center">Notification Details</h2>
            <p><strong>Query:</strong> {selectedNotification.query}</p>
            <p><strong>Mentor Response:</strong> {selectedNotification.mentor_response}</p>
            <p><strong>Mentor ID:</strong> {selectedNotification.mentorid}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default MainContent;
