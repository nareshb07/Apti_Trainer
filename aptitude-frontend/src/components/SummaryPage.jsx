import { useTrainer } from '../context/TrainerContext';
import '../index.css';
import { useNavigate } from 'react-router-dom';

const SummaryPage = () => {
  const { selectedTopic, selectedLevel } = useTrainer();
  const navigate = useNavigate();

  const handleStartTutorial = () => {
    // Start with the first part (order=1)
    navigate(`/tutorial/1`); 
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">🎯 You chose:</h2>
      <div className="mb-6 space-y-2">
        <p className="text-lg">
          <span className="font-medium">Topic:</span> {selectedTopic?.name}
        </p>
        <p className="text-lg">
          <span className="font-medium">Level:</span> {selectedLevel?.name}
        </p>
      </div>

      <div className="flex flex-col space-y-3">
        <button
          className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded transition duration-200"
          onClick={handleStartTutorial}
        >
          Start Tutorial
        </button>
        <button
          className="bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded transition duration-200"
          onClick={() => navigate('/questions')}
        >
          Jump to Practice Questions
        </button>
      </div>
    </div>
  );
};

export default SummaryPage;