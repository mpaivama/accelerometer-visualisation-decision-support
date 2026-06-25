const state = {
  answers: {},
  history: [],
  step: null,
};

const questionCard = document.querySelector("#question-card");
const resultsSection = document.querySelector("#results");
const questionNumber = document.querySelector("#question-number");
const questionTitle = document.querySelector("#question-title");
const questionHelp = document.querySelector("#question-help");
const answerControls = document.querySelector("#answer-controls");
const answerSummary = document.querySelector("#answer-summary");
const progressLabel = document.querySelector("#progress-label");
const progressBar = document.querySelector("#progress-bar");
const errorBox = document.querySelector("#error-box");
const backButton = document.querySelector("#back-button");
const resetButton = document.querySelector("#reset-button");
const resultsBackButton = document.querySelector("#results-back-button");
const resultsResetButton = document.querySelector("#results-reset-button");

const displayText = {
  direct_example_available: "direct case-study example available",
  related_example_available: "related case-study example available",
  general_example_available: "simulated example available",
  signpost_only: "signpost only",
};

async function api(path, answers) {
  const response = await fetch(path, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({answers}),
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "The interface could not process that answer.");
  }
  return payload;
}

function showError(error) {
  errorBox.textContent = error.message;
  errorBox.hidden = false;
}

function clearError() {
  errorBox.hidden = true;
  errorBox.textContent = "";
}

function renderSummary(step) {
  answerSummary.replaceChildren();
  if (step.answer_summary.length === 0) {
    const empty = document.createElement("li");
    empty.className = "empty-summary";
    empty.textContent = "Your answers will appear here.";
    answerSummary.append(empty);
  } else {
    step.answer_summary.forEach((item) => {
      const row = document.createElement("li");
      const prompt = document.createElement("span");
      const answer = document.createElement("span");
      prompt.className = "answer-question";
      answer.className = "answer-value";
      prompt.textContent = item.question;
      answer.textContent = item.answer;
      row.append(prompt, answer);
      answerSummary.append(row);
    });
  }

  const total = Math.max(step.current_total, 1);
  const percentage = Math.round((step.answered_count / total) * 100);
  progressBar.style.width = `${percentage}%`;
  progressLabel.textContent = step.complete
    ? "Complete"
    : `${step.answered_count} of about ${step.current_total}`;
}

function renderChoiceQuestion(question) {
  question.options.forEach((option) => {
    const button = document.createElement("button");
    const label = document.createElement("span");
    const description = document.createElement("span");
    button.type = "button";
    button.className = "option-button";
    button.dataset.testid = `option-${option.value}`;
    label.className = "option-label";
    description.className = "option-description";
    label.textContent = option.label;
    description.textContent = option.description;
    button.append(label, description);
    button.addEventListener("click", () => submitAnswer(question.field, option.value));
    answerControls.append(button);
  });
}

function renderNumberQuestion(question) {
  const form = document.createElement("form");
  const fieldLabel = document.createElement("label");
  const input = document.createElement("input");
  const submit = document.createElement("button");
  const labelText = document.createElement("span");

  form.className = "number-form";
  fieldLabel.className = "number-field";
  labelText.textContent = "Whole number";
  input.type = "number";
  input.min = question.minimum;
  input.step = "1";
  input.required = true;
  input.placeholder = question.placeholder;
  input.dataset.testid = "number-input";
  submit.type = "submit";
  submit.className = "button primary";
  submit.textContent = "Continue";

  fieldLabel.append(labelText, input);
  form.append(fieldLabel, submit);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    submitAnswer(question.field, Number(input.value));
  });
  answerControls.append(form);
  input.focus();
}

function renderQuestion(step) {
  const question = step.question;
  questionCard.hidden = false;
  resultsSection.hidden = true;
  questionNumber.textContent = `Question ${step.answered_count + 1}`;
  questionTitle.textContent = question.title;
  questionHelp.textContent = question.help;
  answerControls.replaceChildren();

  if (question.type === "choice") {
    renderChoiceQuestion(question);
  } else {
    renderNumberQuestion(question);
  }

  backButton.disabled = state.history.length === 0;
}

function addDetail(card, label, text) {
  if (!text) return;
  const paragraph = document.createElement("p");
  const strong = document.createElement("strong");
  paragraph.className = "recommendation-detail";
  strong.textContent = `${label}: `;
  paragraph.append(strong, document.createTextNode(displayText[text] || text));
  card.append(paragraph);
}

function addDetailList(card, label, items) {
  if (!items || items.length === 0) return;
  const container = document.createElement("div");
  const strong = document.createElement("strong");
  const list = document.createElement("ul");
  container.className = "recommendation-detail";
  strong.textContent = `${label}: `;
  items.forEach((item) => {
    const row = document.createElement("li");
    row.textContent = item;
    list.append(row);
  });
  container.append(strong, list);
  card.append(container);
}

function addExampleFigure(card, recommendation) {
  if (!recommendation.example_image_file) return;

  const figure = document.createElement("figure");
  const image = document.createElement("img");
  const caption = document.createElement("figcaption");
  const captionLead = document.createElement("strong");
  const imageLink = document.createElement("a");

  figure.className = "example-figure";
  image.src = recommendation.example_image_file;
  image.alt = `${recommendation.visualisation} visual example`;
  image.loading = "lazy";

  captionLead.textContent = "Visual example. ";
  caption.append(captionLead);
  if (recommendation.example_source) {
    caption.append(document.createTextNode(`Source: ${recommendation.example_source}. `));
  }
  if (recommendation.example_source_note) {
    caption.append(document.createTextNode(recommendation.example_source_note));
  }
  imageLink.href = recommendation.example_image_file;
  imageLink.target = "_blank";
  imageLink.rel = "noreferrer";
  imageLink.textContent = "Open image";
  caption.append(document.createTextNode(" "));
  caption.append(imageLink);

  figure.append(image, caption);
  card.append(figure);
}

function renderList(elementId, items) {
  const list = document.querySelector(elementId);
  list.replaceChildren();
  items.forEach((item) => {
    const row = document.createElement("li");
    row.textContent = item;
    list.append(row);
  });
}

async function renderResults() {
  const result = await api("/api/recommend", state.answers);
  questionCard.hidden = true;
  resultsSection.hidden = false;

  const recommendationList = document.querySelector("#recommendation-list");
  recommendationList.replaceChildren();
  result.recommendations.forEach((recommendation) => {
    const card = document.createElement("article");
    const rank = document.createElement("span");
    const title = document.createElement("h3");
    card.className = "recommendation-card";
    rank.className = "recommendation-rank";
    rank.textContent = recommendation.rank;
    title.textContent = recommendation.visualisation;
    card.append(rank, title);
    addExampleFigure(card, recommendation);
    addDetail(card, "Visual mapping", recommendation.visual_mapping);
    addDetail(card, "Why", recommendation.rationale);
    addDetail(card, "Use when", recommendation.use_when);
    addDetail(card, "Caution", recommendation.caution);
    addDetail(card, "How to adapt code later", recommendation.adaptation_guidance);
    addDetail(card, "Example status", recommendation.implementation_status);
    addDetail(card, "Example note", recommendation.implementation_note);
    addDetail(card, "Example code file", recommendation.example_code_file);
    addDetailList(card, "Direct worked examples", recommendation.direct_case_study_examples);
    addDetailList(card, "Related worked examples", recommendation.related_case_study_examples);
    addDetail(card, "Data needed", recommendation.data_required);
    addDetailList(card, "Adapt in the worked example", recommendation.case_study_adaptation_points);
    addDetailList(card, "Checklist aspects to review", recommendation.checklist_aspects_to_review);
    recommendationList.append(card);
  });

  renderList("#decision-path", result.decision_path);
  renderList("#design-notes", result.design_notes);
  resultsBackButton.disabled = state.history.length === 0;
}

async function refresh() {
  clearError();
  try {
    const step = await api("/api/step", state.answers);
    state.step = step;
    state.answers = step.answers;
    renderSummary(step);
    if (step.complete) {
      await renderResults();
    } else {
      renderQuestion(step);
    }
  } catch (error) {
    showError(error);
  }
}

async function submitAnswer(field, value) {
  state.history.push({...state.answers});
  state.answers = {...state.answers, [field]: value};
  await refresh();
}

async function goBack() {
  if (state.history.length === 0) return;
  state.answers = state.history.pop();
  await refresh();
}

async function reset() {
  state.answers = {};
  state.history = [];
  await refresh();
}

backButton.addEventListener("click", goBack);
resultsBackButton.addEventListener("click", goBack);
resetButton.addEventListener("click", reset);
resultsResetButton.addEventListener("click", reset);

refresh();
