document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('text-form');
    const textInput = document.getElementById('text-input');
    const resultDiv = document.getElementById('result');
    const messagePara = document.getElementById('message');
    const feedbackSection = document.getElementById('feedback-section');
  
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = textInput.value.trim();
      if (!text) return;
  
      // Reset UI
      resultDiv.classList.add('hidden');
      feedbackSection.classList.add('hidden');
  
      // Send text to backend for analysis
      try {
        const response = await fetch('/analyze-text', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text }),
        });
  
        const result = await response.json();
        messagePara.textContent = `${result.message} (Confidence: ${result.confidence}%)`;
  
        // Show result
        resultDiv.classList.remove('hidden');
  
        // Show feedback section if uncertain
        if (result.is_misinformation === 'uncertain') {
          feedbackSection.classList.remove('hidden');
        }
      } catch (error) {
        messagePara.textContent = 'Error analyzing text. Please try again later.';
        resultDiv.classList.remove('hidden');
      }
    });
  
    // Feedback buttons
    document.getElementById('feedback-yes').addEventListener('click', () => sendFeedback(true));
    document.getElementById('feedback-no').addEventListener('click', () => sendFeedback(false));
  
    async function sendFeedback(userVerdict) {
      const text = textInput.value.trim();
      try {
        await fetch('/submit-feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text, user_verdict: userVerdict }),
        });
        alert('Feedback submitted. Thank you!');
      } catch (error) {
        alert('Error submitting feedback. Please try again later.');
      }
    }
  });
  