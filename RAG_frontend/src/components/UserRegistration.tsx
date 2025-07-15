import React, { useState } from 'react';
import axios from 'axios';

const UserRegistration: React.FC = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        try {
            const response = await axios.post('http://localhost:8000/users/', {
                username,
                email,
                password,
            });
            setMessage(`User ${response.data.username} registered successfully!`);
            setUsername('');
            setEmail('');
            setPassword('');
        } catch (error: any) {
            setMessage(`Error: ${error.response?.data?.detail || 'Something went wrong'}`);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded shadow-md">
            <h2 className="text-2xl font-bold mb-4">Register User</h2>
            <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Username:</label>
                <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />
            </div>
            <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Email:</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />
            </div>
            <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Password:</label>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />
            </div>
            <button type="submit" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">Register</button>
            {message && <p className="mt-4 text-sm text-center">{message}</p>}
        </form>
    );
};

export default UserRegistration;
