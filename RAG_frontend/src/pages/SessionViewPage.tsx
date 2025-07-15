import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

interface Session {
    session_id: string;
    user_id: number;
    start_time: string;
    end_time: string | null;
    rag_config: Record<string, any>;
}

const SessionViewPage: React.FC = () => {
    const { sessionId } = useParams<{ sessionId: string }>();
    const [session, setSession] = useState<Session | null>(null);
    const [message, setMessage] = useState('');

    useEffect(() => {
        const fetchSession = async () => {
            try {
                if (sessionId) {
                    const response = await axios.get<Session>(`http://localhost:8000/sessions/${sessionId}`);
                    setSession(response.data);
                }
            } catch (error: any) {
                setMessage(`Error fetching session: ${error.response?.data?.detail || 'Something went wrong'}`);
            }
        };
        fetchSession();
    }, [sessionId]);

    if (!session) {
        return <div className="p-4">Loading session details...</div>;
    }

    return (
        <div className="p-4 border rounded shadow-md bg-white">
            <h1 className="text-3xl font-bold mb-4">Session Details</h1>
            {message && <p className="mb-4 text-sm text-center text-red-500">{message}</p>}
            <p><strong>Session ID:</strong> {session.session_id}</p>
            <p><strong>User ID:</strong> {session.user_id}</p>
            <p><strong>Start Time:</strong> {new Date(session.start_time).toLocaleString()}</p>
            <p><strong>End Time:</strong> {session.end_time ? new Date(session.end_time).toLocaleString() : 'N/A'}</p>
            <p><strong>RAG Config:</strong> {JSON.stringify(session.rag_config, null, 2)}</p>
        </div>
    );
};

export default SessionViewPage;
