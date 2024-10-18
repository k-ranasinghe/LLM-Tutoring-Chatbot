import Login from "../components/Login";
import Header from '../components/Header';

const LoginPage = () => {
  return (
    <div>
      <Header isAdmin={false} />
      <Login />
    </div>
  );
};

export default LoginPage;
