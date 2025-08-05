import React from 'react';

const evaluations = [
  { id: 1, name: 'Evaluation 1', date: '2025-07-14', status: 'Completed' },
  { id: 2, name: 'Evaluation 2', date: '2025-07-15', status: 'In Progress' },
  { id: 3, name: 'Evaluation 3', date: '2025-07-15', status: 'Completed' },
];

const EvaluationHistory: React.FC = () => {
  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-4">Evaluation History</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white">
          <thead className="bg-gray-800 text-white">
            <tr>
              <th className="w-1/3 text-left py-3 px-4 uppercase font-semibold text-sm">Name</th>
              <th className="w-1/3 text-left py-3 px-4 uppercase font-semibold text-sm">Date</th>
              <th className="text-left py-3 px-4 uppercase font-semibold text-sm">Status</th>
            </tr>
          </thead>
          <tbody className="text-gray-700">
            {evaluations.map((evalItem, index) => (
              <tr key={evalItem.id} className={index % 2 === 0 ? 'bg-gray-100' : ''}>
                <td className="w-1/3 text-left py-3 px-4">{evalItem.name}</td>
                <td className="w-1/3 text-left py-3 px-4">{evalItem.date}</td>
                <td className="text-left py-3 px-4">{evalItem.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default EvaluationHistory;
