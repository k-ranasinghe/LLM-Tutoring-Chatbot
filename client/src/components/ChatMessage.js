// src/components/ChatMessage.js
import React from 'react';
import { motion } from 'framer-motion';

function ChatMessage({ text, type }) {
  const isUser = type === 'user';
  const messageStyle = isUser ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800';
  const alignment = isUser ? 'self-end' : 'self-start';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`p-4 rounded-lg my-2 max-w-xl ${messageStyle} ${alignment}`}
    >
      {Array.isArray(text) ? (
        <div>
          {text.length > 1 ? (
            <>
              {/* Render header and text elements if more than one item */}
              {text.map((line, index) => (
                <React.Fragment key={index}>
                  {index === 1 && <p className="mt-4 mb-2 text-lg font-semibold">Recommended Resources:</p>}
                  <p className="mb-1">{line}</p>
                </React.Fragment>
              ))}
            </>
          ) : (
            // Render single element normally
            <p>{text[0]}</p>
          )}
        </div>
      ) : (
        <p>{text}</p>
      )}
    </motion.div>
  );
}

export default ChatMessage;
