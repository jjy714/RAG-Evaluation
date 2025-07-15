import React, { useState } from 'react';
import axios from 'axios';

interface SessionCreatorProps {
    userId: number;
}

const SessionCreator: React.FC<SessionCreatorProps> = ({ userId }) => {
    const [message, setMessage] = useState('');

    const handleCreateSession = async () => {
        const ragConfig = {
            retriever: 'hybrid',
            generator: 'gpt-4'
        };
        try {
            const response = await axios.post('http://localhost:8000/sessions/', {
                user_id: userId,
                rag_config: ragConfig,
            });
            setMessage(`Session ${response.data.session_id} created successfully!`);
        } catch (error: any) {
            setMessage(`Error creating session: ${error.response?.data?.detail || 'Something went wrong'}`);
        }
    };

    return (
        <div className="p-4 border rounded shadow-md bg-white">
            <h2 className="text-xl font-semibold mb-4">Create Session</h2>
            <button 
                onClick={handleCreateSession}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
                Start New Session
            </button>
            {message && <p className="mt-4 text-sm text-center">{message}</p>}
        </div>
    );
};

export default SessionCreator;
