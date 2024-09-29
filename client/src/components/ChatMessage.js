import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { SpeakerWaveIcon, PauseIcon, PlayIcon, DocumentIcon, PhotoIcon, VideoCameraIcon, MusicalNoteIcon, MicrophoneIcon } from '@heroicons/react/24/solid';
import { HandThumbUpIcon as HandThumbUpOutline, HandThumbDownIcon as HandThumbDownOutline } from '@heroicons/react/24/outline'; // Outline Icons
import { HandThumbUpIcon as HandThumbUpSolid, HandThumbDownIcon as HandThumbDownSolid } from '@heroicons/react/24/solid'; // Solid Icons
import LoadingAnimation from './LoadingAnimation';

function ChatMessage({ text, type, shouldStream, mediaType, fileName, inputUserQuery, userId }) {
  const isUser = type === 'user';
  const messageStyle = isUser ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800';
  const alignment = isUser ? 'self-end' : 'self-start';
  const [displayedText, setDisplayedText] = useState('');
  const [isStreamingComplete, setIsStreamingComplete] = useState(false); // New state for tracking streaming completion
  const [audioUrl, setAudioUrl] = useState('');
  const [isAudioPlaying, setIsAudioPlaying] = useState(false); // Track if audio is playing
  const [isAudioLoading, setIsAudioLoading] = useState(false); // Track if audio is being generated
  const [icon, setIcon] = useState(<SpeakerWaveIcon className="w-6 h-6 text-gray-700" />); // Initial icon state
  const [feedback, setFeedback] = useState(null); // State for feedback
  const [showFeedbackPopup, setShowFeedbackPopup] = useState(false); // New state for showing feedback popup
  const [feedbackText, setFeedbackText] = useState(''); // New state to capture feedback text
  const audioRef = useRef(null); // Reference to audio object

  // Split the message into main content and resources
  const mainContent = Array.isArray(text) ? text[0] : text;
  const recommendedResources = Array.isArray(text) && text.length > 1 ? text.slice(1) : [];

  // Helper function to generate a random delay within a range (min, max)
  // This will be used to simulate the streaming/generative effect of ChatGPT
  const getRandomDelay = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

  const localStorageKey = mainContent;
  const [userQuery, setUserQuery] = useState(() => {
    const savedQuery = localStorage.getItem(localStorageKey);
    return savedQuery ? savedQuery : '';
  });

  useEffect(() => {
    if (inputUserQuery) {
      setUserQuery(inputUserQuery);
      localStorage.setItem(localStorageKey, inputUserQuery);
    }
  }, [inputUserQuery, localStorageKey]);

  // Load feedback state from local storage on component mount
  useEffect(() => {
    const savedFeedback = localStorage.getItem(`${localStorageKey}-feedback`);
    if (savedFeedback) {
      setFeedback(savedFeedback);
    }
  }, [localStorageKey]);

  useEffect(() => {
    if (shouldStream && typeof mainContent === 'string') {
      let currentText = '';
      let wordIndex = 0;
      const words = mainContent.split(' ');

      const streamText = () => {
        currentText += words[wordIndex] + ' ';
        setDisplayedText(currentText);
        wordIndex++;

        if (wordIndex < words.length) {

          // If you want the response to be generated faster/slower, change the vale range here
          const randomDelay = getRandomDelay(0, 300); // Set random delay between 0ms and 300ms
          setTimeout(streamText, randomDelay);
        } else {
          setIsStreamingComplete(true); // Mark as complete after all words are displayed
        }
      };

      streamText(); // Start streaming
    } else {
      setDisplayedText(mainContent); // Display normally if not streaming
      setIsStreamingComplete(true); // Immediately mark as complete if not streaming
    }
  }, [mainContent, shouldStream]);

  // Text-to-Speech (TTS) API Integration
  // This function handles the audio generation and playback for existing chat messages. 
  const handleSpeak = async () => {
    if (isAudioPlaying) {
      audioRef.current.pause(); // Pause if audio is already playing
      setIsAudioPlaying(false);
      setIcon(<PlayIcon className="w-6 h-6 text-gray-700" />); // Change icon to Play when paused
    } else if (audioUrl) {
      // Play audio if URL is already generated
      audioRef.current.play();
      setIsAudioPlaying(true);
      setIcon(<PauseIcon className="w-6 h-6 text-gray-700" />); // Change to Pause while playing
    } else {
      // Generate audio from the TTS API
      try {
        setIsAudioLoading(true);
        setIcon(<LoadingAnimation />); // Show loading state

        const response = await fetch('http://localhost:8000/text-to-speech', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ text: mainContent }),
        });

        if (!response.ok) throw new Error('Network response was not ok');

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);

        const audio = new Audio(url);
        audioRef.current = audio; // Store audio object in ref
        audio.playbackRate = 1.5; // Change playback speed if needed

        audio.play();
        setIsAudioPlaying(true);
        setIcon(<PauseIcon className="w-6 h-6 text-gray-700" />); // Set icon to Pause when audio starts playing
        setIsAudioLoading(false);

        // Handle audio ending event to reset icon
        audio.onended = () => {
          setIsAudioPlaying(false);
          setIcon(<SpeakerWaveIcon className="w-6 h-6 text-gray-700" />); // Reset to speaker icon when audio ends
        };
      } catch (error) {
        console.error('Error fetching the audio:', error);
        setIsAudioLoading(false);
        setIcon(<SpeakerWaveIcon className="w-6 h-6 text-gray-700" />); // Reset to speaker if an error occurs
      }
    }
  };

  // This function is used to get the icon for different media types shown in the chat message
  const getMediaIcon = (type, fileName) => {
    const iconMap = {
      document: <DocumentIcon className="h-6 w-6 text-white-500" />,
      image: <PhotoIcon className="h-6 w-6 text-white-500" />,
      video: <VideoCameraIcon className="h-6 w-6 text-white-500" />,
      audio: <MusicalNoteIcon className="h-6 w-6 text-white-500" />,
      voice: <MicrophoneIcon className="h-6 w-6 text-white-500" />,
    };

    const icon = iconMap[type] || null;

    if (icon) {
      return (
        <div className="flex items-center space-x-2">
          {icon}
          <span className="text-m font-bold text-white truncate" style={{ fontFamily: 'Inter' }}>{fileName}</span>
        </div>
      );
    }

    return null;
  };

  // Function to send feedback to the backend
  const sendFeedbackToBackend = async (feedbackType) => {
    try {
      const response = await fetch('http://localhost:8000/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: mainContent,
          feedback: feedbackType,
          feedbackText: feedbackText,
          userText: userQuery,
          userId: userId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send feedback');
      }

      console.log('Feedback sent successfully');
    } catch (error) {
      console.error('Error sending feedback:', error);
    }
  };

  const handleFeedback = (type) => {
    if (feedback === type) {
      // If the same feedback is clicked again, reset to null
      setFeedback(null);
      localStorage.removeItem(`${localStorageKey}-feedback`); // Remove feedback from localStorage
      setShowFeedbackPopup(false);
    } else {
      setFeedback(type);
      localStorage.setItem(`${localStorageKey}-feedback`, type); // Store feedback in localStorage
      setShowFeedbackPopup(true); // Show the feedback popup when thumbs-up or down is clicked
    }
  };

  const handleFeedbackSubmit = () => {
    sendFeedbackToBackend(feedback); // Send feedback to backend
    setShowFeedbackPopup(false); // Close the popup after submission
    setFeedbackText(''); // Reset feedback text
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`p-4 rounded-lg my-2 max-w-xl ${messageStyle} ${alignment}`}
    >
      {mediaType && mediaType !== 'text' && (
        <div className="flex items-center mb-2">
          {getMediaIcon(mediaType, fileName)}
        </div>
      )}
      <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word', fontFamily: 'sans-serif' }}>{shouldStream ? displayedText : mainContent}</pre>

      {/* Only show recommended resources once the streaming is complete */}
      {isStreamingComplete && recommendedResources.length > 0 && (
        <div className="mt-4">
          <p className="text-lg font-semibold mb-2">Recommended Resources:</p>
          <ul className="list-disc pl-5">
            {recommendedResources.map((resource, index) => (
              <li key={index}>{resource}</li>
            ))}
          </ul>
          <div className="flex space-x-4">
            <button
              onClick={handleSpeak}
              disabled={isAudioLoading} // Disable button while audio is loading
              className="p-2 bg-gray-300 rounded-full hover:bg-gray-400 flex items-center justify-center"
              aria-label="Read Aloud"
            >
              {icon} {/* Render the current icon */}
            </button>
            {/* Thumbs Up/Down Feedback */}
            <button
              onClick={() => handleFeedback('up')}
              className={`p-2 rounded-full ${feedback === 'up' ? 'bg-green-400' : 'bg-gray-300'} hover:bg-green-500 flex items-center justify-center`}
              aria-label="Thumbs Up"
            >
              {feedback === 'up' ? <HandThumbUpSolid className="w-6 h-6 text-white" /> : <HandThumbUpOutline className="w-6 h-6 text-gray-700" />}
            </button>
            <button
              onClick={() => handleFeedback('down')}
              className={`p-2 rounded-full ${feedback === 'down' ? 'bg-red-400' : 'bg-gray-300'} hover:bg-red-500 flex items-center justify-center`}
              aria-label="Thumbs Down"
            >
              {feedback === 'down' ? <HandThumbDownSolid className="w-6 h-6 text-white" /> : <HandThumbDownOutline className="w-6 h-6 text-gray-700" />}
            </button>
          </div>
          {showFeedbackPopup && (
            <div className="mt-2 p-2 bg-gray-100 rounded-lg shadow-lg">
              <textarea
                className="w-full p-2 border rounded-md"
                rows="3"
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                placeholder="(Optional) Tell us more about your feedback..."
              ></textarea>
              <button
                onClick={handleFeedbackSubmit}
                className="mt-2 bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
              >
                Submit Feedback
              </button>
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
}

export default ChatMessage;
