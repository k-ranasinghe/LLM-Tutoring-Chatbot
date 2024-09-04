// src/components/Sidebar.js
import React, { useState, useEffect } from 'react';
import { XMarkIcon, Bars3Icon, PlusCircleIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline';
import axios from 'axios'

function Sidebar({ isOpen, toggleSidebar, chatId, setChatId }) {
  const [chatTitle, setChatTitle] = useState('');
  const [studentType, setStudentType] = useState('');
  const [learningStyle, setLearningStyle] = useState('');
  const [communicationFormat, setCommunicationFormat] = useState('');
  const [toneStyle, setToneStyle] = useState('');
  const [reasoningFramework, setReasoningFramework] = useState('');
  const [pastChats, setPastChats] = useState([]);

  useEffect(() => {
    getPersonalization(chatId);
    fetchPastChats(); // Fetch past chats on component mount
  }, [chatId]);

  const fetchPastChats = async () => {
    try {
      const response = await axios.get('http://localhost:8000/get-past-chats');
      setPastChats(response.data); // Assuming response data is an array of past chats
    } catch (error) {
      console.error('Error fetching past chats:', error);
    }
  };

  const setChat = async (selectedChatId) => {
    try {
        setChatId(selectedChatId); // Update current chatId

    } catch (error) {
        console.error('Error loading chat:', error);
    }
  };

  function generateRandomString(length, pastChats) {
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
    } while (pastChats.some(chat => chat.ChatID === result));
    
    return result;
  };

  const handleNewChat = () => {
    const chatId = generateRandomString(10, pastChats);
    const chatTitle = "";
    setChatId(chatId); 
    setChatTitle(chatTitle); 
    const personalizationData = {
      chat_id: chatId,
      chat_title: chatTitle,
      student_type: "type1",
      learning_style: "Verbal",
      communication_format: "Textbook",
      tone_style: "Neutral",
      reasoning_framework: "Deductive",
    };
    savePersonalization(personalizationData);
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
        setStudentType(data.student_type || '');
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
      chat_id: chatId,
      chat_title: chatTitle,
      student_type: studentType,
      learning_style: learningStyle,
      communication_format: communicationFormat,
      tone_style: toneStyle,
      reasoning_framework: reasoningFramework,
    };
    console.log(personalizationData);
    savePersonalization(personalizationData);
  };


  return (
    <div className={`text-white flex-shrink-0 ${isOpen ? 'w-64' : 'w-20'} transition-all duration-300 h-full font-sans overflow-y-auto`} style={{backgroundColor:"#042f47"}}>
      <div className="p-4 flex justify-between items-center">
        <h2 className={`text-xl font-bold ${isOpen ? 'block' : 'hidden'}`}>Past Chats</h2>
        <button onClick={toggleSidebar}>
          {isOpen ? <XMarkIcon className="h-6 w-6" /> : <Bars3Icon className="h-6 w-6" />}
        </button>
      </div>
      
      <div className="overflow-y-auto">
        <button onClick={handleNewChat} className="p-2 w-full text-left hover:bg-gray-700 cursor-pointer text-lg font-semibold flex items-center space-x-2"><PlusCircleIcon className="h-6 w-6 mr-2" />New Chat</button>
        <ul>
          {pastChats.map((chat) => (
            <li key={chat.ChatID} className="p-2 hover:bg-gray-700 cursor-pointer" onClick={() => setChat(chat.ChatID)}>
              {chat.Chat_title || `Chat ${chat.ChatID}`}
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
          <label className="block mb-1">Student Type</label>
          <select className="w-full p-2 rounded text-black" value={studentType} onChange={(e) => setStudentType(e.target.value)}>
            <option value="">Select</option>
            <option value="type1">Age 10-15</option>
            <option value="type2">Age 16-18</option>
          </select>
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
      </div>
    </div>
  );
}

export default Sidebar;
