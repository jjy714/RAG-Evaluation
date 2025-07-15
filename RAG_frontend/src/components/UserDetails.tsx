import React from 'react';
import axios from 'axios';

interface User {
    id: number;
    username: string;
    email: string;
    role: string;
}

interface UserDetailsProps {
    user: User;
    onPromote: (userId: number) => void;
}

const UserDetails: React.FC<UserDetailsProps> = ({ user, onPromote }) => {
    return (
        <div className="p-4 border rounded shadow-sm mb-4 bg-white">
            <h2 className="text-xl font-semibold">User Details</h2>
            <p><strong>ID:</strong> {user.id}</p>
            <p><strong>Username:</strong> {user.username}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>Role:</strong> {user.role}</p>
            {user.role !== 'admin' && (
                <button 
                    onClick={() => onPromote(user.id)}
                    className="mt-2 bg-green-500 hover:bg-green-700 text-white font-bold py-1 px-3 rounded text-sm"
                >
                    Promote to Admin
                </button>
            )}
        </div>
    );
};

export default UserDetails;
