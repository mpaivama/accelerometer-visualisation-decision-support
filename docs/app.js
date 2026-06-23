const siteData = window.DECISION_TREE_DATA;

const state = {
  answers: {},
  history: [],
  step: null,
  stateId: siteData.default_state,
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
const sourceNote = document.querySelector("#source-note");

const displayText = {
  direct_example_available: "direct example available",
  related_example_available: "related example available",
  general_example_available: "general example available",
  signpost_only: "signpost only",
};

function valueKey(value) {
  return JSON.stringify(value);
}

function currentStep() {
  const step = siteData.states[state.stateId];
  if (!step) {
    throw new Error(
      "This answer path is not available in the generated decision tree. " +
      "Please start again, or check that the site was rebuilt from the current Python code.",
    );
  }
  return step;
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
  const summaryItems = answerSummaryItems();
  if (summaryItems.length === 0) {
    const empty = document.createElement("li");
    empty.className = "empty-summary";
    empty.textContent = "Your answers will appear here.";
    answerSummary.append(empty);
  } else {
    summaryItems.forEach((item) => {
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

function answerLabel(field, value) {
  const fieldLabels = siteData.answer_labels[field] || {};
  const key = String(value);
  return fieldLabels[key] || String(value);
}

function answerSummaryItems() {
  return siteData.field_order
    .filter((field) => Object.prototype.hasOwnProperty.call(state.answers, field))
    .map((field) => ({
      field,
      question: siteData.field_titles[field],
      answer: answerLabel(field, state.answers[field]),
    }));
}

function decisionPathItems() {
  return answerSummaryItems().map((item) => `${item.question}: ${item.answer}`);
}

function renderQuestion(step) {
  const question = siteData.questions[step.question_id];
  questionCard.hidden = false;
  resultsSection.hidden = true;
  questionNumber.textContent = `Question ${step.answered_count + 1}`;
  questionTitle.textContent = question.title;
  questionHelp.textContent = question.help;
  answerControls.replaceChildren();
  renderChoiceQuestion(question);
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

function renderList(elementId, items) {
  const list = document.querySelector(elementId);
  list.replaceChildren();
  items.forEach((item) => {
    const row = document.createElement("li");
    row.textContent = item;
    list.append(row);
  });
}

function renderResults() {
  const result = siteData.results[state.step.result_id];
  if (!result) {
    throw new Error("No recommendation was generated for this completed path.");
  }

  questionCard.hidden = true;
  resultsSection.hidden = false;

  const recommendationList = document.querySelector("#recommendation-list");
  recommendationList.replaceChildren();
  result.recommendation_ids.forEach((recommendationId) => {
    const recommendation = siteData.recommendations[recommendationId];
    const card = document.createElement("article");
    const rank = document.createElement("span");
    const title = document.createElement("h3");
    card.className = "recommendation-card";
    rank.className = "recommendation-rank";
    rank.textContent = recommendation.rank;
    title.textContent = recommendation.visualisation;
    card.append(rank, title);
    addDetail(card, "Visual mapping", recommendation.visual_mapping);
    addDetail(card, "Why", recommendation.rationale);
    addDetail(card, "Use when", recommendation.use_when);
    addDetail(card, "Caution", recommendation.caution);
    addDetail(card, "How to adapt code later", recommendation.adaptation_guidance);
    addDetail(card, "Worked example status", recommendation.implementation_status);
    addDetail(card, "Worked example note", recommendation.implementation_note);
    addDetail(card, "Example code file", recommendation.example_code_file);
    addDetailList(card, "Direct worked examples", recommendation.direct_case_study_examples);
    addDetailList(card, "Related worked examples", recommendation.related_case_study_examples);
    addDetail(card, "Data needed", recommendation.data_required);
    addDetailList(card, "Adapt in the worked example", recommendation.case_study_adaptation_points);
    addDetailList(card, "Checklist aspects to review", recommendation.checklist_aspects_to_review);
    recommendationList.append(card);
  });

  renderList("#decision-path", decisionPathItems());
  renderList("#design-notes", result.design_notes);
  resultsBackButton.disabled = state.history.length === 0;
}

function refresh() {
  clearError();
  try {
    const step = currentStep();
    state.step = step;
    renderSummary(step);
    if (step.complete) {
      renderResults();
    } else {
      renderQuestion(step);
    }
  } catch (error) {
    showError(error);
  }
}

function submitAnswer(field, value) {
  const step = currentStep();
  const nextStateId = step.transitions[valueKey(value)];
  if (!nextStateId) {
    showError(new Error("This choice is not available from the current state."));
    return;
  }
  state.history.push({
    answers: {...state.answers},
    stateId: state.stateId,
  });
  state.answers = {...state.answers, [field]: value};
  state.stateId = nextStateId;
  refresh();
}

function goBack() {
  if (state.history.length === 0) return;
  const previous = state.history.pop();
  state.answers = previous.answers;
  state.stateId = previous.stateId;
  refresh();
}

function reset() {
  state.answers = {};
  state.history = [];
  state.stateId = siteData.default_state;
  refresh();
}

backButton.addEventListener("click", goBack);
resultsBackButton.addEventListener("click", goBack);
resetButton.addEventListener("click", reset);
resultsResetButton.addEventListener("click", reset);

sourceNote.textContent =
  `Generated from ${siteData.meta.source_of_truth}. ` +
  siteData.meta.preliminary_notice;

refresh();
