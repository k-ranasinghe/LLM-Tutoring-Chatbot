import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import ChatPage from "./pages/ChatPage";
import SignupPage from "./pages/SignupPage";

function App() {
  return (
      <Router>
        <div className="container">
          <Routes>
            <Route exact path="/" element={<ChatPage />} />
            {/*<Route path="/about" element={<About />} />*/}
            <Route path="/sign-up" element={<SignupPage />} />
            {/* <Route path="/register" element={<RegisterPage />} /> */}
            {/*<Route path='/dashboard' element={<Dashboard />} />*/}
          </Routes>
        </div>
      </Router>
  );
}

export default App;