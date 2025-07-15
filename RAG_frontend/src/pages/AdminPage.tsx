import React, { useEffect, useState } from 'react';
import axios from 'axios';
import UserDetails from '../components/UserDetails';

interface User {
    id: number;
    username: string;
    email: string;
    role: string;
}

const AdminPage: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [message, setMessage] = useState('');

    const fetchUsers = async () => {
        try {
            const response = await axios.get<User[]>('http://localhost:8000/users/');
            setUsers(response.data);
        } catch (error: any) {
            setMessage(`Error fetching users: ${error.response?.data?.detail || 'Something went wrong'}`);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handlePromote = async (userId: number) => {
        try {
            await axios.patch(`http://localhost:8000/users/${userId}/role`, { role: 'admin' });
            setMessage(`User ${userId} promoted to admin successfully!`);
            fetchUsers(); // Re-fetch users to update the list
        } catch (error: any) {
            setMessage(`Error promoting user: ${error.response?.data?.detail || 'Something went wrong'}`);
        }
    };

    return (
        <div className="p-4">
            <h1 className="text-3xl font-bold mb-6">Admin Panel</h1>
            {message && <p className="mb-4 text-sm text-center text-red-500">{message}</p>}
            <div className="mt-8">
                <h2 className="text-2xl font-semibold mb-4">User Management</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {users.map((user) => (
                        <UserDetails key={user.id} user={user} onPromote={handlePromote} />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default AdminPage;
