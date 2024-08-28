CREATE DATABASE chatbot;

USE chatbot;

CREATE TABLE chat_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    chat_history JSON,
    chat_summary TEXT
);

CREATE TABLE PersonalizationInstructions (
    parameter VARCHAR(50) PRIMARY KEY,
    personalization_type VARCHAR(50),
    instruction TEXT
);

INSERT INTO PersonalizationInstructions (parameter, personalization_type, instruction) VALUES
('type1', 'student_type', 'User age is 10-15. Provide explanations in simple language with clear examples. Focus on engaging and interactive content to maintain interest.'),
('type2', 'student_type', 'User age is 16-18. Offer more detailed explanations, encouraging critical thinking and problem-solving. Use advanced concepts and real-world applications.'),
('Visual', 'learning_style', 'Incorporate diagrams, charts, and images to explain concepts. Use visual aids and color-coding to enhance understanding.'),
('Verbal', 'learning_style', 'Focus on detailed explanations and word-based information. Encourage reading, writing, and listening activities.'),
('Active', 'learning_style', 'Engage with hands-on activities and problem-solving tasks. Include interactive exercises to involve the learner actively.'),
('Intuitive', 'learning_style', 'Highlight abstract concepts and patterns. Encourage exploring new ideas and looking beyond the obvious solutions.'),
('Reflective', 'learning_style', 'Allow time for thinking and self-assessment. Use reflective questions and activities that promote deep thinking.'),
('Textbook', 'communication_format', 'Present information in a structured and detailed manner. Use formal language and include definitions, examples, and exercises.'),
('Layman', 'communication_format', 'Simplify complex concepts using everyday language. Avoid jargon and use relatable analogies to explain ideas.'),
('Storytelling', 'communication_format', 'Weave information into a narrative. Use characters, plots, and scenarios to make the content more engaging and memorable.'),
('Encouraging', 'tone_style', 'Use positive reinforcement and motivational language. Highlight progress and encourage continuous effort.'),
('Neutral', 'tone_style', 'Provide information in an unbiased and straightforward manner. Avoid emotional language and keep the tone professional.'),
('Informative', 'tone_style', 'Focus on delivering facts and explanations. Ensure clarity and accuracy without adding personal opinions.'),
('Friendly', 'tone_style', 'Use a warm and approachable tone. Engage the reader with casual language and show empathy towards their needs.'),
('Deductive', 'reasoning_framework', 'Start with general principles and apply them to specific cases. Ensure conclusions follow logically from premises.'),
('Inductive', 'reasoning_framework', 'Use specific examples to build general conclusions. Highlight patterns and trends to support the reasoning.'),
('Abductive', 'reasoning_framework', 'Explore the most likely explanation based on available evidence. Consider multiple possibilities and narrow down to the best hypothesis.'),
('Analogical', 'reasoning_framework', 'Draw comparisons between similar situations to explain concepts. Use analogies to illustrate relationships and outcomes.');

CREATE TABLE Chat_info (
    ChatID VARCHAR(50) PRIMARY KEY,
    Chat_title VARCHAR(50),
    Student_type ENUM('type1', 'type2'),
    Learning_style ENUM('Visual', 'Verbal', 'Active', 'Intuitive', 'Reflective'),
    Communication_format ENUM('Textbook', 'Layman', 'Storytelling'),
    Tone_style ENUM('Encouraging', 'Neutral', 'Informative', 'Friendly'),
    Reasoning_framework ENUM('Deductive', 'Inductive', 'Abductive', 'Analogical')
);

INSERT INTO Chat_info (ChatID, Chat_title, Student_type, Learning_style, Communication_format, Tone_style, Reasoning_framework)
VALUES ('abc1', 'Introduction to Python', 'type2', 'Intuitive', 'Storytelling', 'Neutral', 'Abductive');


select * from chat_info;