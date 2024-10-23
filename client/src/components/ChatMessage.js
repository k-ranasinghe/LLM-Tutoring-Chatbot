import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';
import { SpeakerWaveIcon, PauseIcon, PlayIcon, DocumentIcon, PhotoIcon, VideoCameraIcon, MusicalNoteIcon, MicrophoneIcon, ChevronUpIcon, ChevronDownIcon } from '@heroicons/react/24/solid';
import { HandThumbUpIcon as HandThumbUpOutline, HandThumbDownIcon as HandThumbDownOutline } from '@heroicons/react/24/outline'; // Outline Icons
import { HandThumbUpIcon as HandThumbUpSolid, HandThumbDownIcon as HandThumbDownSolid } from '@heroicons/react/24/solid'; // Solid Icons
import LoadingAnimation from './LoadingAnimation';

function ChatMessage({ text, type, shouldStream, mediaType, fileName, inputUserQuery, userId, chatId }) {
  const isUser = type === 'user';
  const messageStyle = isUser ? 'bg-custombg1 text-customtxt' : 'bg-custombg text-customtxt';
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
  const [recommendedResources, setRecommendedResources] = useState({});
  const [imageUrls, setImageUrls] = useState([]);
  const [resourcesOpen, setResourcesOpen] = useState(false);
  const [relatedWorkOpen, setRelatedWorkOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);

  // Split the message into main content and resources
  const mainContent = Array.isArray(text) ? text[0] : text;
  const resources = Array.isArray(text) && text.length > 1 ? text.slice(1)[0] : [];

  useEffect(() => {
    const resources = Array.isArray(text) && text.length > 1 ? text.slice(1) : [];

    if (resources.length > 0) {
      const files = text.slice(2)[0];
      setImageUrls(files);
    }
    setRecommendedResources(resources);
  }, [text]);


  const handleImageClick = (url) => {
    setSelectedImage(url);
  };

  const closeImagePopup = () => {
    setSelectedImage(null);
  };

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
          const randomDelay = getRandomDelay(0, 100); // Set random delay between 0ms and 300ms
          setTimeout(streamText, randomDelay);
        } else {
          setIsStreamingComplete(true); // Mark as complete after all words are displayed
          fetchRecommendedResources(); // Fetch recommended resources after streaming is complete
        }
      };

      streamText(); // Start streaming
    } else {
      setDisplayedText(mainContent); // Display normally if not streaming
      setIsStreamingComplete(true); // Immediately mark as complete if not streaming
    }
  }, [mainContent, shouldStream]);


  const fetchRecommendedResources = async () => {
    try {
      const response = await fetch('http://localhost:8000/fetch-resources', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input_text: userQuery, // Use the current user query
          response: mainContent, // Use the main response that was streamed
          chatId: chatId,
        }),
      });

      const data = await response.json();
      console.log('Recommended resources:', data);
      setRecommendedResources(data); // Update state with new resources
    } catch (error) {
      console.error('Error fetching resources:', error);
    }
  };


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
          <span className="text-m font-bold text-customtxt truncate" style={{ fontFamily: 'Inter' }}>{fileName}</span>
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

  const renderRecommendedResources = (resources = {}) => {
    const { 'YouTube Videos': youtubeVideos = [], 'Web Articles': webArticles = [] } = resources;

    return (
      <div className="-mt-4 p-4">
        {youtubeVideos.length > 0 && (
          <>
            <p className="text-lg font-bold mb-1 text-customtxt">▶️ YouTube Videos:</p>
            <ul className="list-disc pl-8 space-y-0">
              {youtubeVideos.map((video, index) => {
                const [name, url] = video.split(': ').map(item => item.trim());
                return (
                  <li key={index}>
                    <a href={url} target="_blank" rel="noopener noreferrer" className="text-sky-600 hover:text-gray-500 transition-colors">
                      {name}
                    </a>
                  </li>
                );
              })}
            </ul>
          </>
        )}
        {webArticles.length > 0 && (
          <>
            <p className="text-lg font-bold mt-6 mb-1 text-customtxt">📰 Web Articles:</p>
            <ul className="list-disc pl-8 space-y-0">
              {webArticles.map((article, index) => {
                const [name, url] = article.split(': ').map(item => item.trim());
                return (
                  <li key={index}>
                    <a href={url} target="_blank" rel="noopener noreferrer" className="text-sky-600 hover:text-gray-500 transition-colors">
                      {name}
                    </a>
                  </li>
                );
              })}
            </ul>
          </>
        )}
      </div>
    );
  };


  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`p-4 rounded-2xl my-2 max-w-xl ${messageStyle} ${alignment}`}
    >
      {mediaType && mediaType !== 'text' && (
        <div className="flex items-center mb-2">
          {getMediaIcon(mediaType, fileName)}
        </div>
      )}
      <ReactMarkdown
        className="whitespace-pre-wrap"
        components={{
          // Add any custom components here if needed
        }}
      >
        {shouldStream ? displayedText : mainContent}
      </ReactMarkdown>
      {/* Only show recommended resources once the streaming is complete */}
      {isStreamingComplete && typeof resources === 'object' && Object.keys(resources).length > 0 && (
        <div className="mt-4">
          <p className="text-xl font-semibold mb-2 flex items-center">
            <span className="mr-2">Recommended Resources</span>
            <button
              onClick={() => setResourcesOpen(prev => !prev)}
              className="focus:outline-none"
              aria-label={resourcesOpen ? "Minimize resources" : "Expand resources"}
            >
              {resourcesOpen ? <ChevronUpIcon className="h-6 w-6" /> : <ChevronDownIcon className="h-6 w-6" />}
            </button>
          </p>
          {resourcesOpen && (
            <ul className="list-disc pl-5">
              {renderRecommendedResources(recommendedResources[0])}
            </ul>
          )}
          {isStreamingComplete && Array.isArray(imageUrls) && imageUrls.length > 0 && (
            <div className="mt-4">
              <p className="text-xl font-semibold mb-2 flex items-center">
                <span className="mr-2">Related Work</span>
                <button onClick={() => setRelatedWorkOpen(prev => !prev)} className="focus:outline-none">
                  {relatedWorkOpen ? <ChevronUpIcon className="h-6 w-6" /> : <ChevronDownIcon className="h-6 w-6" />}
                </button>
              </p>
              {relatedWorkOpen && (
                <div className="overflow-x-auto flex mb-2">
                  <style>
                    {`
                      ::-webkit-scrollbar {
                        width: 20px; /* Width of the scrollbar */
                        background: transparent; /* Transparent background */
                      }
                      ::-webkit-scrollbar-thumb {
                        background-color: rgba(90, 90, 90, 0.8); /* Lighter thumb color */
                        border-left: 0px solid #212121;
                        border-right: 0px solid #212121;
                      }
                      ::-webkit-scrollbar-thumb:hover {
                        background: rgba(90, 90, 90, 1); /* Darker thumb on hover */
                      }
                    `}
                  </style>
                  {imageUrls.map((url, index) => (
                    <div key={index} className="flex-shrink-0 p-2">
                      <img
                        src={url}
                        alt={`Related work ${index + 1}`}
                        className="rounded-lg shadow-md w-48 h-auto cursor-pointer" // Adjust width as needed
                        onClick={() => handleImageClick(url)} // Handle click on the image
                      />
                    </div>
                  ))}
                </div>
              )}
              {selectedImage && (
                <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-75" onClick={closeImagePopup}>
                  <img src={selectedImage} alt="Selected" className="max-w-3xl max-h-3/4 rounded-lg" />
                </div>
              )}
            </div>
          )}
        </div>
      )}
      {isStreamingComplete && !isUser && (
        <div className="flex space-x-4 mt-4">
          <button
            onClick={handleSpeak}
            disabled={isAudioLoading} // Disable button while audio is loading
            className="p-2 bg-gray-300 rounded-full hover:bg-sky-500 flex items-center justify-center hover:scale-125 transition-transform duration-200"
            aria-label="Read Aloud"
          >
            {icon} {/* Render the current icon */}
          </button>
          {/* Thumbs Up/Down Feedback */}
          <button
            onClick={() => handleFeedback('up')}
            className={`p-2 rounded-full ${feedback === 'up' ? 'bg-green-700' : 'bg-gray-300'} hover:bg-green-500 hover:-rotate-45 hover:scale-125 transition-transform duration-200 flex items-center justify-center`}
            aria-label="Thumbs Up"
          >
            {feedback === 'up' ? <HandThumbUpSolid className="w-6 h-6 text-white" /> : <HandThumbUpOutline className="w-6 h-6 text-gray-700" />}
          </button>
          <button
            onClick={() => handleFeedback('down')}
            className={`p-2 rounded-full ${feedback === 'down' ? 'bg-red-800' : 'bg-gray-300'} hover:bg-red-500 hover:-rotate-45 hover:scale-125 transition-transform duration-200 flex items-center justify-center`}
            aria-label="Thumbs Down"
          >
            {feedback === 'down' ? <HandThumbDownSolid className="w-6 h-6 text-white" /> : <HandThumbDownOutline className="w-6 h-6 text-gray-700" />}
          </button>
        </div>
      )}
      {showFeedbackPopup && (
        <div className="mt-2 p-2 bg-custombg2 rounded-lg shadow-lg">
          <textarea
            className="w-full p-2 border rounded-md bg-custombg"
            rows="3"
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            placeholder="(Optional) Tell us more about your feedback..."
          ></textarea>
          <button
            onClick={handleFeedbackSubmit}
            style={{ backgroundColor: "#2f28909c" }}
            className="mt-2 text-white px-4 py-2 rounded-md hover:text-customtxt hover:scale-105 transition-transform duration-200"
          >
            Submit Feedback
          </button>
        </div>
      )}
      {selectedImage && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50" onClick={closeImagePopup}>
          <img src={selectedImage} alt="Selected" className="max-w-[80%] max-h-[80%] rounded-lg" />
        </div>
      )}
    </motion.div>
  );
}

export default ChatMessage;
