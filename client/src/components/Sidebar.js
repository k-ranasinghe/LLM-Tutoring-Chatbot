// src/components/Sidebar.js
import React, { useState, useEffect } from 'react';
import { PlusCircleIcon, AdjustmentsHorizontalIcon, TrashIcon, ChatBubbleLeftRightIcon, WindowIcon, ChevronUpIcon, ChevronDownIcon } from '@heroicons/react/24/outline';
import axios from 'axios'
import Logo from "../logo.avif";

function Sidebar({ isOpen, toggleSidebar, chatId, setChatId, userId }) {
  const [chatTitle, setChatTitle] = useState('');
  const [learningStyle, setLearningStyle] = useState('');
  const [communicationFormat, setCommunicationFormat] = useState('');
  const [toneStyle, setToneStyle] = useState('');
  const [reasoningFramework, setReasoningFramework] = useState('');
  const [pastChats, setPastChats] = useState([]);
  const [chatIDs, setChatIDs] = useState([]);
  const [showDeletePopup, setShowDeletePopup] = useState(false);
  const [chatToDelete, setChatToDelete] = useState(null); // Store the chat ID to delete

  const [isPastChatsOpen, setIsPastChatsOpen] = useState(true);
  const [isPersonalizationOpen, setIsPersonalizationOpen] = useState(true);

  useEffect(() => {
    getPersonalization(chatId);
    fetchPastChats(userId); // Fetch past chats on component mount
    fetchChatIDs();
  }, [chatId]);

  const fetchPastChats = async (userId) => {
    try {
      const response = await axios.get(`http://localhost:8000/get-past-chats?userId=${userId}`);
      setPastChats(response.data);
    } catch (error) {
      console.error('Error fetching past chats:', error);
    }
  };

  // This function fetches all chat IDs. Used when generating a new chat ID.
  const fetchChatIDs = async () => {
    try {
      const response = await axios.get("http://localhost:8000/get-chat-ids");
      setChatIDs(response.data);
    } catch (error) {
      console.error('Error fetching chat ids:', error);
    }
  };

  const setChat = async (selectedChatId) => {
    try {
      setChatId(selectedChatId); // Update current chatId

    } catch (error) {
      console.error('Error loading chat:', error);
    }
  };

  // This function generates a random string of a given length that is not already in the chatIDs array
  function generateRandomString(length, chatIDs) {
    const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    const randomValues = new Uint8Array(length);

    do {
      result = [];
      window.crypto.getRandomValues(randomValues);
      for (let i = 0; i < length; i++) {
        result.push(charset[randomValues[i] % charset.length]);
      }
      result = result.join('');
    } while (chatIDs.some(chat => chat === result));

    return result;
  };

  // This function creates a new chat.
  // When chat_title is empty, a new title is generated in the backend.
  // Default personalization values are set.
  const handleNewChat = () => {
    const chatId = generateRandomString(10, chatIDs);
    const chatTitle = "";
    setChatId(chatId);
    setChatTitle(chatTitle);
    const personalizationData = {
      ChatID: chatId,
      UserID: userId,
      chat_title: chatTitle,
      learning_style: "Verbal",
      communication_format: "Textbook",
      tone_style: "Neutral",
      reasoning_framework: "Deductive",
    };
    savePersonalization(personalizationData);
    // window.location.reload();
  };

  const savePersonalization = async (personalizationData) => {
    const url = "http://localhost:8000/update-personalization";
    const postData = personalizationData;

    try {
      const response = await axios.post(url, postData);

      console.log('Personalization saved successfully');
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const getPersonalization = async (chatId) => {
    try {
      const response = await fetch(`http://localhost:8000/get-personalization?chat_id=${chatId}`);
      const data = await response.json();

      if (response.ok) {
        setChatTitle(data.chat_title || '');
        setLearningStyle(data.learning_style || '');
        setCommunicationFormat(data.communication_format || '');
        setToneStyle(data.tone_style || '');
        setReasoningFramework(data.reasoning_framework || '');
      } else {
        console.error('Failed to fetch personalization data');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleSave = () => {
    const personalizationData = {
      ChatID: chatId,
      UserID: userId,
      chat_title: chatTitle,
      learning_style: learningStyle,
      communication_format: communicationFormat,
      tone_style: toneStyle,
      reasoning_framework: reasoningFramework,
    };
    console.log(personalizationData);
    savePersonalization(personalizationData);
    window.location.reload();
  };

  const handleDeleteChat = (chatId) => {
    setChatToDelete(chatId); // Set the chat to delete
    setShowDeletePopup(true); // Show the delete confirmation popup
  };

  const confirmDeleteChat = async () => {
    try {
      const response = await fetch(`http://localhost:8000/delete-chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ chat_id: chatToDelete }), // Send the chat ID in the body
      });

      if (response.ok) {
        setPastChats(pastChats.filter(chat => chat.ChatID !== chatToDelete)); // Remove the chat from the list
        setShowDeletePopup(false); // Hide the delete popup
        setChatToDelete(null); // Clear the chat to delete
        window.location.reload();
      } else {
        console.error('Failed to delete chat:', await response.text());
      }
    } catch (error) {
      console.error('Error deleting chat:', error);
    }
  };

  return (
    <div className={`text-customtxt flex-shrink-0 ${isOpen ? 'w-64' : 'w-20'} transition-all duration-300 h-full font-sans overflow-y-auto`} 
      style={{
        backgroundColor: "#171717",
        // scrollbarColor: "#5a5a5a #171717",
      }}
      >
      <style>
    {`
      ::-webkit-scrollbar {
        width: 20px; /* Width of the scrollbar */
        background: transparent; /* Transparent background */
      }
      ::-webkit-scrollbar-thumb {
        background-color: rgba(90, 90, 90, 0.8); /* Lighter thumb color */
        border-left: 4px solid #171717;
        border-right: 4px solid #171717;
      }
      ::-webkit-scrollbar-thumb:hover {
        background: rgba(90, 90, 90, 1); /* Darker thumb on hover */
      }
    `}
  </style>
      <img src={Logo} alt="Chat GPT Logo" style={{ backgroundColor: "#ffffff" }} className="object-contain h-30 w-35" />
      {/* <div className="flex justify-end">
        <button onClick={toggleSidebar}>
          <WindowIcon className="h-6 w-6 mt-2 mr-3 -mb-3 transform rotate-90 -scale-y-100 hover:scale-125 transition-transform duration-200" />
        </button>
      </div> */}

      <div className="p-4 flex justify-between items-center mt-10">
        <h3 className={`text-lg font-bold -mb-3 flex items-center space-x-2 ${isOpen ? 'block' : 'hidden'}`}><ChatBubbleLeftRightIcon className="h-6 w-6 mr-2" />Past Chats</h3>
        <button onClick={() => setIsPastChatsOpen(!isPastChatsOpen)}>
          {isPastChatsOpen ? <ChevronUpIcon className="h-6 w-6" /> : <ChevronDownIcon className="h-6 w-6" />}
        </button>
      </div>
      {isPastChatsOpen && (
        <div className="overflow-y-auto ml-2">
          <button onClick={handleNewChat} className="p-2 w-full text-left hover:bg-custombg rounded-lg cursor-pointer text-sm font-semibold flex items-center space-x-2"><PlusCircleIcon className="h-6 w-6 mr-2 transform hover:scale-125 transition-transform duration-200" />New Chat</button>
          <ul>
            {pastChats.map((chat) => (
              <li key={chat.ChatID} className="p-2 text-sm hover:bg-custombg rounded-lg cursor-pointer flex justify-between items-center">
                <span onClick={() => setChat(chat.ChatID)}>
                  {chat.Chat_title || `Untitled Chat`}
                </span>
                <button onClick={() => handleDeleteChat(chat.ChatID)} className="ml-2">
                  <TrashIcon className="h-5 w-5 text-white hover:text-red-500 transform hover:scale-125 transition-transform duration-200" />
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="p-4">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-bold mb-2 flex items-center space-x-2"><AdjustmentsHorizontalIcon className="h-6 w-6 mr-2" />Personalization</h3>
          <button onClick={() => setIsPersonalizationOpen(!isPersonalizationOpen)}>
            {isPersonalizationOpen ? <ChevronUpIcon className="h-6 w-6" /> : <ChevronDownIcon className="h-6 w-6" />}
          </button>
        </div>
        {isPersonalizationOpen && (
          <>
            <div className="mb-2">
              <label className="block text-sm mb-1">Chat Title</label>
              <textarea
                className="w-full p-1 py-2 text-sm rounded bg-custombg resize-none"
                value={chatTitle}
                onChange={(e) => setChatTitle(e.target.value)}
                rows="2" // Set the number of visible rows to 2
                placeholder="Type your chat title..."
              />
            </div>
            <div className="mb-2">
              <label className="block text-sm mb-1">Learning Style</label>
              <select className="w-full p-1 py-2 text-sm rounded bg-custombg" value={learningStyle} onChange={(e) => setLearningStyle(e.target.value)}>
                <option value="">Select</option>
                <option value="Visual">Visual</option>
                <option value="Verbal">Verbal</option>
                <option value="Active">Active</option>
                <option value="Intuitive">Intuitive</option>
                <option value="Reflective">Reflective</option>
              </select>
            </div>
            <div className="mb-2">
              <label className="block text-sm mb-1">Communication Format</label>
              <select className="w-full p-1 py-2 text-sm rounded bg-custombg" value={communicationFormat} onChange={(e) => setCommunicationFormat(e.target.value)}>
                <option value="">Select</option>
                <option value="Textbook">Textbook</option>
                <option value="Layman">Layman</option>
                <option value="Storytelling">Storytelling</option>
              </select>
            </div>
            <div className="mb-2">
              <label className="block text-sm mb-1">Tone Style</label>
              <select className="w-full p-1 py-2 text-sm rounded bg-custombg" value={toneStyle} onChange={(e) => setToneStyle(e.target.value)}>
                <option value="">Select</option>
                <option value="Encouraging">Encouraging</option>
                <option value="Neutral">Neutral</option>
                <option value="Informative">Informative</option>
                <option value="Friendly">Friendly</option>
              </select>
            </div>
            <div className="mb-2">
              <label className="block text-sm mb-1">Reasoning Framework</label>
              <select className="w-full p-1 py-2 text-sm rounded bg-custombg" value={reasoningFramework} onChange={(e) => setReasoningFramework(e.target.value)}>
                <option value="">Select</option>
                <option value="Deductive">Deductive</option>
                <option value="Inductive">Inductive</option>
                <option value="Abductive">Abductive</option>
                <option value="Analogical">Analogical</option>
              </select>
            </div>
            <div className="flex justify-center">
              <button
                style={{ backgroundColor: "#4038be99" }}
                className="w-40 text-customtxt p-2 rounded-2xl font-semibold hover:scale-110 transition-transform duration-200"
                onClick={handleSave}>
                Save
              </button>
            </div>
          </>
        )}

        {showDeletePopup && (
          <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-75">
            <div className="bg-custombg p-8 rounded-lg shadow-lg text-center relative">
              <div className="absolute inset-x-0 top-[-35px] flex justify-center">
                <div className="h-16 w-16 bg-red-800  rounded-full flex items-center justify-center">
                  <TrashIcon className="h-12 w-12 text-gray-400" />
                </div>
              </div>
              <h2 className="text-2xl font-bold mb-2 text-customtxt mt-6">Delete Chat</h2>
              <p className="text-gray-400 mb-6 text-lg">Are you sure you want to delete the chat?</p>
              <div className="flex justify-center space-x-4">
                <button
                  className="bg-red-800 text-white px-6 py-3 rounded-md font-semibold hover:bg-red-700 hover:scale-105 transition-transform duration-200"
                  onClick={confirmDeleteChat}>
                  Yes, Delete
                </button>
                <button
                  className="bg-gray-400 text-black px-6 py-3 rounded-md font-semibold hover:bg-gray-300 hover:scale-105 transition-transform duration-200"
                  onClick={() => setShowDeletePopup(false)}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Sidebar;
