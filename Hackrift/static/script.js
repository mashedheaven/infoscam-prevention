document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("text-form");
  const textInput = document.getElementById("text-input");
  const analyzeBtn = document.getElementById("analyze-btn");
  const clearBtn = document.getElementById("clear-btn");
  const charCount = document.getElementById("char-count");
  const resultPanel = document.getElementById("result");
  const riskLevel = document.getElementById("risk-level");
  const verdictBadge = document.getElementById("verdict-badge");
  const messagePara = document.getElementById("message");
  const riskScore = document.getElementById("risk-score");
  const scoreFill = document.getElementById("score-fill");
  const confidence = document.getElementById("confidence");
  const signalsList = document.getElementById("signals-list");
  const recommendationsList = document.getElementById("recommendations-list");
  const feedbackStatus = document.getElementById("feedback-status");
  const feedbackRisky = document.getElementById("feedback-risky");
  const feedbackSafe = document.getElementById("feedback-safe");

  let lastAnalysis = null;
  let lastText = "";

  textInput.addEventListener("input", updateCharacterCount);
  clearBtn.addEventListener("click", clearForm);
  feedbackRisky.addEventListener("click", () => sendFeedback(true));
  feedbackSafe.addEventListener("click", () => sendFeedback(false));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const text = textInput.value.trim();
    if (!text) {
      showInlineError("Enter text before running an assessment.");
      return;
    }

    setLoading(true);
    feedbackStatus.textContent = "Mark the message based on what you know.";

    try {
      const response = await fetch("/analyze-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "Analysis failed.");
      }

      lastText = text;
      lastAnalysis = payload;
      renderResult(payload);
    } catch (error) {
      showInlineError(error.message || "Analysis failed.");
    } finally {
      setLoading(false);
    }
  });

  updateCharacterCount();

  function renderResult(result) {
    const verdict = result.is_misinformation;
    const badgeText = verdict === true ? "Likely risky" : verdict === false ? "Likely safe" : "Review";
    const badgeClass = verdict === true ? "danger" : verdict === false ? "success" : "warning";

    resultPanel.classList.remove("hidden", "danger", "success", "warning");
    resultPanel.classList.add(badgeClass);
    verdictBadge.className = `verdict-badge ${badgeClass}`;
    verdictBadge.textContent = badgeText;
    riskLevel.textContent = result.risk_level || "Needs review";
    messagePara.textContent = result.message || "Assessment complete.";
    riskScore.textContent = String(result.risk_score ?? 0);
    scoreFill.style.width = `${Math.min(Number(result.risk_score || 0), 100)}%`;
    confidence.textContent = `Confidence ${result.confidence ?? 0}%`;

    replaceList(
      signalsList,
      result.signals && result.signals.length
        ? result.signals.map((signal) => `${signal.label}: ${signal.detail}`)
        : ["No strong warning signs found."]
    );

    replaceList(recommendationsList, result.recommendations || []);
  }

  async function sendFeedback(userVerdict) {
    if (!lastAnalysis || !lastText) {
      feedbackStatus.textContent = "Run an assessment before submitting feedback.";
      return;
    }

    feedbackRisky.disabled = true;
    feedbackSafe.disabled = true;
    feedbackStatus.textContent = "Saving feedback...";

    try {
      const response = await fetch("/submit-feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: lastText,
          user_verdict: userVerdict,
          analysis: lastAnalysis,
        }),
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "Feedback was not saved.");
      }

      feedbackStatus.textContent = "Feedback saved.";
    } catch (error) {
      feedbackStatus.textContent = error.message || "Feedback was not saved.";
    } finally {
      feedbackRisky.disabled = false;
      feedbackSafe.disabled = false;
    }
  }

  function replaceList(list, items) {
    list.replaceChildren();
    items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      list.appendChild(li);
    });
  }

  function showInlineError(message) {
    resultPanel.classList.remove("hidden", "danger", "success", "warning");
    resultPanel.classList.add("warning");
    verdictBadge.className = "verdict-badge warning";
    verdictBadge.textContent = "Attention";
    riskLevel.textContent = "Needs input";
    messagePara.textContent = message;
    riskScore.textContent = "0";
    scoreFill.style.width = "0%";
    confidence.textContent = "Confidence 0%";
    replaceList(signalsList, []);
    replaceList(recommendationsList, ["Add the message text and try again."]);
  }

  function clearForm() {
    textInput.value = "";
    lastAnalysis = null;
    lastText = "";
    resultPanel.classList.add("hidden");
    updateCharacterCount();
    textInput.focus();
  }

  function updateCharacterCount() {
    charCount.textContent = `${textInput.value.length} / ${textInput.maxLength}`;
  }

  function setLoading(isLoading) {
    analyzeBtn.disabled = isLoading;
    analyzeBtn.textContent = isLoading ? "Analyzing..." : "Analyze";
  }
});
