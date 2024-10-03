// src/components/Sidebar.js
import React, { useState, useEffect } from 'react';
import { XMarkIcon, Bars3Icon, PlusCircleIcon, AdjustmentsHorizontalIcon, TrashIcon } from '@heroicons/react/24/outline';
import axios from 'axios'

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
      UserID: "user123",
      chat_title: chatTitle,
      learning_style: "Verbal",
      communication_format: "Textbook",
      tone_style: "Neutral",
      reasoning_framework: "Deductive",
    };
    savePersonalization(personalizationData);
    window.location.reload();
  };

  const savePersonalization = async (personalizationData) => {
    const url = "http://localhost:8000/update-personalization";
    const postData = personalizationData;

    try{
      const response = await axios.post(url,postData);
      
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
      UserID: "user123",
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
        } else {
          console.error('Failed to delete chat:', await response.text());
        }
      } catch (error) {
        console.error('Error deleting chat:', error);
      }
  };

  return (
    <div className={`text-white flex-shrink-0 ${isOpen ? 'w-64' : 'w-20'} transition-all duration-300 h-full font-sans overflow-y-auto`} style={{backgroundColor:"#042f47"}}>
      <div className="p-4 flex justify-between items-center">
        <h2 className={`text-xl font-bold ${isOpen ? 'block' : 'hidden'}`}>Past Chats</h2>
        <button onClick={toggleSidebar}>
          {isOpen ? <XMarkIcon className="h-6 w-6 transform hover:scale-125 transition-transform duration-200" /> : <Bars3Icon className="h-6 w-6 transform hover:scale-125 transition-transform duration-200" />}
        </button>
      </div>
      
      <div className="overflow-y-auto">
        <button onClick={handleNewChat} className="p-2 w-full text-left hover:bg-gray-700 cursor-pointer text-lg font-semibold flex items-center space-x-2"><PlusCircleIcon className="h-6 w-6 mr-2 transform hover:scale-125 transition-transform duration-200" />New Chat</button>
        <ul>
          {pastChats.map((chat) => (
            <li key={chat.ChatID} className="p-2 hover:bg-gray-700 cursor-pointer flex justify-between items-center">
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

      <div className="p-4">
        <h3 className="text-lg font-bold mb-2 flex items-center space-x-2"><AdjustmentsHorizontalIcon className="h-6 w-6 mr-2" />Personalization</h3>
        <div className="mb-2">
          <label className="block mb-1">Chat Title</label>
          <input 
            type="text" 
            className="w-full p-2 rounded text-black" 
            value={chatTitle} 
            onChange={(e) => setChatTitle(e.target.value)} 
          />
        </div>
        <div className="mb-2">
          <label className="block mb-1">Learning Style</label>
          <select className="w-full p-2 rounded text-black" value={learningStyle} onChange={(e) => setLearningStyle(e.target.value)}>
            <option value="">Select</option>
            <option value="Visual">Visual</option>
            <option value="Verbal">Verbal</option>
            <option value="Active">Active</option>
            <option value="Intuitive">Intuitive</option>
            <option value="Reflective">Reflective</option>
          </select>
        </div>
        <div className="mb-2">
          <label className="block mb-1">Communication Format</label>
          <select className="w-full p-2 rounded text-black" value={communicationFormat} onChange={(e) => setCommunicationFormat(e.target.value)}>
            <option value="">Select</option>
            <option value="Textbook">Textbook</option>
            <option value="Layman">Layman</option>
            <option value="Storytelling">Storytelling</option>
          </select>
        </div>
        <div className="mb-2">
          <label className="block mb-1">Tone Style</label>
          <select className="w-full p-2 rounded text-black" value={toneStyle} onChange={(e) => setToneStyle(e.target.value)}>
            <option value="">Select</option>
            <option value="Encouraging">Encouraging</option>
            <option value="Neutral">Neutral</option>
            <option value="Informative">Informative</option>
            <option value="Friendly">Friendly</option>
          </select>
        </div>
        <div className="mb-2">
          <label className="block mb-1">Reasoning Framework</label>
          <select className="w-full p-2 rounded text-black" value={reasoningFramework} onChange={(e) => setReasoningFramework(e.target.value)}>
            <option value="">Select</option>
            <option value="Deductive">Deductive</option>
            <option value="Inductive">Inductive</option>
            <option value="Abductive">Abductive</option>
            <option value="Analogical">Analogical</option>
          </select>
        </div>
        <button 
          className="w-full bg-blue-600 hover:bg-blue-700 text-white p-2 rounded mt-2"
          onClick={handleSave}>
          Save
        </button>

        {showDeletePopup && (
          <div className="fixed inset-0 flex items-center justify-center bg-gray-800 bg-opacity-75">
            <div className="bg-white p-8 rounded-lg shadow-lg text-center relative">
              <div className="absolute inset-x-0 top-[-35px] flex justify-center">
                <div className="h-16 w-16 bg-red-500 rounded-full flex items-center justify-center">
                  <TrashIcon className="h-12 w-12 text-white" />
                </div>
              </div>
              <h2 className="text-2xl font-bold mb-2 text-gray-800 mt-6">Delete Chat</h2>
              <p className="text-gray-600 mb-6 text-lg">Are you sure you want to delete the chat?</p>
              <div className="flex justify-center space-x-4">
                <button 
                  className="bg-red-500 text-white px-6 py-3 rounded-md font-semibold hover:bg-red-700" 
                  onClick={confirmDeleteChat}>
                  Yes, Delete
                </button>
                <button 
                  className="bg-gray-300 text-black px-6 py-3 rounded-md font-semibold hover:bg-gray-400" 
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
