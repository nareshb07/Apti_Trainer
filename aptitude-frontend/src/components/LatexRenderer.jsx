// src/components/LatexRenderer.js
import React from 'react';
import Latex from 'react-latex-next';
import 'katex/dist/katex.min.css'; // Still required CSS for KaTeX

// Delimiters matching Python output (double backslashes become \\\\ in JS strings)
const latexDelimiters = [
    { left: "\\\\\\(", right: "\\\\\\)", display: false }, // Inline math \\(...\\)
    { left: "\\\\\\[", right: "\\\\\\]", display: true },  // Display math \\[...\\]
];

// Use React.memo for potential performance optimization
const LatexRenderer = React.memo(({ children }) => {
    if (!children || typeof children !== 'string') {
        return null;
    }

    // Directly render the string; parent component handles structure (like newlines)
    return (
        <Latex delimiters={latexDelimiters}>
            {children}
        </Latex>
    );
});

export default LatexRenderer;