CREATE DATABASE chatbot;

USE chatbot;

CREATE TABLE Chat_sessions (
    ChatID VARCHAR(255) PRIMARY KEY,
    UserID VARCHAR(255),
    chat_history JSON,
    chat_summary TEXT
);

CREATE TABLE PersonalizationInstructions (
    parameter VARCHAR(50) PRIMARY KEY,
    personalization_type VARCHAR(50),
    instruction TEXT
);

INSERT INTO PersonalizationInstructions (parameter, personalization_type, instruction) VALUES
('type1', 'student_type', "User is aged 10-15. Use simple language and clear examples. Avoid complex terminology. Break down concepts into small, digestible parts. Use analogies related to everyday experiences of this age group. Incorporate interactive elements like simple quizzes or thought experiments."),
('type2', 'student_type', "User is aged 16-18. Use more advanced vocabulary and complex concepts. Encourage critical thinking by asking 'why' and 'how' questions. Relate concepts to real-world applications and potential career paths. Introduce some technical terms, but always explain them."),
('Visual', 'learning_style', "Prefered learning style is visual. Use descriptive language to paint mental pictures. Suggest sketching diagrams or flowcharts. Refer to visual concepts like color, shape, or spatial relationships. Recommend visual learning aids like mind maps or infographics."),
('Verbal', 'learning_style', "Prefered learning style is verbal. Emphasize written and spoken explanations. Suggest summarizing concepts in words. Encourage articulating ideas aloud. Recommend creating acronyms or mnemonic devices for key points."),
('Active', 'learning_style', "Prefered learning style is active. Propose hands-on coding exercises or algorithm simulations. Suggest role-playing different parts of a system or algorithm. Encourage implementing concepts in a preferred programming language."),
('Intuitive', 'learning_style', "Prefered learning style is intuitive. Focus on the 'why' behind concepts. Explore theoretical aspects and potential future developments. Encourage finding connections between different algorithms or data structures. Suggest coming up with novel applications of the concept."),
('Reflective', 'learning_style', "Prefered learning style is reflective. Propose thought experiments. Encourage journaling about learning process. Suggest comparing and contrasting different approaches. Ask open-ended questions that require deep contemplation."),
('Textbook', 'communication_format', "Prefered communication format is textbook. Use formal language and structure. Define all technical terms. Provide step-by-step explanations. Include 'Key Points' summaries. Suggest practice problems or exercises."),
('Layman', 'communication_format', "Prefered communication format is layman. Use everyday analogies and real-life examples. Avoid technical jargon, or explain it thoroughly when used. Break complex ideas into simpler components. Use 'imagine if...' scenarios to illustrate points."),
('Storytelling', 'communication_format', "Prefered communication format is storytelling. Create characters or scenarios to illustrate concepts. Develop a narrative arc in explanations. Use cliffhangers or plot twists to maintain engagement. Relate concepts to character's journey or problem-solving."),
('Encouraging', 'tone_style', "Prefered tone style is encouraging. Use phrases like 'Great question!', 'You're on the right track'. Acknowledge effort and progress. Provide positive reinforcement for attempts, not just correct answers. Offer reassurance when concepts are challenging."),
('Neutral', 'tone_style', "Prefered tone style is neutral. Present information without emotional coloring. Use phrases like 'Consider this...', 'One approach is...'. Avoid superlatives or judgment words. Present multiple viewpoints objectively."),
('Informative', 'tone_style', "Prefered tone style is informative. Focus on facts and established knowledge. Use phrases like 'Research shows...', 'In practice,...'. Cite sources or reference well-known experts. Provide context for why the information is relevant."),
('Friendly', 'tone_style', "Prefered tone style is friendly. Use conversational language and personal pronouns. Share anecdotes or personal experiences when relevant. Use humor appropriately. Show empathy with phrases like 'I understand this can be tricky'."),
('Deductive', 'reasoning_framework', "Prefered reasoning framework is deductive. Start with general principles of computer science or mathematics. Guide towards specific applications or examples. Use 'If...then' statements to show logical progression. Encourage deriving specific cases from general rules."),
('Inductive', 'reasoning_framework', "Prefered reasoning framework is inductive. Begin with specific examples or case studies. Guide towards forming general principles or patterns. Use phrases like 'What do you notice about these examples?'. Encourage making predictions based on observed patterns."),
('Abductive', 'reasoning_framework', "Prefered reasoning framework is abductive. Present a 'mystery' or unexplained phenomenon in computing. Encourage generating multiple hypotheses. Guide through evaluating evidence for each hypothesis. Use phrases like 'What's the most likely explanation?'."),
('Analogical', 'reasoning_framework', "Prefered reasoning framework is analogical. Draw parallels between the concept and a familiar system or process. Use phrases like 'This is similar to...'. Encourage finding similarities and differences between the analogy and the actual concept. Guide through applying insights from the analogy to the original problem.");

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


CREATE TABLE Mentor_notes (
	NoteID INT AUTO_INCREMENT PRIMARY KEY,
    MentorID VARCHAR(50) NOT NULL,
    StudentID VARCHAR(50) NOT NULL,
    Course VARCHAR(255),
    Notes TEXT
);

INSERT INTO mentor_notes (mentorid, studentid, course, notes) VALUES 
(
"user789",
"user123", 
'Programming', 
'The student has demonstrated a solid understanding of timing complexities and data structures. We covered various topics including Big O notation, sorting algorithms (bubble sort, merge sort), and basic data structures (arrays, linked lists, and trees). The student has shown good progress in applying these concepts to practical problems and has completed all exercises with a high level of accuracy. However, there is room for improvement in understanding advanced data structures like graphs and hash tables. Additional focus on optimizing code for performance is recommended.'
),
(
"user789",
"user123", 
'3D Design', 
'The student has shown considerable progress in 3D design concepts. We covered a range of topics including basic modeling techniques, texture mapping, and lighting. The student has successfully created several 3D models using various tools and techniques such as extrusion, lofting, and Boolean operations. Their work demonstrates a good understanding of spatial relationships and object composition. However, there is room for improvement in applying advanced rendering techniques and optimizing models for performance. Additional practice with animation and real-time rendering engines would further enhance their skills.'
);


select * from Chat_sessions;
select * from PersonalizationInstructions;
select * from Chat_info;
select * from Mentor_notes;









