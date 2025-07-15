import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import SessionCreator from '../components/SessionCreator';

interface Session {
    session_id: string;
    user_id: number;
    start_time: string;
    end_time: string | null;
    rag_config: Record<string, any>;
}

const DashboardPage: React.FC = () => {
    // In a real app, this userId would come from an authentication context
    const userId = 1; 
    const [sessions, setSessions] = useState<Session[]>([]);
    const [message, setMessage] = useState('');

    const fetchSessions = async () => {
        try {
            // Assuming an endpoint to get sessions by user ID or all sessions for now
            // For simplicity, let's assume we can fetch all sessions and filter by userId on the frontend
            // In a real app, you'd have a backend endpoint like /users/{userId}/sessions
            const response = await axios.get<Session[]>('http://localhost:8000/sessions/'); // This endpoint doesn't exist yet, will need to add it
            setSessions(response.data.filter(session => session.user_id === userId));
        } catch (error: any) {
            setMessage(`Error fetching sessions: ${error.response?.data?.detail || 'Something went wrong'}`);
        }
    };

    useEffect(() => {
        fetchSessions();
    }, []);

    return (
        <div className="p-4">
            <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
            <p className="mt-2 mb-4">Welcome, User {userId}!</p>
            {message && <p className="mb-4 text-sm text-center text-red-500">{message}</p>}
            
            <div className="mb-8">
                <SessionCreator userId={userId} />
            </div>

            <h2 className="text-2xl font-semibold mb-4">Your Sessions</h2>
            {sessions.length === 0 ? (
                <p>No sessions found. Start a new one!</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {sessions.map((session) => (
                        <div key={session.session_id} className="p-4 border rounded shadow-sm bg-white">
                            <h3 className="text-lg font-semibold">Session ID: {session.session_id.substring(0, 8)}...</h3>
                            <p>Start Time: {new Date(session.start_time).toLocaleString()}</p>
                            <p>RAG Config: {JSON.stringify(session.rag_config)}</p>
                            <Link 
                                to={`/session/${session.session_id}`}
                                className="mt-2 inline-block bg-purple-500 hover:bg-purple-700 text-white font-bold py-1 px-3 rounded text-sm"
                            >
                                View Details
                            </Link>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default DashboardPage;
