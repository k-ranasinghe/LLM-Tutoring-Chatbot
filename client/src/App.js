import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from '@mui/material/styles';
import { Box } from '@mui/material';
import theme from './components/theme.js';
import ManageFiles from "./pages/ManageFiles.tsx";
import UploadFiles from "./pages/UploadFiles.tsx";
import MentorNotes from "./pages/MentorNotes.tsx";
import MentorQueries from "./pages/MentorQueries.tsx";
import ChatPage from "./pages/ChatPage";
import LoginPage from "./pages/LoginPage";
import SignUpPage from "./pages/SignUpPage";

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Box sx={{ bgcolor: 'background.default', minHeight: '100vh' }}>
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />

            <Route path="/chat" element={<ChatPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/sign-up" element={<SignUpPage />} />
            
            <Route path="/upload" element={<UploadFiles />} /> 
            <Route path="/manage" element={<ManageFiles />} /> 
            <Route path="/notes" element={<MentorNotes />} /> 
            <Route path="/queries" element={<MentorQueries />} /> 
          </Routes>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;