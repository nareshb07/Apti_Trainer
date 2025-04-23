// src/context/TrainerContext.js
import { createContext, useContext, useState, useCallback } from 'react';
import API from '../api'; // Assuming API is configured (e.g., Axios instance)

const TrainerContext = createContext();

export const TrainerProvider = ({ children }) => {
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [selectedLevel, setSelectedLevel] = useState(null);
  const [tutorialParts, setTutorialParts] = useState([]);
  const [isTutorialLoading, setIsTutorialLoading] = useState(false);
  const [tutorialError, setTutorialError] = useState(null);

  // --- CORRECTED fetchTutorials function ---
  const fetchTutorials = useCallback(async (topic, level) => {
    // Guard clauses for missing topic/level or slugs
    if (!topic?.slug || !level?.slug) {
      setTutorialParts([]);
      setTutorialError(null);
      setIsTutorialLoading(false);
      console.log("fetchTutorials skipped: Missing topic or level slug.");
      return;
    }

    // Construct API URL - *** Double check if you need /api/ prefix ***
    const apiUrl = `/tutorials/${topic.slug}/${level.slug}/`;
    // const apiUrl = `/tutorials/${topic.slug}/${level.slug}/`; // If no /api/ prefix needed

    console.log(`FETCHING TUTORIALS from ${apiUrl} for: Topic Slug = ${topic.slug}, Level Slug = ${level.slug}`);
    setIsTutorialLoading(true);
    setTutorialError(null);
    setTutorialParts([]); // Clear old parts

    try {
        // Use await with try/catch for cleaner async handling with Axios
        const response = await API.get(apiUrl); // Assuming API.get returns Axios response

        // Axios typically throws for non-2xx, so we expect success here.
        // Validate the data received in response.data
        if (Array.isArray(response?.data)) {
            console.log('Context: Fetch successful, received data:', response.data);
            setTutorialParts(response.data); // Access parsed data from response.data
        } else {
            // Handle cases where API returns 2xx but unexpected data format
            console.warn("API response data is not an array:", response?.data);
            throw new Error("Invalid data format received for tutorials.");
        }

    } catch (err) {
        console.error("Failed to fetch tutorial data:", err);

        // --- Axios-specific Error Handling ---
        let errorMessage = "An unknown error occurred"; // Default message
        if (err.response) {
            // Server responded with a status code outside the 2xx range
            console.error("Error Response Data:", err.response.data);
            console.error("Error Response Status:", err.response.status);

            // Extract specific error message from backend if available
            const backendError = err.response.data?.error ||
                                 err.response.data?.detail ||
                                 (typeof err.response.data === 'string' ? err.response.data : null);

            errorMessage = backendError || err.response.statusText || `Request failed with status code ${err.response.status}`;
            errorMessage = `(${err.response.status}) ${errorMessage}`; // Prepend status code

        } else if (err.request) {
            // The request was made but no response was received
            console.error("Error Request:", err.request);
            errorMessage = "No response received from server. Check network connection or backend status.";
        } else {
            // Something happened in setting up the request that triggered an Error
            console.error('Error Message:', err.message);
            errorMessage = err.message;
        }

        setTutorialError(`Failed to load tutorial: ${errorMessage}`); // Set the more detailed error
        setTutorialParts([]); // Ensure parts are cleared on error

    } finally {
        // This runs regardless of success or error
        setIsTutorialLoading(false);
        console.log("Context: fetchTutorials finished.");
    }
  }, []); // Dependencies are empty as it uses args


  // --- Rest of the Provider ---
  return (
    <TrainerContext.Provider value={{
        selectedTopic,
        setSelectedTopic,
        selectedLevel,
        setSelectedLevel,
        tutorialParts,
        isTutorialLoading,
        tutorialError,
        fetchTutorials
    }}>
        {children}
    </TrainerContext.Provider>
  );
}

export function useTrainer() {
  const context = useContext(TrainerContext);
  if (context === undefined) {
    throw new Error('useTrainer must be used within a TrainerProvider');
  }
  return context;
}