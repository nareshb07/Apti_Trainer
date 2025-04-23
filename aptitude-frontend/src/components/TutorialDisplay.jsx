// src/components/TutorialDisplay.js
import React, { useState, useEffect } from 'react';
import TutorialPart from './TutorialPart';
import { useTrainer } from '../context/TrainerContext'; // Adjust path if needed

// This component now relies on the context for topic, level, and parts data
const TutorialDisplay = () => {
    // Get state and setters from the context
    const { selectedTopic, selectedLevel, tutorialParts, setTutorialParts } = useTrainer();

    // Keep local state for the fetch operation itself
    const [loading, setLoading] = useState(false); // Initially false, true only during fetch
    const [error, setError] = useState(null);

    // Effect runs when selectedTopic or selectedLevel changes
    useEffect(() => {
        // Only fetch if both topic and level are selected and have slugs
        if (selectedTopic?.slug && selectedLevel?.slug) {
            setLoading(true); // Start loading indicator
            setError(null); // Clear previous errors
            setTutorialParts([]); // Clear previous parts immediately

            const apiUrl = `/api/tutorials/${selectedTopic.slug}/${selectedLevel.slug}/`;

            fetch(apiUrl)
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            throw new Error(`HTTP error ${response.status}: ${text || response.statusText}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    if (Array.isArray(data)) {
                        setTutorialParts(data); // Update context with fetched parts
                    } else {
                        console.warn("API did not return an array:", data);
                        throw new Error("Unexpected data format received from API.");
                    }
                    setLoading(false); // Stop loading
                })
                .catch(err => {
                    console.error("Failed to fetch tutorial data:", err);
                    setError(`Failed to load tutorial: ${err.message}`);
                    setTutorialParts([]); // Clear parts on error
                    setLoading(false); // Stop loading
                });
        } else {
            // If topic or level is not selected, clear parts and any errors
            setTutorialParts([]);
            setError(null);
            setLoading(false);
        }
        // Dependency array: fetch when topic/level changes, include setter from context
    }, [selectedTopic, selectedLevel, setTutorialParts]);

    // --- Render Logic ---

    // Display message if no topic/level selected
     if (!selectedTopic || !selectedLevel) {
        return (
            <div className="max-w-4xl mx-auto p-4 md:p-6 text-center">
                 <p className="text-lg text-gray-500 mt-10">
                     Please select a topic and level to begin.
                 </p>
            </div>
        );
    }

    // Display loading state
    if (loading) {
        return (
            <div className="flex justify-center items-center h-40">
                <p className="text-lg text-gray-500 animate-pulse">Loading tutorial...</p>
            </div>
        );
    }

    // Display error state
    if (error) {
        return (
             <div className="max-w-4xl mx-auto p-4 md:p-6">
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                    <strong className="font-bold">Error: </strong>
                    <span className="block sm:inline">{error}</span>
                </div>
            </div>
        );
    }

    // Display "No parts found" state (after successful fetch but empty result)
    if (!loading && (!tutorialParts || tutorialParts.length === 0)) {
         return (
             <div className="max-w-4xl mx-auto p-4 md:p-6 text-center">
                 <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4 capitalize">
                     {/* Use names from context objects if available, fallback to slug */}
                     {selectedTopic?.name || selectedTopic.slug}: {selectedLevel?.name || selectedLevel.slug}
                 </h1>
                 <p className="text-lg text-gray-500 mt-10">No tutorial parts found for this topic and level.</p>
            </div>
         );
    }

    // Success State - Displaying Tutorial Parts fetched into context
    return (
        <div className="max-w-4xl mx-auto p-4 md:p-6 font-sans">
            <h1 className="text-center text-3xl md:text-4xl font-bold text-gray-800 mb-8 capitalize">
                {/* Use names from context objects if available, fallback to slug */}
                {selectedTopic?.name || selectedTopic.slug}: {selectedLevel?.name || selectedLevel.slug} Tutorial
            </h1>
            <div>
                {tutorialParts.map((part) => (
                    <TutorialPart key={part.slug || part.order} part={part} />
                ))}
            </div>
        </div>
    );
};

export default TutorialDisplay;