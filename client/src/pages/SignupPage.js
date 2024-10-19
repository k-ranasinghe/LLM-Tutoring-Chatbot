import Header from '../components/Header';
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

function SignUpPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [dateOfBirth, setDateOfBirth] = useState('');
    const [name, setName] = useState('');
    const [phoneNumber, setPhoneNumber] = useState('');
    const [isPasswordMatch, setIsPasswordMatch] = useState(true);
    const [buttonColor, setButtonColor] = useState("#4038be99");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            setIsPasswordMatch(false);
            return;
        }
        const formattedDateOfBirth = dateOfBirth ? dateOfBirth.toISOString().split('T')[0] : '';

        const formData = { email, password, dateOfBirth: formattedDateOfBirth, name, phoneNumber };

        try {
            const response = await fetch('http://127.0.0.1:8000/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });

            const result = await response.json();
            if (!result.success) {
                // Handle registration error
                console.error("Registration failed", result.message);
            } else {
                // Redirect to login on successful registration
                navigate("/login");
            }
        } catch (error) {
            console.error("Registration error", error);
        }
    };

    return (
        <>
        <div className="flex flex-col h-screen">
            <Header isAdmin={false} className="h-16" />
            <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8 -mt-20">
                <div className="sm:mx-auto sm:w-full sm:max-w-sm">
                    <h2 className="mt-10 text-center text-5xl font-bold leading-9 tracking-tight text-customtxt">
                        Create Account
                    </h2>
                </div>

                <div className="mt-4 sm:mx-auto sm:w-full sm:max-w-sm">
                    <form className="space-y-6" onSubmit={handleSubmit}>
                    <div>
                            <label htmlFor="name" className="block text-sm font-medium leading-6 text-customtxt">
                                Name
                            </label>
                            <div>
                                <input
                                    id="name"
                                    name="name"
                                    type="text"
                                    required
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    className="block w-full h-8 rounded-md py-1.5 px-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="phoneNumber" className="block text-sm font-medium leading-6 text-customtxt">
                                Phone Number
                            </label>
                            <div>
                                <input
                                    id="phoneNumber"
                                    name="phoneNumber"
                                    type="tel"
                                    required
                                    value={phoneNumber}
                                    onChange={(e) => setPhoneNumber(e.target.value)}
                                    className="block w-full h-8 rounded-md py-1.5 px-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                />
                            </div>
                        </div>
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium leading-6 text-customtxt">
                                Email Address
                            </label>
                            <div>
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    autoComplete="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="block w-full h-8 rounded-md py-1.5 px-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-medium leading-6 text-customtxt">
                                Password
                            </label>
                            <div>
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="block w-full h-8 rounded-md py-1.5 px-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="confirmPassword" className="block text-sm font-medium leading-6 text-customtxt">
                                Confirm Password
                            </label>
                            <div>
                                <input
                                    id="confirmPassword"
                                    name="confirmPassword"
                                    type="password"
                                    required
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    className="block w-full h-8 rounded-md py-1.5 px-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                />
                            </div>
                            {!isPasswordMatch && (
                                <p className="mt-2 text-sm text-red-500">Passwords do not match</p>
                            )}
                        </div>

                        <div>
                            <label htmlFor="dateOfBirth" className="block text-sm font-medium leading-6 text-customtxt">
                                Date of Birth
                            </label>
                            <div>
                                <DatePicker
                                    selected={dateOfBirth}
                                    onChange={(date) => setDateOfBirth(date)}
                                    className="block w-full h-8 rounded-md py-1.5 px-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                    dateFormat="yyyy-MM-dd"
                                    placeholderText="Select a date"
                                    required
                                    showYearDropdown
                                    yearDropdownItemNumber={50}
                                    scrollableYearDropdown
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
                                Sign Up
                            </button>
                        </div>
                    </form>

                    <p className="mt-10 text-center text-sm text-gray-500">
                        Already have an account?{" "}
                        <a href="/login" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
                            Sign in here
                        </a>
                    </p>
                </div>
            </div>
        </div>
        </>
    );
}

export default SignUpPage;
