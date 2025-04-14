import { useTrainer } from '../context/TrainerContext';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../api';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';

const QuestionsPage = () => {
  const { selectedTopic, selectedLevel } = useTrainer();
  const [questions, setQuestions] = useState([]);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showAnswers, setShowAnswers] = useState(false);
  const [loading, setLoading] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    if (!selectedTopic || !selectedLevel) {
      navigate('/');
      return;
    }

    const fetchQuestions = async () => {
      try {
        const res = await API.post('http://localhost:8000/api/generate-questions/', {
          topic: selectedTopic.name,
          level: selectedLevel.name,
        });
        setQuestions(res.data.questions || []);
      } catch (error) {
        console.error("Failed to fetch questions:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, [selectedTopic, selectedLevel, navigate]);

  const handleOptionSelect = (qIndex, optionKey) => {
    setSelectedAnswers(prev => ({ ...prev, [qIndex]: optionKey }));
  };

  const handleSubmit = () => {
    if (Object.keys(selectedAnswers).length !== questions.length) {
      alert("Please answer all questions before submitting.");
      return;
    }
    setShowAnswers(true);
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center text-xl text-white bg-black">
      <Loader2 className="animate-spin w-8 h-8 mr-2 text-cyan-400" /> Loading questions...
    </div>
  );

  if (!questions || !questions.length) {
    return (
      <div className="min-h-screen flex items-center justify-center text-white text-xl bg-black">
        ❌ No questions available. Please try again later.
      </div>
    );
  }

  const q = questions[currentQuestion] || {};
  const selected = selectedAnswers[currentQuestion];

  // Mapping letters to index keys
  const letterToIndex = { A: 0, B: 1, C: 2, D: 3 };
  const correctIndex = letterToIndex[q.answer?.toUpperCase()];

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black text-white p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-cyan-400">🎯 {selectedTopic?.name} - {selectedLevel?.name}</h2>
          <span className="text-gray-400">{currentQuestion + 1} / {questions?.length || 0}</span>
        </div>

        <div className="bg-gray-900 p-8 rounded-3xl shadow-xl">
          <p className="text-xl font-semibold mb-6 leading-relaxed">{q?.question}</p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {Object.entries(q?.options || {}).map(([key, value]) => {
              const keyNum = parseInt(key);
              const isSelected = selected == keyNum;
              const isCorrect = keyNum === correctIndex;

              let buttonStyle = "w-full px-5 py-3 rounded-xl border font-medium transition duration-200 text-left flex items-center gap-2";

              if (showAnswers) {
                if (isCorrect) {
                  buttonStyle += isSelected
                    ? " bg-green-500 text-white border-green-600"
                    : " bg-green-700 text-white border-green-600";
                } else if (isSelected) {
                  buttonStyle += " bg-red-500 text-white border-red-600";
                } else {
                  buttonStyle += " bg-gray-800 text-white border-gray-700";
                }
              } else {
                buttonStyle += isSelected
                  ? " bg-cyan-500 text-white border-cyan-600"
                  : " bg-gray-800 hover:bg-gray-700 border-gray-700";
              }

              return (
                <button
                  key={key}
                  onClick={() => !showAnswers && handleOptionSelect(currentQuestion, keyNum)}
                  className={buttonStyle}
                >
                  <span className="flex-1">{value}</span>
                  {showAnswers && isCorrect && <CheckCircle className="w-5 h-5" />}
                  {showAnswers && !isCorrect && isSelected && <XCircle className="w-5 h-5" />}
                </button>
              );
            })}
          </div>

          {showAnswers && (
            <div className="mt-5">
              <p className="text-sm text-slate-400 mt-1">💡 Explanation: {q.explanation}</p>
              <p className="text-xs text-gray-500 mt-3">
                Correct answer: {q.options?.[correctIndex] || q.answer}
              </p>
            </div>
          )}
        </div>

        <div className="mt-8 flex justify-between items-center">
          <button
            onClick={handlePrev}
            disabled={currentQuestion === 0}
            className="px-5 py-2 rounded-full bg-gray-700 hover:bg-gray-600 disabled:opacity-40"
          >
            ⬅️ Prev
          </button>

          {currentQuestion === questions.length - 1 && !showAnswers && (
            <button
              onClick={handleSubmit}
              className="px-8 py-3 bg-cyan-600 hover:bg-cyan-700 text-white rounded-full text-lg font-semibold shadow-lg"
            >
              Submit Answers
            </button>
          )}

          <button
            onClick={handleNext}
            disabled={currentQuestion === questions.length - 1}
            className="px-5 py-2 rounded-full bg-gray-700 hover:bg-gray-600 disabled:opacity-40"
          >
            Next ➡️
          </button>
        </div>

        {!showAnswers && (
          <p className="text-sm text-slate-500 mt-4 text-center italic">
            Answer all to submit. You can navigate using Next/Prev.
          </p>
        )}
      </div>
    </div>
  );
};

export default QuestionsPage;
