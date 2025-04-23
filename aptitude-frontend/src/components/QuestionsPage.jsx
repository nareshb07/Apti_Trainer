// import { useTrainer } from '../context/TrainerContext';
// import { useEffect, useState } from 'react';
// import { useNavigate } from 'react-router-dom';
// import API from '../api';
// import { Loader2, CheckCircle, XCircle } from 'lucide-react';

// const QuestionsPage = () => {
//   const { selectedTopic, selectedLevel } = useTrainer();
//   const [tutorial, setTutorial] = useState([]);
//   const [questions, setQuestions] = useState([]);
//   const [tutorialStep, setTutorialStep] = useState(0);
//   const [showQuestions, setShowQuestions] = useState(false);
//   const [selectedAnswers, setSelectedAnswers] = useState({});
//   const [showAnswers, setShowAnswers] = useState(false);
//   const [loading, setLoading] = useState(true);
//   const [currentQuestion, setCurrentQuestion] = useState(0);
//   const navigate = useNavigate();

//   useEffect(() => {
//     if (!selectedTopic || !selectedLevel) {
//       navigate('/');
//       return;
//     }

//     const fetchTutorialAndQuestions = async () => {
//       try {
//         const res = await API.post('http://localhost:8000/api/generate-tutorial-and-questions/', {
//           topic: selectedTopic.name,
//           level: selectedLevel.name,
//         });
//         setTutorial(res.data.tutorial || []);
//         setQuestions(res.data.questions || []);
//       } catch (error) {
//         console.error("Failed to fetch data:", error);
//       } finally {
//         setLoading(false);
//       }
//     };

//     fetchTutorialAndQuestions();
//   }, [selectedTopic, selectedLevel, navigate]);

//   if (loading) {
//     return (
//       <div className="min-h-screen flex items-center justify-center text-xl text-white bg-black">
//         <Loader2 className="animate-spin w-8 h-8 mr-2 text-cyan-400" /> Loading...
//       </div>
//     );
//   }

//   if (!showQuestions && tutorial.length > 0) {
//     const part = tutorial[tutorialStep];

//     return (
//       <div className="min-h-screen bg-black text-white p-6">
//         <div className="max-w-3xl mx-auto">
//           <h2 className="text-2xl text-cyan-400 font-bold mb-4">📘 Tutorial: {part.title}</h2>
//           <p className="text-lg text-gray-200 mb-6 whitespace-pre-line">{part.content}</p>

//           <div className="flex justify-between">
//             <button
//               onClick={() => setTutorialStep(prev => Math.max(prev - 1, 0))}
//               disabled={tutorialStep === 0}
//               className="px-5 py-2 rounded-full bg-gray-700 disabled:opacity-50"
//             >
//               ⬅️ Prev
//             </button>
//             {tutorialStep === tutorial.length - 1 ? (
//               <button
//                 onClick={() => setShowQuestions(true)}
//                 className="px-6 py-3 bg-cyan-600 text-white font-semibold rounded-full"
//               >
//                 Start Questions ➡️
//               </button>
//             ) : (
//               <button
//                 onClick={() => setTutorialStep(prev => prev + 1)}
//                 className="px-5 py-2 rounded-full bg-cyan-600"
//               >
//                 Next ➡️
//               </button>
//             )}
//           </div>
//         </div>
//       </div>
//     );
//   }

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black text-white p-6">
//       <div className="max-w-4xl mx-auto">
//         <div className="flex justify-between items-center mb-6">
//           <h2 className="text-2xl font-bold text-cyan-400">🎯 {selectedTopic?.name} - {selectedLevel?.name}</h2>
//           <span className="text-gray-400">{currentQuestion + 1} / {questions?.length || 0}</span>
//         </div>

//         <div className="bg-gray-900 p-8 rounded-3xl shadow-xl">
//           <p className="text-xl font-semibold mb-6 leading-relaxed">{q?.question}</p>

//           <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
//             {Object.entries(q?.options || {}).map(([key, value]) => {
//               const keyNum = parseInt(key);
//               const isSelected = selected == keyNum;
//               const isCorrect = keyNum === correctIndex;

//               let buttonStyle = "w-full px-5 py-3 rounded-xl border font-medium transition duration-200 text-left flex items-center gap-2";

//               if (showAnswers) {
//                 if (isCorrect) {
//                   buttonStyle += isSelected
//                     ? " bg-green-500 text-white border-green-600"
//                     : " bg-green-700 text-white border-green-600";
//                 } else if (isSelected) {
//                   buttonStyle += " bg-red-500 text-white border-red-600";
//                 } else {
//                   buttonStyle += " bg-gray-800 text-white border-gray-700";
//                 }
//               } else {
//                 buttonStyle += isSelected
//                   ? " bg-cyan-500 text-white border-cyan-600"
//                   : " bg-gray-800 hover:bg-gray-700 border-gray-700";
//               }

//               return (
//                 <button
//                   key={key}
//                   onClick={() => !showAnswers && handleOptionSelect(currentQuestion, keyNum)}
//                   className={buttonStyle}
//                 >
//                   <span className="flex-1">{value}</span>
//                   {showAnswers && isCorrect && <CheckCircle className="w-5 h-5" />}
//                   {showAnswers && !isCorrect && isSelected && <XCircle className="w-5 h-5" />}
//                 </button>
//               );
//             })}
//           </div>

//           {showAnswers && (
//             <div className="mt-5">
//               <p className="text-sm text-slate-400 mt-1">💡 Explanation: {q.explanation}</p>
//               <p className="text-xs text-gray-500 mt-3">
//                 Correct answer: {q.options?.[correctIndex] || q.answer}
//               </p>
//             </div>
//           )}
//         </div>

//         <div className="mt-8 flex justify-between items-center">
//           <button
//             onClick={handlePrev}
//             disabled={currentQuestion === 0}
//             className="px-5 py-2 rounded-full bg-gray-700 hover:bg-gray-600 disabled:opacity-40"
//           >
//             ⬅️ Prev
//           </button>

//           {currentQuestion === questions.length - 1 && !showAnswers && (
//             <button
//               onClick={handleSubmit}
//               className="px-8 py-3 bg-cyan-600 hover:bg-cyan-700 text-white rounded-full text-lg font-semibold shadow-lg"
//             >
//               Submit Answers
//             </button>
//           )}

//           <button
//             onClick={handleNext}
//             disabled={currentQuestion === questions.length - 1}
//             className="px-5 py-2 rounded-full bg-gray-700 hover:bg-gray-600 disabled:opacity-40"
//           >
//             Next ➡️
//           </button>
//         </div>

//         {!showAnswers && (
//           <p className="text-sm text-slate-500 mt-4 text-center italic">
//             Answer all to submit. You can navigate using Next/Prev.
//           </p>
//         )}
//       </div>
//     </div>
//   );
// };

// export default QuestionsPage;

// -----------------------------------------------------------


import { useTrainer } from '../context/TrainerContext';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../api';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';

const QuestionsPage = () => {
  const { selectedTopic, selectedLevel } = useTrainer();
  const [tutorialPart, setTutorialPart] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentPartIndex, setCurrentPartIndex] = useState(0);
  const [showQuestions, setShowQuestions] = useState(false);
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

    const fetchTutorial = async () => {
      try {
        setLoading(true);
        const res = await API.post(`/fetch_tutorial_prompt/`, {
          params: {
            topic: selectedTopic.name,
            level: selectedLevel.name,
            order: currentPartIndex + 1,
          },
        });
        if (res.data?.tutorial) {
          setTutorialPart(res.data.tutorial);
          setShowQuestions(false);
        } else {
          // All tutorials completed
          setTutorialPart(null);
          setQuestions([]);
        }
      } catch (error) {
        console.error("Failed to fetch tutorial part:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchTutorial();
  }, [currentPartIndex, selectedTopic, selectedLevel, navigate]);

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      const res = await API.post('/generate-questions/', {
        topic: selectedTopic.name,
        level: selectedLevel.name,
        tutorial_part: tutorialPart?.part_title,
      });
      setQuestions(res.data.questions || []);
      setShowQuestions(true);
    } catch (error) {
      console.error("Failed to fetch questions:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleOptionSelect = (qIndex, optionKey) => {
    setSelectedAnswers(prev => ({ ...prev, [qIndex]: optionKey }));
  };

  const handleSubmitAnswers = () => {
    if (Object.keys(selectedAnswers).length !== questions.length) {
      alert("Please answer all questions before submitting.");
      return;
    }
    setShowAnswers(true);
  };

  const goToNextTutorial = () => {
    setCurrentPartIndex(prev => prev + 1);
    setQuestions([]);
    setSelectedAnswers({});
    setShowAnswers(false);
    setCurrentQuestion(0);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-xl text-white bg-black">
        <Loader2 className="animate-spin w-8 h-8 mr-2 text-cyan-400" /> Loading...
      </div>
    );
  }

  if (!tutorialPart && questions.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center text-white text-xl bg-black">
        🎉 All tutorials completed for this topic and level!
      </div>
    );
  }

  // Tutorial Part View
  if (!showQuestions) {
    return (
      <div className="min-h-screen bg-black text-white p-6 flex flex-col items-center justify-center">
        <div className="max-w-2xl bg-gray-900 p-8 rounded-3xl shadow-xl">
          <h2 className="text-2xl font-bold mb-4 text-cyan-400">📚 {tutorialPart?.part_title}</h2>
          <p className="text-lg whitespace-pre-line leading-relaxed">{tutorialPart?.content}</p>
          <button
            onClick={fetchQuestions}
            className="mt-6 bg-cyan-600 hover:bg-cyan-700 px-6 py-3 rounded-full font-semibold text-white shadow-md"
          >
            Continue to Questions ➡️
          </button>
        </div>
      </div>
    );
  }

  // Questions View
  const q = questions[currentQuestion] || {};
  const selected = selectedAnswers[currentQuestion];
  const correctIndex = { A: 0, B: 1, C: 2, D: 3 }[q.answer?.toUpperCase()];

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black text-white p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-cyan-400">{selectedTopic?.name} - {selectedLevel?.name}</h2>
          <span className="text-gray-400">{currentQuestion + 1} / {questions?.length}</span>
        </div>

        <div className="bg-gray-900 p-8 rounded-3xl shadow-xl">
          <p className="text-xl font-semibold mb-6 leading-relaxed">{q?.question}</p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {Object.entries(q?.options || {}).map(([key, value], idx) => {
              const isSelected = selected == idx;
              const isCorrect = idx === correctIndex;

              let btnClass = "w-full px-5 py-3 rounded-xl border font-medium transition duration-200 text-left flex items-center gap-2";
              if (showAnswers) {
                if (isCorrect) {
                  btnClass += isSelected ? " bg-green-500" : " bg-green-700";
                } else if (isSelected) {
                  btnClass += " bg-red-500";
                } else {
                  btnClass += " bg-gray-800";
                }
              } else {
                btnClass += isSelected ? " bg-cyan-500" : " bg-gray-800 hover:bg-gray-700";
              }

              return (
                <button
                  key={key}
                  onClick={() => !showAnswers && handleOptionSelect(currentQuestion, idx)}
                  className={btnClass}
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
              <p className="text-sm text-slate-400">💡 Explanation: {q.explanation}</p>
            </div>
          )}
        </div>

        <div className="mt-8 flex justify-between items-center">
          <button
            onClick={() => setCurrentQuestion(q => Math.max(0, q - 1))}
            disabled={currentQuestion === 0}
            className="px-5 py-2 rounded-full bg-gray-700 hover:bg-gray-600 disabled:opacity-40"
          >
            ⬅️ Prev
          </button>

          {currentQuestion === questions.length - 1 && !showAnswers && (
            <button
              onClick={handleSubmitAnswers}
              className="px-8 py-3 bg-cyan-600 hover:bg-cyan-700 text-white rounded-full text-lg font-semibold shadow-lg"
            >
              Submit Answers
            </button>
          )}

          <button
            onClick={() => setCurrentQuestion(q => Math.min(questions.length - 1, q + 1))}
            disabled={currentQuestion === questions.length - 1}
            className="px-5 py-2 rounded-full bg-gray-700 hover:bg-gray-600 disabled:opacity-40"
          >
            Next ➡️
          </button>
        </div>

        {showAnswers && (
          <div className="flex justify-center mt-8">
            <button
              onClick={goToNextTutorial}
              className="bg-cyan-500 hover:bg-cyan-600 text-white px-8 py-3 rounded-full font-bold shadow-md"
            >
              Continue to Next Tutorial
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuestionsPage;


