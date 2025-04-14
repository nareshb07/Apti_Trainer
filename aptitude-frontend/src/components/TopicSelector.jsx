import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import API from '../api';
import { useTrainer } from '../context/TrainerContext'; 
import '../index.css';

const TopicSelector = () => {
  const [topics, setTopics] = useState([]);
  const { setSelectedTopic } = useTrainer();
  const navigate = useNavigate();
//   const [loading, setLoading] = useState(false);

  useEffect(() => {
    API.get('/topics/')
      .then((res) => setTopics(res.data))
      .catch((err) => console.error('Failed to fetch Topics', err));
  }, []);
//   if (loading) return <p>Loading topics...</p>;
  const handleSelect = (topic) => {
    setSelectedTopic(topic); // ✅ Using context to set it globally
    navigate('/level');      // ✅ Navigate to level selection
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
    <h2 className="text-xl font-bold mb-4">Select a Topic</h2>
    <ul className="space-y-2">
      {topics.map((topic) => (
        <li key={topic.id}>
          <button
            onClick={() => handleSelect(topic)}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded transition duration-200"
          >
            {topic.name}
          </button>
        </li>
      ))}
    </ul>
  </div>
  
  );
};

export default TopicSelector;
