import Login from "../components/Login";
import Header from '../components/Header';

const LoginPage = () => {
  return (
    <div>
      <Header navItem={null} isAdmin={false} />
      <Login />
    </div>
  );
};

export default LoginPage;
