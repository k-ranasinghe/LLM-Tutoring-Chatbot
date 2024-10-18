import React, { useState } from 'react';

const slides = [
    {
        title: "Welcome to Obo Tutor",
        content: (
            <>
                <p className="text-sm text-left">The chatbot is currently in the <strong>testing phase</strong>. We encourage you to explore all available features to check for any issues. Here are some key functionalities:</p>
                <ul className="list-disc list-inside mb-4 text-left space-y-1">
                    <li><strong>Side Panel:</strong> View your previous chats and adjust chat personalization parameters. Feel free to play around with these settings to see how the chatbot responds.</li>
                    <li><strong>Voice Feature:</strong> You can send voice messages to the chatbot and also have it speak its responses. Just click the button on the message to hear it!</li>
                    <li><strong>File Attachments:</strong> The chatbot supports attachments for many file types, including images, audio, and video. Feel free to try it out!</li>
                    <li><strong>Recommended Resources:</strong> After each response, the chatbot may suggest related links from the web and YouTube. Additionally, the related work section will show images from the knowledge base relevant to your queries.</li>
                </ul>
                <p className="font-semibold text-center text-sm">We encourage you to try out all of these features!</p>
            </>
        ),
    },
    {
        title: "Knowledge Base Coverage",
        content: (
            <>
                <p className="text-sm text-left">This chatbot is equipped with a <strong>Custom Knowledge Base</strong> that covers fundamentals of the subjects:</p>
                <ul className="list-disc list-inside mb-4 text-left">
                    <li>Programming</li>
                    <li>Electronics</li>
                    <li>Embedded Systems</li>
                </ul>
                <p className="text-sm text-left mb-4">Ask questions from these topics to see how well the chatbot is able to answer your queries. If you ask questions outside of these areas, the chatbot will try to refrain from providing answers. We encourage you to test this functionality by asking <strong>out-of-scope questions</strong> to see how effectively it handles them!</p>
                <p className="text-sm text-left">When the chatbot handles out of context questions they are forwarded to <strong>Mentors</strong> who would answer on behalf of the chatbot. You can view their responses via the <strong>Notiffication Panel</strong> from the button on the bottom right corner.</p>
            </>
        ),
    },
    {
        title: "Providing Feedback",
        content: (
            <>
                <p className="text-sm text-left">At the end of each chatbot message, you'll find <strong>Thumbs Up</strong> and <strong>Thumbs Down</strong> buttons.</p>
                <p className="text-sm text-left">You can provide feedback on that specific response and even include an optional description. This feedback plays a crucial role in enhancing the chatbot's performance by:</p>
                <ul className="list-disc list-inside mb-4 text-left">
                    <li>Submitting it to a <strong>LLM</strong> model for analysis</li>
                    <li>Generating instructions tailored for your interactions with the chatbot</li>
                </ul>
                <p className="text-sm text-left mb-4">These generated instructions will be given to model when you use it the next time. These instructions are stored with respect to the user, hence the feedback you provide will be used to enhance your user experience only. The <strong>Administrators</strong> can go through the feedback and decide which of them needs to be provided to the model globally.</p>
                <p className="font-semibold text-sm text-left">Your feedback is essential for improving the chatbot, so we encourage you to use this feature as much as possible!</p>
            </>
        ),
    },
    {
        title: "Data Safety and Transparency",
        content: (
            <>
                <p className="text-sm text-left">We are committed to safeguarding your data privacy. The information we collect includes:</p>
                <ul className="list-disc list-inside mb-4 text-left">
                    <li><strong>Email:</strong> Used as your unique ID within the system.</li>
                    <li><strong>Date of Birth:</strong> Utilized to set your user type, allowing us to customize your experience based on age.</li>
                    <li><strong>Phone Number:</strong> Required for access to our WhatsApp bot, which is available for use as well. Only registered phone numbers can access the chatbot via WhatsApp.</li>
                </ul>
                <p className="font-semibold text-sm text-left">Important Note:</p>
                <p className="text-sm text-left">The WhatsApp bot is live, but due to API limitations, we cannot provide open access to all users. If you're interested in trying this feature, please reach out to us!</p>
            </>
        ),
    },
];

function Disclaimer({ onClose }) {
    const [currentSlide, setCurrentSlide] = useState(0);

    const goToSlide = (index) => {
        setCurrentSlide(index);
    };

    return (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-70">
            <div className="bg-white p-6 rounded-lg shadow-lg max-w-xl text-center">
                <h1 className="text-3xl font-bold mb-4">
                    Disclaimer
                </h1>
                <h2 className="text-lg font-bold mb-4">
                    {slides[currentSlide].title}
                </h2>
                <div className="mb-4 h-96 overflow-y-auto"> {/* Fixed height with overflow */}
                    {slides[currentSlide].content}
                </div>

                <div className="mt-4">
                    {slides.map((_, index) => (
                        <span
                            key={index}
                            onClick={() => goToSlide(index)}
                            className={`inline-block w-2 h-2 rounded-full cursor-pointer ${index === currentSlide ? 'bg-blue-600' : 'bg-gray-400'} mx-1`}
                        />
                    ))}
                </div>

                <button
                    onClick={onClose}
                    className="mt-6 bg-gray-300 text-gray-700 font-bold px-4 py-2 rounded-xl hover:bg-gray-400 hover:text-sky-700 hover:scale-110 transition duration-200"
                >
                    Close
                </button>
            </div>
        </div>
    );
}

export default Disclaimer;
