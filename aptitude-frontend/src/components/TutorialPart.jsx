// src/components/TutorialPart.js
import React from 'react';
import LatexRenderer from './LatexRenderer';
import TutorialExamples from './TutorialExamples';

// Helper to render newline-separated text into styled list items
const renderListItems = (text) => {
    if (!text || typeof text !== 'string') return null;
    const lines = text.split('\n').filter(line => line.trim() !== '');
    return (
        <ul className="pl-5 list-disc text-gray-700 space-y-2">
            {lines.map((line, index) => (
                <li key={index}>
                    <LatexRenderer>{line.trim()}</LatexRenderer>
                </li>
            ))}
        </ul>
    );
};

const TutorialPart = ({ part }) => {
    if (!part) return null;

    return (
        <article className="bg-white border border-gray-200 rounded-lg mb-8 p-6 md:p-8 shadow-md hover:shadow-lg transition-shadow duration-200 ease-in-out">
            {/* Part Title */}
            <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mt-0 mb-6 pb-3 border-b-2 border-blue-500">
                {part.part_name || 'Tutorial Part'}
            </h2>

            {/* Key Concepts Section */}
            {part.key_concepts && (
                <section className="mb-6">
                    <h3 className="text-xl font-semibold text-blue-600 mb-3">Key Concepts</h3>
                    {renderListItems(part.key_concepts)}
                </section>
            )}

            {/* Learning Roadmap/Strategy Section */}
            {part.preparation_strategy && (
                 <section className="mb-6">
                    <h3 className="text-xl font-semibold text-blue-600 mb-3">Learning Roadmap / Strategy</h3>
                    {renderListItems(part.preparation_strategy)}
                </section>
            )}

            {/* Explanation/Approach Section */}
             {part.explanations && (
                 <section className="mb-6">
                    <h3 className="text-xl font-semibold text-blue-600 mb-3">Explanation / Approach</h3>
                     {/* Apply whitespace-pre-wrap to handle \n correctly within the explanation text */}
                     <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                        <LatexRenderer>{part.explanations}</LatexRenderer>
                     </div>
                </section>
            )}

            {/* Examples Section */}
            {part.example_problems && (
                 <section className="mb-6">
                   {/* TutorialExamples now contains its own h3 heading */}
                   <TutorialExamples examplesString={part.example_problems} />
                </section>
            )}

            {/* Common Pitfalls Section */}
            {part.common_pitfalls && (
                 <section className="mb-6">
                    <h3 className="text-xl font-semibold text-orange-600 mb-3">Common Pitfalls</h3> {/* Different color? */}
                    {renderListItems(part.common_pitfalls)}
                </section>
            )}

            {/* Quick Tips Section */}
            {part.quick_tips && (
                 <section className="mb-6">
                    <h3 className="text-xl font-semibold text-green-600 mb-3">Quick Tips / Pro Tips</h3> {/* Different color? */}
                    {renderListItems(part.quick_tips)}
                </section>
            )}

        </article>
    );
};

export default TutorialPart;