import React, { useState } from 'react';

const App = () => {
    const [ingredients, setIngredients] = useState('');
    const [results, setResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const mockApiCall = async (ingredientsList) => {
        // This is a mock API call. In a real application, this would be a call to your backend.
        console.log("Analyzing ingredients:", ingredientsList);
        // Simulate a network delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Mock results
        return ingredientsList.map(ingredient => {
            if (/e102|yellow 5/i.test(ingredient)) {
                return {
                    ingredient: ingredient,
                    normalized: "E102 (Tartrazine)",
                    status: "Compliant",
                    maxLevel: "20 mg/l",
                    regulation: "Commission Regulation (EU) No 1129/2011",
                    explanation: "This additive is compliant as per the provided concentration."
                };
            }
            if (/e122|azorubine/i.test(ingredient)) {
                return {
                    ingredient: ingredient,
                    normalized: "E122 (Azorubine)",
                    status: "Non-compliant",
                    maxLevel: "50 mg/l",
                    regulation: "Regulation (EC) No 1333/2008",
                    explanation: "The requested concentration exceeds the maximum permitted level."
                };
            }
            return {
                ingredient: ingredient,
                normalized: ingredient,
                status: "Unknown",
                maxLevel: "N/A",
                regulation: "N/A",
                explanation: "Could not determine the compliance status for this ingredient."
            };
        });
    };

    const handleTextSubmit = async () => {
        if (!ingredients) return;
        setIsLoading(true);
        setError('');
        setResults([]);

        const ingredientsList = ingredients.replace(/\n/g, ',').split(',').map(i => i.trim()).filter(i => i);
        try {
            const apiResults = await mockApiCall(ingredientsList);
            setResults(apiResults);
        } catch (err) {
            setError('Failed to analyze ingredients. Please try again.');
        }
        setIsLoading(false);
    };

    const handlePhotoUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setIsLoading(true);
        setError('');
        setResults([]);

        const { Tesseract } = window;
        try {
            const { data: { text } } = await Tesseract.recognize(file, 'eng');
            setIngredients(text);
            const ingredientsList = text.split(/[,
]/).map(i => i.trim()).filter(i => i);
            const apiResults = await mockApiCall(ingredientsList);
            setResults(apiResults);
        } catch (err) {
            setError('Failed to process image. Please try again with a clearer image.');
        }
        setIsLoading(false);
    };

    const getStatusClass = (status) => {
        if (status === 'Compliant') return 'text-success';
        if (status === 'Non-compliant') return 'text-danger';
        return 'text-muted';
    };

    return (
        <>
            <div className="header text-center">
                <h1>Food Additive Compliance Checker</h1>
                <p className="lead">Analyze food additives for EU compliance.</p>
            </div>

            <div className="container my-5">
                <div className="card">
                    <div className="card-body">
                        <h2 className="card-title">Analyze Ingredients</h2>
                        <div className="mb-3">
                            <label htmlFor="ingredientsTextarea" className="form-label">Enter ingredients (one per line or comma-separated)</label>
                            <textarea 
                                className="form-control" 
                                id="ingredientsTextarea"
                                rows="5"
                                value={ingredients}
                                onChange={(e) => setIngredients(e.target.value)}
                            ></textarea>
                        </div>
                        <button 
                            className="btn btn-primary me-2"
                            onClick={handleTextSubmit}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Analyzing...' : 'Analyze Text'}
                        </button>
                        
                        <div className="mt-3">
                            <label htmlFor="photoUpload" className="form-label">Or upload a photo of the ingredients label</label>
                            <input 
                                className="form-control"
                                type="file"
                                id="photoUpload"
                                accept="image/*"
                                onChange={handlePhotoUpload}
                                disabled={isLoading}
                            />
                        </div>
                    </div>
                </div>

                {error && <div className="alert alert-danger mt-4">{error}</div>}

                {results.length > 0 && (
                    <div className="card results-card">
                        <div className="card-body">
                            <h2 className="card-title">Analysis Results</h2>
                            <ul className="list-group list-group-flush">
                                {results.map((result, index) => (
                                    <li key={index} className="list-group-item">
                                        <div className="d-flex w-100 justify-content-between">
                                            <h5 className="mb-1">{result.ingredient}</h5>
                                            <small className={getStatusClass(result.status)}>{result.status}</small>
                                        </div>
                                        <p className="mb-1"><strong>Normalized:</strong> {result.normalized}</p>
                                        <p className="mb-1"><strong>Max Level:</strong> {result.maxLevel}</p>
                                        <p className="mb-1"><strong>Regulation:</strong> {result.regulation}</p>
                                        <small>{result.explanation}</small>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                )}
            </div>
        </>
    );
};

export default App;