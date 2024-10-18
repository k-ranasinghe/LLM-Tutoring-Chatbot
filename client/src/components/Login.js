import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Cookies from 'js-cookie';

export default function Login() {
  const [buttonColor, setButtonColor] = useState("#4038be99");
  const [isCorrectPwd, setIsCorrectPwd] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = { email, password };

    try {
      const response = await fetch('http://127.0.0.1:8000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const result = await response.json();
      if (!result.success) {
        setIsCorrectPwd(false); // Show error message if login failed
        alert(result.message);  // Alert with the error message
      } else {
        // Redirect to home on successful login
        Cookies.set('userId', email, { expires: 7 });
        Cookies.set('isAdmin', result.isAdmin, { expires: 7 });
        Cookies.set('showDisclaimer', 'true', result.isAdmin, { expires: 7 });
        if (result.isAdmin) {
          navigate("/upload"); // Redirect to /upload if user is an admin
        } else {
          navigate("/chat", { state: { fromLogin: true } }); // Redirect to /chat if user is not an admin
        }
      }
    } catch (error) {
      console.error("Login error", error);
    }
  };

  return (
    <>
      <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8 mt-20">
        <div className="sm:mx-auto sm:w-full sm:max-w-sm">
          <h2 className="mt-10 text-center text-5xl font-bold leading-9 tracking-tight text-customtxt">
            Welcome Back
          </h2>
        </div>

        <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="block text-sm font-medium leading-6 text-customtxt">
                Email address
              </label>
              <div className="mt-2">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full rounded-md py-1.5 px-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium leading-6 text-customtxt">
                Password
              </label>
              <div className="mt-2">
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full rounded-md py-1.5 px-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                className="flex w-full justify-center rounded-md px-3 py-1.5 text-sm font-semibold text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
                style={{ backgroundColor: buttonColor }}
                onMouseEnter={() => setButtonColor("#4c47a399")}
                onMouseLeave={() => setButtonColor("#4038be99")}
              >
                Sign in
              </button>
            </div>
          </form>

          {isCorrectPwd ? null : (
            <p className="mt-4 text-center text-sm text-red-500">Incorrect Password</p>
          )}

          <p className="mt-10 text-center text-sm text-gray-500">
            Not a member?{" "}
            <a href="/sign-up" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
              Register Now
            </a>
          </p>
        </div>
      </div>
    </>
  );
}
