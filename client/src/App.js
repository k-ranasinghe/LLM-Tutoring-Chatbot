import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ManageFiles from "./pages/ManageFiles.tsx";
import UploadFiles from "./pages/UploadFiles.tsx";
import MentorNotes from "./pages/MentorNotes.tsx";
import MentorQueries from "./pages/MentorQueries.tsx";
import ChatPage from "./pages/ChatPage";
import SignupPage from "./pages/SignupPage";

function App() {
  return (
      <Router>
        <div className="container">
          <Routes>
            <Route exact path="/" element={<ChatPage />} />
            <Route path="/sign-up" element={<SignupPage />} />
            
            <Route path="/upload" element={<UploadFiles />} /> 
            <Route path="/manage" element={<ManageFiles />} /> 
            <Route path="/notes" element={<MentorNotes />} /> 
            <Route path="/queries" element={<MentorQueries />} /> 
          </Routes>
        </div>
      </Router>
  );
}

export default App;