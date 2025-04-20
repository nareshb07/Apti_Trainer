import { useEffect, useState } from 'react';
import { useTrainer } from '../context/TrainerContext';
import API from '../api';
import { useNavigate, useParams } from 'react-router-dom';
import '../index.css';

const TutorialContent = () => {
    const { selectedTopic, selectedLevel } = useTrainer();
    const { partOrder } = useParams();
    const [tutorial, setTutorial] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchTutorial = async () => {
            try {
                setLoading(true);
                const response = await API.post('/generate_tutorial_content/', {
                    topic_id: selectedTopic.id,
                    level_id: selectedLevel.id,
                    part_order: partOrder
                });
                setTutorial(response.data);
            } catch (err) {
                setError(err.response?.data?.error || 'Failed to load tutorial');
            } finally {
                setLoading(false);
            }
        };

        if (selectedTopic && selectedLevel && partOrder) {
            fetchTutorial();
        } else {
            navigate('/');
        }
    }, [selectedTopic, selectedLevel, partOrder, navigate]);

    if (loading) return <div className="text-center py-8">Generating tutorial content...</div>;
    if (error) return <div className="text-red-500 p-4">{error}</div>;

    return (
        <div className="max-w-4xl mx-auto p-6">
            <div className="mb-6">
                <h1 className="text-2xl font-bold mb-2">{tutorial.topic} - {tutorial.level}</h1>
                <h2 className="text-xl font-semibold text-blue-600">{tutorial.part_title}</h2>
            </div>
            
            <div className="prose max-w-none bg-white p-6 rounded-lg shadow-md">
                <div dangerouslySetInnerHTML={{ __html: tutorial.content.replace(/\n/g, '<br />') }} />
            </div>

            <div className="mt-6 flex space-x-4">
                <button 
                    onClick={() => navigate(-1)}
                    className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
                >
                    Back
                </button>
                <button 
                    onClick={() => navigate('/questions')}
                    className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded"
                >
                    Practice Questions
                </button>
            </div>
        </div>
    );
};

export default TutorialContent;