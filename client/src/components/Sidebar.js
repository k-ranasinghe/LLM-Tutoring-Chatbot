// src/components/Sidebar.js
import React, { useState, useEffect } from 'react';
import { XMarkIcon, Bars3Icon } from '@heroicons/react/24/outline';
import axios from 'axios'

function Sidebar({ isOpen, toggleSidebar, chatId }) {
  const [chatTitle, setChatTitle] = useState('');
  const [studentType, setStudentType] = useState('');
  const [learningStyle, setLearningStyle] = useState('');
  const [communicationFormat, setCommunicationFormat] = useState('');
  const [toneStyle, setToneStyle] = useState('');
  const [reasoningFramework, setReasoningFramework] = useState('');

  useEffect(() => {
    getPersonalization(chatId);
  }, [chatId]);

  const savePersonalization = async (personalizationData) => {
    // try {
    //   const response = await fetch('http://localhost:8000/update-personalization', {
    //     method: 'POST',
    //     headers: {
    //       'Content-Type': 'application/json',
    //     },
    //     body: personalizationData
    //   });

    //   if (!response.ok) {
    //     throw new Error('Failed to save personalization');
    //   }

    //   console.log('Personalization saved successfully');
    // } catch (error) {
    //   console.error('Error:', error);
    // }

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
    <div className={`text-white flex-shrink-0 ${isOpen ? 'w-64' : 'w-20'} transition-all duration-300 h-full font-sans`} style={{backgroundColor:"#042f47"}}>
      <div className="p-4 flex justify-between items-center">
        <h2 className={`text-xl font-bold ${isOpen ? 'block' : 'hidden'}`}>Past Chats</h2>
        <button onClick={toggleSidebar}>
          {isOpen ? <XMarkIcon className="h-6 w-6" /> : <Bars3Icon className="h-6 w-6" />}
        </button>
      </div>
      <div className="overflow-y-auto">
        {/* Add your past chats here */}
        <ul>
          <li className="p-2 hover:bg-gray-700 cursor-pointer">{chatTitle}</li>
          <li className="p-2 hover:bg-gray-700 cursor-pointer">Chat 2</li>
          <li className="p-2 hover:bg-gray-700 cursor-pointer">Chat 3</li>
        </ul>
      </div>
      <div className="p-4">
        <h3 className="text-lg font-bold mb-2">Personalization</h3>
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
