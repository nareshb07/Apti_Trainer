// src/components/TutorialExamples.js
import React from 'react';
import LatexRenderer from './LatexRenderer';

// Keep the same parsing logic as before
const parseExamples = (examplesString) => {
     if (!examplesString || typeof examplesString !== 'string') {
        return [];
    }
    const examples = [];
    const exampleRegex = /EXAMPLE\s*\d+:\s*Problem:\s*(.*?)\s*Solution Steps:\s*((?:-\s*.*(?:\n|$))+)\s*Answer:\s*(.*?)(?:\s*Visualization Tip:\s*(.*?))?(?=\n\nEXAMPLE|\s*$)/gs;
    let match;
    while ((match = exampleRegex.exec(examplesString)) !== null) {
        const problem = match[1]?.trim() || '';
        const stepsRaw = match[2]?.trim() || '';
        const finalAnswer = match[3]?.trim() || '';
        const visualization = match[4]?.trim() || '';
        const solutionSteps = stepsRaw.split('\n')
                                     .map(step => step.replace(/^-\s*/, '').trim())
                                     .filter(step => step);
        examples.push({ problem, solutionSteps, finalAnswer, visualization });
    }
    return examples;
};


const TutorialExamples = ({ examplesString }) => {
    const examples = parseExamples(examplesString);

    if (!examples || examples.length === 0) {
        // Added some basic styling for the "No examples" case
        return <p className="text-gray-500 italic">No examples provided.</p>;
    }

    return (
        // Container for all examples
        <div className="mt-5 pt-4 border-t border-gray-200">
            <h3 className="text-xl font-semibold text-blue-600 mb-4">Worked Examples</h3> {/* Heading for the section */}
            {examples.map((example, index) => (
                // Individual example block
                <div key={index} className="mb-8 p-4 border border-gray-300 rounded-lg bg-gray-50 shadow-sm">
                    {/* Example number heading */}
                    <h4 className="mb-4 pb-2 border-b border-gray-200 text-lg font-semibold text-gray-700">
                        Example {index + 1}
                    </h4>
                    {/* Problem Section */}
                    <div className="mb-4">
                        <strong className="block mb-1 font-medium text-gray-600">Problem:</strong>
                        <div className="text-gray-800"> {/* Container for potentially multiline content */}
                             <LatexRenderer>{example.problem}</LatexRenderer>
                        </div>
                    </div>
                    {/* Solution Steps Section */}
                    <div className="mb-4">
                        <strong className="block mb-1 font-medium text-gray-600">Solution Steps:</strong>
                        <ul className="pl-5 list-disc text-gray-800">
                            {example.solutionSteps.map((step, stepIndex) => (
                                <li key={stepIndex} className="mb-2">
                                    <LatexRenderer>{step}</LatexRenderer>
                                </li>
                            ))}
                        </ul>
                    </div>
                     {/* Answer Section */}
                    <div className="mb-4">
                        <strong className="block mb-1 font-medium text-gray-600">Answer:</strong>
                         <div className="text-gray-800 font-medium"> {/* Make answer stand out slightly */}
                             <LatexRenderer>{example.finalAnswer}</LatexRenderer>
                        </div>
                    </div>
                    {/* Visualization Tip Section (Optional) */}
                    {example.visualization && (
                        <div className="mt-4 pt-3 border-t border-dashed border-gray-300">
                            <strong className="block mb-1 font-medium text-gray-600 text-sm">Visualization Tip:</strong>
                             <p className="text-gray-700 text-sm italic">
                                 <LatexRenderer>{example.visualization}</LatexRenderer>
                             </p>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
};

export default TutorialExamples;