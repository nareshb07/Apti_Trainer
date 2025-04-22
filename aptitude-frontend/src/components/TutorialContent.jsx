// src/components/TutorialContent.js
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTrainer } from '../context/TrainerContext';
import TutorialPart from './TutorialPart'; // Reuse the single part renderer

const TutorialContent = () => {
    const { partOrder } = useParams(); // Get partOrder from URL (string)
    const navigate = useNavigate();
    const {
        tutorialParts,
        isTutorialLoading,
        tutorialError,
        selectedTopic,
        selectedLevel
    } = useTrainer();

    const [currentPart, setCurrentPart] = useState(null);
    const [partIndex, setPartIndex] = useState(-1); // 0-based index
    const totalParts = tutorialParts.length;

    useEffect(() => {
        // Validate partOrder and find the corresponding part
        const orderNum = parseInt(partOrder, 10);
        if (isNaN(orderNum) || !tutorialParts || tutorialParts.length === 0) {
            setCurrentPart(null);
            setPartIndex(-1);
            return;
        }

        // Find part by its 'order' property (which should be 1-based)
        const foundPart = tutorialParts.find(p => p.order === orderNum);
        const foundIndex = tutorialParts.findIndex(p => p.order === orderNum); // Get 0-based index too

        setCurrentPart(foundPart || null);
        setPartIndex(foundIndex);

    }, [partOrder, tutorialParts]); // Rerun when URL param or fetched parts change

    // --- Render Logic ---

    // Handle missing selection upstream
     if (!selectedTopic || !selectedLevel) {
         return (
             <div className="max-w-4xl mx-auto p-4 md:p-6 text-center">
                 <p className="text-lg text-gray-500 mt-10">
                     Please <Link to="/" className="text-blue-600 hover:underline">select a Level and Topic</Link> first.
                 </p>
            </div>
         );
     }

    // Handle Loading State from Context
    if (isTutorialLoading) {
        return (
            <div className="flex justify-center items-center h-40">
                <p className="text-lg text-gray-500 animate-pulse">Loading tutorial content...</p>
            </div>
        );
    }

    // Handle Fetch Error from Context
    if (tutorialError) {
        return (
             <div className="max-w-4xl mx-auto p-4 md:p-6">
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                    <strong className="font-bold">Error loading tutorial: </strong>
                    <span className="block sm:inline">{tutorialError}</span>
                    <p className="mt-2">Please try selecting the topic again.</p>
                </div>
            </div>
        );
    }

    // Handle Invalid partOrder or empty parts after load/no error
    if (!currentPart) {
         // Check if parts array is actually empty vs just invalid partOrder
        if(tutorialParts.length > 0) {
             return (
                 <div className="max-w-4xl mx-auto p-4 md:p-6 text-center">
                     <p className="text-lg text-red-600 mt-10">
                         Invalid tutorial part number: {partOrder}.
                     </p>
                     <Link to={`/tutorial/1`} className="text-blue-600 hover:underline mt-4 inline-block">Go to first part</Link>
                </div>
            );
        } else if (!isTutorialLoading) {
             // Parts array is empty, and not loading, and no error -> likely fetch didn't run or returned empty
             return (
                 <div className="max-w-4xl mx-auto p-4 md:p-6 text-center">
                     <p className="text-lg text-gray-500 mt-10">
                         Tutorial content not found. Please ensure topic and level are selected correctly.
                     </p>
                 </div>
             );
        }
        // If still loading, the loading indicator above handles it. Avoid rendering this briefly during load.
        return null;
    }

    // --- Display Found Part ---
    const isFirstPart = partIndex === 0;
    const isLastPart = partIndex === totalParts - 1;

    const handleNavigate = (direction) => {
        const currentOrder = parseInt(partOrder, 10);
        if (isNaN(currentOrder)) return;

        let nextOrder;
        if (direction === 'next') {
            nextOrder = currentOrder + 1;
        } else {
            nextOrder = currentOrder - 1;
        }

        if (nextOrder > 0 && nextOrder <= totalParts) {
             navigate(`/tutorial/${nextOrder}`);
        } else if (direction === 'next' && isLastPart) {
            // Navigate to questions page after the last part
             navigate('/questions');
        }
    };


    return (
        <div className="max-w-4xl mx-auto p-4 md:p-6 font-sans">
            {/* Optional: Add breadcrumbs or topic title here if needed */}
             <div className="mb-6 text-sm text-gray-500">
                 <Link to="/" className="hover:underline">Levels</Link> &gt;{' '}
                 <Link to="/topics" className="hover:underline">{selectedLevel?.name || 'Topics'}</Link> &gt;{' '}
                 <span className="font-medium text-gray-700">{selectedTopic?.name || 'Tutorial'}</span> - Part {partOrder}/{totalParts}
             </div>

            {/* Render the specific Tutorial Part */}
            <TutorialPart part={currentPart} />

            {/* Navigation Buttons */}
            <div className="mt-8 flex justify-between items-center">
                <button
                    onClick={() => handleNavigate('prev')}
                    disabled={isFirstPart}
                    className={`px-6 py-2 rounded text-white font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                        isFirstPart
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
                    }`}
                >
                    ← Previous
                </button>

                <span className="text-gray-600">
                    Part {partOrder} of {totalParts}
                </span>

                <button
                    onClick={() => handleNavigate('next')}
                     className={`px-6 py-2 rounded text-white font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                        isLastPart
                            ? 'bg-green-600 hover:bg-green-700 focus:ring-green-500' // Change style for last button
                            : 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
                    }`}
                >
                    {isLastPart ? 'Finish & Start Questions' : 'Next'} →
                </button>
            </div>
        </div>
    );
};

export default TutorialContent;