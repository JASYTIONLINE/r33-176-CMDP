// scripts/main.js

document.addEventListener("DOMContentLoaded", () => {
  const startButton = document.getElementById("startButton");
  const container = document.getElementById("questionContainer");
  let currentIndex = 0;
  let questions = [];

  // Load questions from JSON
  async function loadQuestions() {
    try {
      const response = await fetch("data/missed-questions.json");
      questions = await response.json();
      showQuestion(currentIndex);
    } catch (error) {
      container.innerHTML = "<p>Error loading questions. Check file path or syntax.</p>";
      console.error("Error loading JSON:", error);
    }
  }

  // Render question to the page
  function showQuestion(index) {
    const q = questions[index];

    if (!q) {
      container.innerHTML = "<p>No more questions to review.</p>";
      return;
    }

    const optionsHTML = Object.entries(q.options).map(([key, value]) => {
      return `<li><strong>${key}.</strong> ${value}</li>`;
    }).join("");

    container.innerHTML = `
      <section class="question-block">
        <h2>Question ${index + 1}</h2>
        <p class="question-text">${q.question}</p>
        <ul class="options-list">${optionsHTML}</ul>
        <div class="answer-block">
          <h3>Explanation</h3>
          <p>${q.answer}</p>
        </div>
        <div class="exam-cue-block">
          <h4>Exam Cue</h4>
          <p>${q.examCue}</p>
        </div>
        <div class="dte-block">
          <strong>DTE:</strong> ${q.dte}
        </div>
        <button id="nextButton">Next Question</button>
      </section>
    `;

    document.getElementById("nextButton").addEventListener("click", () => {
      currentIndex++;
      showQuestion(currentIndex);
    });
  }

  startButton.addEventListener("click", () => {
    loadQuestions();
  });
});
