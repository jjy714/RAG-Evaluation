import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import EvaluationHistory from '../components/EvaluationHistory';
import BenchmarkList from '../components/BenchmarkList';
import MetricList from '../components/MetricList';

const HomePage: React.FC = () => {
  return (
    <div className="flex flex-col min-h-screen bg-gray-100">
      <Header />
      <main className="flex-grow container mx-auto p-4 sm:p-6 lg:p-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <EvaluationHistory />
          </div>
          <div className="space-y-6">
            <BenchmarkList />
            <MetricList />
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default HomePage;