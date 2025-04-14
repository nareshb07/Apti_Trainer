import { useTrainer } from '../context/TrainerContext';
import '../index.css';
// import { useNavigate } from 'react-router-dom';

// const SummaryPage = () => {
//   const { selectedTopic, selectedLevel } = useTrainer();
//   const navigate = useNavigate();

//   if (!selectedTopic || !selectedLevel) {
//     return <p>Please complete topic and level selection first.</p>;
//   }

//   return (
//     <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md text-center">
//       <h2 className="text-xl font-bold mb-4">🎯 You chose:</h2>
//       <p className="mb-2">🧩 Topic: <strong>{selectedTopic.name}</strong></p>
//       <p className="mb-4">📊 Level: <strong>{selectedLevel.name}</strong></p>

//       <button
//         onClick={() => navigate('/questions')}
//         className="bg-purple-600 text-white px-6 py-2 rounded hover:bg-purple-700 transition"
//       >
//         🚀 Start Practice
//       </button>
//     </div>
//   );
// };



import { useNavigate } from 'react-router-dom';

const SummaryPage = () => {
  const { selectedTopic, selectedLevel } = useTrainer();
  const navigate = useNavigate();

  return (
    <div>
      <h2 className="text-xl font-semibold">🎯 You chose:</h2>
      <p>Topic: {selectedTopic?.name}</p>
      <p>Level: {selectedLevel?.name}</p>

      <button
        className="mt-4 bg-blue-500 text-white px-4 py-2 rounded"
        onClick={() => navigate('/questions')}
      >
        Start Quiz
      </button>
    </div>
  );
};


export default SummaryPage;
