import { createContext, useContext, useState } from 'react';

const TrainerContext = createContext();

export const TrainerProvider = ({ children }) => {
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [selectedLevel, setSelectedLevel] = useState(null);
  const [tutorialParts, setTutorialParts] = useState([]);

  return (
    <TrainerContext.Provider value={{
        selectedTopic,
        setSelectedTopic,
        selectedLevel,
        setSelectedLevel,
        tutorialParts,
        setTutorialParts
    }}>
        {children}
    </TrainerContext.Provider>
);
}

export function useTrainer() {
return useContext(TrainerContext);
}