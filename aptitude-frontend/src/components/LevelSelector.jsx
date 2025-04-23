import { useTrainer } from '../context/TrainerContext';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../api';
import '../index.css';

const LevelSelector = () => {
  const [levels, setLevels] = useState([]);
  const { setSelectedLevel } = useTrainer();
  const navigate = useNavigate();

  useEffect(() => {
    API.get('/levels/')
      .then((res) => setLevels(res.data))
      .catch((err) => console.error('Failed to fetch levels', err));
  }, []);

  const handleSelect = (level) => {
    setSelectedLevel(level);
    navigate('/topics');
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">Select a Level</h2>
      <ul className="space-y-2">
        {levels.map((level) => (
          <li key={level.id}>
            <button
              onClick={() => handleSelect(level)}
              className="w-full bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded transition duration-200"
            >
              {level.name}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default LevelSelector;
