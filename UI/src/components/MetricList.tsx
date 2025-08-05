import React from 'react';

const metrics = [
  { id: 1, name: 'Metric X' },
  { id: 2, name: 'Metric Y' },
  { id: 3, name: 'Metric Z' },
];

const MetricList: React.FC = () => {
  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-4">Available Metrics</h2>
      <ul>
        {metrics.map(metric => (
          <li key={metric.id} className="mb-2 p-2 rounded-md bg-gray-100 hover:bg-gray-200 cursor-pointer">
            {metric.name}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default MetricList;
