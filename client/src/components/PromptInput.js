// src/components/PromptInput.js
import React, { useState, useRef } from 'react';
import { PaperAirplaneIcon, MicrophoneIcon, StopIcon, PaperClipIcon, DocumentIcon, PhotoIcon, MusicalNoteIcon, VideoCameraIcon } from '@heroicons/react/24/outline';
import axios from 'axios';

function PromptInput({ onSendMessage, isLoading }) {
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false); // State to track recording status
  const [selectedFile, setSelectedFile] = useState(null); // State to store the selected file
  const mediaRecorderRef = useRef(null); // To keep reference to media recorder
  const audioChunksRef = useRef([]); // Store audio chunks
  const startTimeRef = useRef(null); // Track the start time of the recording

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      // mediaType and fileName are used to show the correct icon and name in the chat message
      const mediaType = selectedFile ? getFileType(selectedFile) : 'text';
      const fileName = selectedFile ? selectedFile.name : 'text';
      onSendMessage({ text: input, file: selectedFile, mediaType, fileName });
      setInput('');
      setSelectedFile(null); // Clear the file after sending
    }
  };

  // Enter Key should send the message
  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSend();
    }
  };

  // Handle file selection
  const handleFileChange = (file) => {
    if (file) {
      setSelectedFile(file);
    } else {
      console.error("No file provided or file is invalid.");
    }
  };

  // Handle paste events to check for files and handle them
  const handlePaste = (event) => {
    const clipboardData = event.clipboardData || window.clipboardData;
    const items = clipboardData.items;

    for (const item of items) {
      if (item.kind === 'file') {
        const file = item.getAsFile();
        handleFileChange(file); // Treat as a file upload
        event.preventDefault(); // Prevent the file from being pasted as text
        return;
      }
    }
    // If no files are pasted, handle the text paste normally
    // setInput(input + clipboardData.getData('Text'));
  };

  // Determine file type icon
  const getFileIcon = (file) => {
    const fileType = file.type;
    if (fileType.startsWith('image/')) {
      return <PhotoIcon className="h-6 w-6 text-gray-500" />;
    } else if (fileType.startsWith('audio/')) {
      return <MusicalNoteIcon className="h-6 w-6 text-gray-500" />;
    } else if (fileType.startsWith('video/')) {
      return <VideoCameraIcon className="h-6 w-6 text-gray-500" />;
    } else {
      return <DocumentIcon className="h-6 w-6 text-gray-500" />;
    }
  };

  const getFileType = (file) => {
    if (!file) return 'text'; // Default to 'text' if no file is provided
  
    const { type } = file;
  
    if (type.startsWith('image/')) return 'image';
    if (type.startsWith('video/')) return 'video';
    if (type.startsWith('audio/')) return 'audio';
    if (type.startsWith('text/') || type.startsWith('application/')) return 'document';
    return 'file'; // Default for other types or unknown types
  };

  // This function handles voice messages.
  // It records audio, and sends the audio file to the backend for transcription.
  // audio should be longer than 3 seconds. This is to handle accidental recordings.
  const toggleRecording = async () => {
    if (isRecording) {
      // Stop recording
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    } else {
      // Start recording
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      startTimeRef.current = Date.now(); // Record the start time

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const duration = (Date.now() - startTimeRef.current) / 1000; // Calculate the duration in seconds

        if (duration < 3) {
          console.log('Recording too short, less than 3 seconds.');
          audioChunksRef.current = []; // Clear the chunks and don't proceed
          return;
        }

        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        audioChunksRef.current = []; // Clear the audio chunks

        // Send the audio file to the backend for transcription
        const formData = new FormData();
        formData.append('file', audioBlob, 'audio.wav');

        try {
          const response = await axios.post('http://localhost:8000/transcribe-audio', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });
          const transcribedText = response.data.transcription;

          // Set the transcribed text as the message to be sent
          if (transcribedText) {
            console.log('Transcribed text:', transcribedText);
            const mediaType = 'voice';
            onSendMessage({ text: transcribedText, file: selectedFile, mediaType, fileName: 'Voice Message' });
          }
        } catch (error) {
          console.error('Error during transcription:', error);
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    }
  };

  return (
    <div style={{ backgroundColor: '#2f2f2f45' }} className="p-2 shadow-md flex flex-col font-sans rounded-full">
      {/* Show file name and icon when a file is attached */}
      {selectedFile && (
        <div className="flex items-center mb-2">
          {getFileIcon(selectedFile)}
          <span className="ml-2 text-gray-700">{selectedFile.name}</span>
        </div>
      )}
      <div style={{ backgroundColor: '#2f2f2f' }} className=" p-4 shadow-md flex items-center font-sans rounded-full">
        <button
          onClick={toggleRecording}
          className="mr-2 text-gray-600 hover:text-gray-900"
          disabled={isLoading}
        >
          {isRecording ? (
            <StopIcon className="h-6 w-6 text-red-600 transform hover:scale-125 transition-transform duration-200" /> // Stop icon during recording
          ) : (
            <MicrophoneIcon className="h-6 w-6 text-gray-500 hover:text-sky-500 transform hover:scale-125 transition-transform duration-200" /> // Mic icon when not recording
          )}
        </button>
        <label className="mr-2 text-gray-600 hover:text-gray-900 cursor-pointer">
          <PaperClipIcon className="h-6 w-6 text-gray-500 hover:text-sky-500 transform hover:scale-125 transition-transform duration-200" />
          <input
            type="file"
            onChange={(e) => handleFileChange(e.target.files[0])}
            className="hidden"
            disabled={isLoading}
          />
        </label>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          onPaste={handlePaste}
          placeholder="Type your prompt..."
          style={{ backgroundColor: '#2f2f2f', color: '#b4b4b4' }}
          className="flex-grow p-2 border border-gray-500 rounded-lg focus:outline-none"
          disabled={isLoading}
        />
        <button
          onClick={handleSend}
          className={`text-white ml-1 p-2 rounded-xl hover:bg-blue-600 ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
          style={{ backgroundColor: "#212121" }}
          disabled={isLoading}
        >
          <PaperAirplaneIcon className="h-6 w-6 text-gray-500 hover:text-sky-500 transform -rotate-45 hover:scale-125 transition-transform duration-200" />
        </button>
      </div>
    </div>
  );
}

export default PromptInput;
