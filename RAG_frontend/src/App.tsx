import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegistrationPage from './pages/RegistrationPage';
import DashboardPage from './pages/DashboardPage';
import SessionViewPage from './pages/SessionViewPage';
import AdminPage from './pages/AdminPage';

function App() {
    return (
        <Router>
            <div className="bg-gray-100 min-h-screen">
                <nav className="bg-white shadow-md">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div className="flex items-center justify-between h-16">
                            <div className="flex items-center">
                                <Link to="/" className="text-2xl font-bold text-gray-800">RAG-Eval</Link>
                            </div>
                            <div className="flex space-x-4">
                                <Link to="/" className="text-gray-600 hover:text-gray-800">Home</Link>
                                <Link to="/login" className="text-gray-600 hover:text-gray-800">Login</Link>
                                <Link to="/register" className="text-gray-600 hover:text-gray-800">Register</Link>
                                <Link to="/dashboard" className="text-gray-600 hover:text-gray-800">Dashboard</Link>
                                <Link to="/admin" className="text-gray-600 hover:text-gray-800">Admin</Link>
                            </div>
                        </div>
                    </div>
                </nav>
                <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                    <Routes>
                        <Route path="/" element={<HomePage />} />
                        <Route path="/login" element={<LoginPage />} />
                        <Route path="/register" element={<RegistrationPage />} />
                        <Route path="/dashboard" element={<DashboardPage />} />
                        <Route path="/session/:sessionId" element={<SessionViewPage />} />
                        <Route path="/admin" element={<AdminPage />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
