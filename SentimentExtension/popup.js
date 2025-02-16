document.addEventListener("DOMContentLoaded", () => {
    // Get elements once at startup
    const positiveBar = document.querySelector('.positive.sentiment-bar');
    const negativeBar = document.querySelector('.negative.sentiment-bar');
    const neutralBar = document.querySelector('.neutral.sentiment-bar');
    const loadingState = document.getElementById('loading');
    const resultsContainer = document.getElementById('results');

    // Initialize bars at 0%
    [positiveBar, negativeBar, neutralBar].forEach(bar => {
        bar.style.width = '0%';
    });

    // Get selected text from storage and populate textarea
    chrome.storage.local.get("selectedText", (data) => {
        if (data.selectedText) {
            inputText.value = data.selectedText;
        }
    });

    // Updated analyze button handler
    document.getElementById("analyzeButton").addEventListener("click", () => {
        const textToAnalyze = inputText.value.trim();
        
        if (!textToAnalyze) {
            showError("Please enter some text to analyze");
            return;
        }

        showLoadingState(true);
        
        // Remove the chrome.storage.local.get block and use textarea value directly
        fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: textToAnalyze })
        })
        .then(response => response.json())
        .then(result => {
            console.log('Full server response:', result);
            animateSentimentBars(result);
            showLoadingState(false);
        })
        
        .catch(error => {
            console.error("Error:", error);
            showLoadingState(false);
            showError("Analysis failed. Please try again.");
        });
    });


    function showLoadingState(show) {
        loadingState.style.display = show ? 'block' : 'none';
        resultsContainer.style.display = show ? 'none' : 'block';
        document.getElementById('analyzeButton').disabled = show;
    }

    function animateSentimentBars(result) {
        animateBar('positive', result.Positive);
        animateBar('negative', result.Negative);
        animateBar('neutral', result.Neutral);
        showSuggestions(result.suggestions);
    }

    function animateBar(sentiment, percentage) {
        const bar = document.querySelector(`.${sentiment}.sentiment-bar`);
        const textElement = document.getElementById(`${sentiment}Percentage`);
        
        // Reset before animating
        bar.style.width = '0%';
        textElement.textContent = '0%';

        // Animate after short delay
        setTimeout(() => {
            bar.style.width = `${percentage}%`;
            textElement.textContent = `${percentage}%`;
        }, 50);
    }

    function showSuggestions(suggestions) {
        const suggestionsBox = document.getElementById('suggestionsBox');
        const suggestionsList = document.getElementById('suggestionsList');
        
        console.log('Suggestions received:', suggestions);
        
        // Always clear previous content
        suggestionsList.innerHTML = '';
        
        if (suggestions && suggestions.length > 0) {
            suggestions.forEach(text => {
                console.log('Adding suggestion:', text);
                const div = document.createElement('div');
                div.className = 'suggestion-item';
                div.textContent = text;
                suggestionsList.appendChild(div);
            });
            suggestionsBox.style.display = 'block';
            console.log('Suggestions box should be visible now');
        } else {
            suggestionsBox.style.display = 'none';
            console.log('No suggestions - hiding box');
        }
    }

    function showError(message) {
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.style.color = '#d63031';
        errorElement.style.padding = '10px';
        errorElement.style.textAlign = 'center';
        errorElement.textContent = message;
        
        document.querySelector('.sentiment-container').appendChild(errorElement);
        
        // Remove error after 3 seconds
        setTimeout(() => {
            errorElement.remove();
        }, 3000);
    }

    
});