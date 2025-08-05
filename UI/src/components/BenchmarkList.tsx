import React from 'react';

const benchmarks = [
  { id: 1, name: 'Benchmark A' },
  { id: 2, name: 'Benchmark B' },
  { id: 3, name: 'Benchmark C' },
];

const BenchmarkList: React.FC = () => {
  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-4">Available Benchmarks</h2>
      <ul>
        {benchmarks.map(benchmark => (
          <li key={benchmark.id} className="mb-2 p-2 rounded-md bg-gray-100 hover:bg-gray-200 cursor-pointer">
            {benchmark.name}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default BenchmarkList;
