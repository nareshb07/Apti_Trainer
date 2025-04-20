import TopicSelector from './components/TopicSelector';
import LevelSelector from './components/LevelSelector';
// import SummaryPage from './components/SummaryPage';
import TutorialContent from './components/TutorialContent';

import { Routes, Route, useNavigate } from 'react-router-dom';
import { useTrainer } from './context/TrainerContext';
import Summary from './components/SummaryPage';
import QuestionsPage from './components/QuestionsPage';
import './index.css';




function App() {
  const {selectedTopic} = useTrainer();
  // const [selectedTopic, setSelectedTopic] = useState(null);
  // const [selectedLevel, setSelectedLevel] = useState(null);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">🧠 the Aptitude Trainer</h1>

      <Routes>
        <Route path="/" element={<TopicSelector/>} />
        <Route
          path="/level"
          element={
            selectedTopic ? (
              <LevelSelector/>
            ) : (
              <div>Please select a topic first</div>
            )
          }
        />
        <Route
          path="/summary"
          element={<Summary />}
        />
        {/* // Add this new route to your existing App.js */}
        <Route 
            path="/tutorial/:partOrder"
            element={<TutorialContent />}
        />
        <Route 
          path="/questions"
          element = {<QuestionsPage/>}
          />
      </Routes>
    </div>
  );
}

export default App;