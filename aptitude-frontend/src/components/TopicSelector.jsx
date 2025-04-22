// src/components/TopicSelector.js
import React, { useEffect, useState } from 'react';
import { useTrainer } from '../context/TrainerContext';
import { useNavigate } from 'react-router-dom';
import API from '../api'; // Assuming API is configured (e.g., Axios instance)

function TopicSelector() {
    // Get necessary state and functions from context
    const {
        selectedTopic,
        setSelectedTopic,
        selectedLevel,
        fetchTutorials,
        isTutorialLoading: isTutorialContentLoading // Loading state for the TUTORIAL CONTENT fetch
    } = useTrainer();
    const navigate = useNavigate();

    // State specifically for fetching and managing the list of TOPICS
    const [availableTopics, setAvailableTopics] = useState([]); // State to hold fetched topics
    const [isLoadingTopics, setIsLoadingTopics] = useState(false); // Loading state for topic list fetch
    const [topicError, setTopicError] = useState(null); // Error state for topic list fetch

    // --- Fetch Available Topics when Level Changes (or on mount if level exists) ---
    useEffect(() => {
        // Only fetch topics if a level is selected and has a slug
        if (selectedLevel?.slug) {
            setIsLoadingTopics(true);
            setTopicError(null);
            setAvailableTopics([]); // Clear old topics before fetching new ones
            setSelectedTopic(null); // Also clear the selected topic when the level changes

            // Define the API endpoint for fetching topics
            const topicsApiUrl = '/topics/';
            // Optional: If topics depend on level, construct URL like:
            // const topicsApiUrl = `/api/topics/?level=${selectedLevel.slug}`;

            console.log(`Fetching topics from: ${topicsApiUrl}`);

            API.get(topicsApiUrl) // Use the correct URL for topics
                .then(response => {
                    // Assuming API returns data in response.data and it's an array
                    if (Array.isArray(response.data)) {
                        console.log("Fetched topics successfully:", response.data);
                        setAvailableTopics(response.data); // <<< CORRECT: Update availableTopics state
                    } else {
                         console.error("API response for topics is not an array:", response.data);
                         throw new Error("Invalid data format received for topics.");
                    }
                })
                .catch(err => {
                    console.error("Failed to fetch topics:", err);
                    // Try to get a more specific error message if available
                    const message = err.response?.data?.error || err.message || "Unknown error";
                    setTopicError(`Failed to load topics: ${message}`);
                })
                .finally(() => {
                    setIsLoadingTopics(false); // Stop loading indicator regardless of success/error
                });
        } else {
            // If no level is selected, clear topics state
            setAvailableTopics([]);
            setSelectedTopic(null); // Ensure topic selection is also cleared
            setIsLoadingTopics(false);
            setTopicError(null);
        }
        // Dependencies: This effect should re-run if the selected level changes.
        // Also include setSelectedTopic because we call it to clear the topic.
    }, [selectedLevel, setSelectedTopic]);

    // --- Handle Topic Selection Change ---
    const handleTopicChange = async (e) => {
        const topicSlug = e.target.value;
        console.log('handleTopicChange: Selected topic slug =', topicSlug);

        // Find the full topic object from the fetched state
        const topic = availableTopics.find(t => t.slug === topicSlug);
        console.log('handleTopicChange: Found topic object =', topic); // Log the found object or undefined

        // Update the selected topic in the global context
        setSelectedTopic(topic || null);

        // Log the currently selected level for debugging the condition
        console.log('handleTopicChange: selectedLevel from context =', selectedLevel);

        // Check if both topic and level are validly selected
        if (topic && selectedLevel) {
            console.log('handleTopicChange: Condition (topic && selectedLevel) is TRUE. Calling fetchTutorials...');
            // Call the function from context to fetch the tutorial parts
            await fetchTutorials(topic, selectedLevel);
            console.log("handleTopicChange: Fetch tutorial call initiated/completed. Navigating...");
            // Navigate to the first part of the tutorial view
            navigate('/tutorial/1');
        } else {
            console.warn('handleTopicChange: Condition (topic && selectedLevel) is FALSE. Fetch Tutorial NOT called.');
            if (!topic) console.warn('Reason: Local `topic` variable is falsy (likely "Select Topic..." or find failed).');
            if (!selectedLevel) console.warn('Reason: `selectedLevel` from context is falsy.');
        }
    };

    // --- Render Logic ---

    // Guard clause if level is not selected (though routing might handle this)
    if (!selectedLevel) {
        return <p>Please select a level first.</p>;
    }

    return (
        <div className="flex flex-col items-center">
            <h2 className="text-xl font-semibold mb-4">Select a Topic for {selectedLevel.name}</h2>

            {/* Display loading indicator while fetching the list of topics */}
            {isLoadingTopics && <p className="text-gray-500 animate-pulse">Loading topics...</p>}

            {/* Display error message if fetching the topic list failed */}
            {topicError && (
                <div className="text-red-600 bg-red-100 border border-red-400 p-3 rounded my-2 text-center">
                    <strong>Error:</strong> {topicError}
                </div>
            )}

            {/* Render the dropdown only if topics are not loading and there was no error */}
            {!isLoadingTopics && !topicError && (
                <select
                    className="border border-gray-300 rounded p-2 w-64 mt-2"
                    value={selectedTopic?.slug || ''} // Control component value using context state
                    onChange={handleTopicChange}
                    // Disable dropdown if EITHER the topics list is loading OR the tutorial content is loading
                    disabled={isLoadingTopics || isTutorialContentLoading}
                >
                    <option value="">Select Topic...</option>
                    {/* Map over the fetched availableTopics state */}
                    {availableTopics.map(t => (
                        <option key={t.slug} value={t.slug}>
                            {t.name}
                        </option>
                    ))}
                </select>
            )}

            {/* Display loading indicator for the TUTORIAL CONTENT fetch (triggered after selection) */}
            {isTutorialContentLoading && <p className="mt-4 text-blue-600 animate-pulse">Loading tutorial content...</p>}
        </div>
    );
}

export default TopicSelector;