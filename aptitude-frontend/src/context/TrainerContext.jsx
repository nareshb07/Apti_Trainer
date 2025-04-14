import { createContext, useContext, useState } from 'react';

const TrainerContext = createContext();

export const TrainerProvider = ({ children }) => {
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [selectedLevel, setSelectedLevel] = useState(null);

  return (
    <TrainerContext.Provider value={{ selectedTopic, setSelectedTopic, selectedLevel, setSelectedLevel }}>
      {children}
    </TrainerContext.Provider>
  );
};

export const useTrainer = () => useContext(TrainerContext);
