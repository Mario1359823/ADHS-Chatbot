const steps = [
  {
    title: 'Erstbewertung der Wunde',
    description:
      'Führen Sie eine strukturierte Anamnese durch, erfassen Sie Vitalparameter und dokumentieren Sie die Wunde mit validierten Scores.',
    actions: [
      {
        label: 'Anamnese & Komorbiditäten erheben',
        decision:
          'Überprüfen Sie Diabetesstatus, Gefäßrisiken, Mobilität und Schmerz. Identifizieren Sie Barrieren für die Wundheilung frühzeitig.',
      },
      {
        label: 'Wundgröße und -tiefe vermessen',
        decision:
          'Nutzen Sie digitale Messsysteme oder Lineal und Tiefenmesser. Dokumentieren Sie Exsudat, Geruch und Gewebearten.',
      },
      {
        label: 'Infektionszeichen screenen',
        decision:
          'Bewerten Sie lokale (Rötung, Wärme, Schmerz) und systemische Zeichen (Fieber, CRP). Ziehen Sie Biofilmmanagement in Erwägung.',
      },
    ],
  },
  {
    title: 'Diagnostische Abklärung',
    description:
      'Ergänzen Sie die klinische Untersuchung um apparative Diagnostik, um Ursachen chronischer Wunden zu identifizieren.',
    actions: [
      {
        label: 'ABI und Doppler-Ultraschall durchführen',
        decision:
          'Ein ABI < 0,5 spricht für eine kritische Ischämie. Ziehen Sie vaskuläre Interventionen in Betracht.',
      },
      {
        label: 'Labor und Mikrobiologie anfordern',
        decision:
          'Bestimmen Sie HbA1c, Albumin, Entzündungsmarker. Bei Infektionsverdacht sterile Abstriche oder Biopsien entnehmen.',
      },
      {
        label: 'Bildgebung planen',
        decision:
          'Bei Osteomyelitisverdacht MRI erwägen. Duplexsonographie zur Evaluation venöser Insuffizienz einplanen.',
      },
    ],
  },
  {
    title: 'Therapieoptionen auswählen',
    description:
      'Leiten Sie aus Befunden und Patientenzielen ein interdisziplinäres Therapiekonzept ab.',
    actions: [
      {
        label: 'Debridement-Strategie wählen',
        decision:
          'Abhängig von Gewebe und Setting: chirurgisch, ultraschallgestützt oder enzymatisch. Schmerzmanagement vorbereiten.',
      },
      {
        label: 'Wundauflage selektieren',
        decision:
          'Kombinieren Sie absorptive und antimikrobielle Produkte gemäß Exsudatmenge und Infektionsrisiko.',
      },
      {
        label: 'Systemtherapie initiieren',
        decision:
          'Optimieren Sie Blutzuckerkontrolle, Druckentlastung, Kompression und behandeln Sie Infektionen leitliniengerecht.',
      },
    ],
  },
  {
    title: 'Verlaufsmonitoring etablieren',
    description:
      'Setzen Sie strukturierte Follow-up-Termine und digitale Dokumentation ein, um Heilungsverlauf zu objektivieren.',
    actions: [
      {
        label: 'Fotodokumentation aktualisieren',
        decision:
          'Nutzen Sie standardisierte Bildprotokolle und vergleichen Sie Flächenreduktion über Zeit.',
      },
      {
        label: 'Heilungsprognose evaluieren',
        decision:
          'Berechnen Sie Wound-Healing-Trajectories und passen Sie das Therapieziel (Healing vs. Palliation) an.',
      },
      {
        label: 'Telemedizinische Visiten planen',
        decision:
          'Integrieren Sie Videosprechstunden und Pflegeberichte, um Verzögerungen frühzeitig zu erkennen.',
      },
    ],
  },
  {
    title: 'Interdisziplinäres Team koordinieren',
    description:
      'Binden Sie alle relevanten Fachbereiche ein und definieren Sie Verantwortlichkeiten.',
    actions: [
      {
        label: 'Wundboard organisieren',
        decision:
          'Legen Sie regelmäßige Treffen fest und dokumentieren Sie Therapieentscheidungen transparent.',
      },
      {
        label: 'Patientenschulung implementieren',
        decision:
          'Schulen Sie Patient:innen zu Selbstkontrolle, Kompression und Lebensstiländerungen.',
      },
      {
        label: 'Versorgungsnetzwerk aufbauen',
        decision:
          'Kooperieren Sie mit Hausärzten, Homecare und Podologie. Definieren Sie Eskalationspfade für Komplikationen.',
      },
    ],
  },
];

const examQuestions = [
  {
    question:
      'Welche Maßnahme ist essenziell, bevor bei einem Ulcus cruris venosum Kompressionstherapie begonnen wird?',
    choices: [
      'Duplexsonographie der V. femoralis',
      'Bestimmung des ABI zur arteriellen Abklärung',
      'MR-Angiographie des Beckens',
      'Routinemäßige Biopsie der Wunde',
    ],
    answer: 1,
    explanation:
      'Vor jeder Kompression muss eine kritische arterielle Durchblutungsstörung ausgeschlossen werden. Der ABI ist der Standard.',
  },
  {
    question:
      'Welcher Befund deutet auf eine Infektion in einer chronischen Wunde hin?',
    choices: [
      'Seröses, klares Exsudat',
      'Wundgeruch, neu aufgetretener Schmerz und Nekrosen',
      'Granulationsgewebe am Wundgrund',
      'Geringes Wundexsudat',
    ],
    answer: 1,
    explanation:
      'Klinische Infektionszeichen sind Geruch, Schmerzverstärkung, Gewebsnekrose oder stagnierende Heilung.',
  },
  {
    question:
      'Welche Empfehlung gilt für das Debridement bei starkem Biofilmverdacht?',
    choices: [
      'Kein Debridement durchführen',
      'Nur trockene Kompressen verwenden',
      'Regelmäßiges, ggf. chirurgisches Debridement mit Biofilmkontrolle',
      'Nur systemische Antibiotikatherapie',
    ],
    answer: 2,
    explanation:
      'Biofilme erfordern konsequentes Debridement kombiniert mit antimikrobiellen Maßnahmen.',
  },
  {
    question:
      'Welche Aussage trifft auf die Telemedizin im Wundmanagement zu?',
    choices: [
      'Sie ersetzt physische Visiten vollständig.',
      'Sie ermöglicht frühzeitige Erkennung von Verschlechterungen durch engmaschige Dokumentation.',
      'Sie erhöht das Risiko für Datenschutzverletzungen und wird nicht empfohlen.',
      'Sie ist nur in Studien zugelassen.',
    ],
    answer: 1,
    explanation:
      'Telemedizin kann die Versorgung ergänzen, indem sie den Informationsfluss beschleunigt und Verschlechterungen früh erkennt.',
  },
  {
    question:
      'Wofür steht die Abkürzung TIME im Wundmanagement?',
    choices: [
      'Therapy, Incision, Moisture, Epithelisation',
      'Tissue, Infection/Inflammation, Moisture balance, Edge advancement',
      'Temperature, Infection, Mobility, Edema',
      'Tissue, Injury, Moisture, Education',
    ],
    answer: 1,
    explanation:
      'TIME ist ein etabliertes Framework für die strukturierte Wundbeurteilung.',
  },
  {
    question:
      'Welche Laborparameter unterstützen die Heilungsprognose einer chronischen Wunde?',
    choices: [
      'Albumin, HbA1c und CRP',
      'Kalium, Natrium und Bilirubin',
      'LDH, CK und Leukozyten',
      'INR, Quick und Fibrinogen',
    ],
    answer: 0,
    explanation:
      'Albumin spiegelt die Eiweißversorgung, HbA1c die Stoffwechseleinstellung und CRP die Entzündungslage wider.',
  },
  {
    question:
      'Welche Aussage zur Schmerztherapie bei chronischen Wunden ist richtig?',
    choices: [
      'Schmerzen spielen keine Rolle für die Heilung.',
      'Nur Opioide sind wirksam.',
      'Schmerzmanagement sollte multimodal erfolgen und bereits vor dem Debridement beginnen.',
      'Schmerztherapie ist Aufgabe der Pflegekräfte.',
    ],
    answer: 2,
    explanation:
      'Ein multimodaler Ansatz (medikamentös, lokal, psychologisch) verbessert Adhärenz und Heilung.',
  },
  {
    question:
      'Was ist ein Vorteil digitaler Wunddokumentation?',
    choices: [
      'Sie verlängert die Dokumentationszeit.',
      'Sie reduziert Transparenz im Team.',
      'Sie ermöglicht Verlaufsmessungen und Qualitätsindikatoren.',
      'Sie ersetzt klinische Untersuchungen.',
    ],
    answer: 2,
    explanation:
      'Digitale Dokumentation macht Heilungsverläufe messbar und erleichtert Qualitätsmanagement.',
  },
  {
    question:
      'Wann ist eine palliative Zielsetzung im Wundmanagement angezeigt?',
    choices: [
      'Wenn die Heilung länger als 4 Wochen dauert.',
      'Bei multimorbiden Patient:innen, wenn die Heilungschancen trotz optimaler Therapie gering sind.',
      'Nur bei onkologischen Patienten.',
      'Nie, palliative Versorgung ist kontraindiziert.',
    ],
    answer: 1,
    explanation:
      'Bei limitierter Prognose oder geringer Heilungschance steht Lebensqualität im Vordergrund.',
  },
  {
    question:
      'Welche Maßnahme unterstützt die Prävention von Rezidiven?',
    choices: [
      'Verzicht auf Kompression bei venösen Ulzera',
      'Fortlaufende Patientenschulung und Versorgung von Begleiterkrankungen',
      'Keine weitere Kontrolle nach Abheilung',
      'Nur systemische Antibiotika für 3 Monate',
    ],
    answer: 1,
    explanation:
      'Patientenedukation, Kompression und Management von Begleiterkrankungen senken Rezidivraten.',
  },
];

const accessGate = document.getElementById('access-gate');
const loginForm = document.getElementById('login-form');
const paymentForm = document.getElementById('payment-form');
const logoutButton = document.getElementById('logout-button');
const toolSteps = document.querySelectorAll('.tool-step');
const toolTitle = document.getElementById('tool-title');
const toolDescription = document.getElementById('tool-description');
const toolActions = document.getElementById('tool-actions');
const toolDecision = document.getElementById('tool-decision');
const examForm = document.getElementById('exam-form');
const examQuestion = document.getElementById('exam-question');
const examChoices = document.getElementById('exam-choices');
const questionCounter = document.getElementById('question-counter');
const progressIndicator = document.getElementById('progress-indicator');
const examResult = document.getElementById('exam-result');
const examScore = document.getElementById('exam-score');
const examFeedback = document.getElementById('exam-feedback');
const restartExamButton = document.getElementById('restart-exam');

let currentStep = 0;
let selectedActionIndex = null;
let examIndex = 0;
let correctAnswers = 0;
let authenticated = false;
let paid = false;

function renderStep(stepIndex) {
  const step = steps[stepIndex];
  toolTitle.textContent = step.title;
  toolDescription.textContent = step.description;
  toolActions.innerHTML = '';
  step.actions.forEach((action, index) => {
    const li = document.createElement('li');
    li.textContent = action.label;
    li.addEventListener('click', () => {
      selectedActionIndex = index;
      document
        .querySelectorAll('.action-list li')
        .forEach((item) => item.classList.remove('selected'));
      li.classList.add('selected');
      toolDecision.textContent = action.decision;
    });
    toolActions.appendChild(li);
  });
  toolDecision.textContent =
    'Wählen Sie oben eine Maßnahme aus, um Details und Handlungsempfehlungen zu sehen.';
}

toolSteps.forEach((button, index) => {
  button.addEventListener('click', () => {
    toolSteps.forEach((btn) => btn.classList.remove('active'));
    button.classList.add('active');
    currentStep = index;
    renderStep(index);
  });
});

function renderQuestion() {
  const currentQuestion = examQuestions[examIndex];
  examQuestion.textContent = currentQuestion.question;
  examChoices.innerHTML = '';
  currentQuestion.choices.forEach((choice, index) => {
    const label = document.createElement('label');
    const input = document.createElement('input');
    input.type = 'radio';
    input.name = 'choice';
    input.value = index.toString();
    label.appendChild(input);
    const span = document.createElement('span');
    span.textContent = choice;
    label.appendChild(span);
    examChoices.appendChild(label);
  });
  questionCounter.textContent = `Frage ${examIndex + 1} von ${examQuestions.length}`;
  progressIndicator.style.width = `${((examIndex + 1) / examQuestions.length) * 100}%`;
}

examForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const selected = examForm.querySelector('input[name="choice"]:checked');
  if (!selected) {
    alert('Bitte wählen Sie eine Antwort aus.');
    return;
  }
  const answer = parseInt(selected.value, 10);
  if (answer === examQuestions[examIndex].answer) {
    correctAnswers += 1;
  }
  examIndex += 1;
  if (examIndex < examQuestions.length) {
    renderQuestion();
  } else {
    finishExam();
  }
});

restartExamButton.addEventListener('click', () => {
  examIndex = 0;
  correctAnswers = 0;
  examResult.hidden = true;
  examForm.hidden = false;
  renderQuestion();
});

function finishExam() {
  examForm.hidden = true;
  examResult.hidden = false;
  const percentage = Math.round((correctAnswers / examQuestions.length) * 100);
  examScore.textContent = `Sie haben ${correctAnswers} von ${examQuestions.length} Fragen richtig beantwortet (${percentage} %).`;
  examFeedback.textContent =
    percentage >= 70
      ? 'Herzlichen Glückwunsch! Sie haben die CME-Prüfung bestanden. Ihr Zertifikat wird automatisch generiert.'
      : 'Leider nicht bestanden. Wiederholen Sie die Inhalte und versuchen Sie die Prüfung erneut.';
}

loginForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  if (!email || !password) {
    alert('Bitte geben Sie Ihre Zugangsdaten ein.');
    return;
  }
  authenticated = true;
  loginForm.hidden = true;
  paymentForm.hidden = false;
  paymentForm.querySelector('input').focus();
});

paymentForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const number = document.getElementById('card-number').value.replace(/\s+/g, '');
  const expiry = document.getElementById('card-expiry').value;
  const cvc = document.getElementById('card-cvc').value;

  if (number.length < 12 || !/^(0[1-9]|1[0-2])\/(\d{2})$/.test(expiry) || cvc.length < 3) {
    alert('Bitte geben Sie gültige Zahlungsdaten ein.');
    return;
  }

  paid = true;
  accessGate.hidden = true;
  logoutButton.hidden = false;
  document.body.classList.add('authenticated');
  renderStep(currentStep);
  renderQuestion();
});

logoutButton.addEventListener('click', () => {
  authenticated = false;
  paid = false;
  loginForm.reset();
  paymentForm.reset();
  paymentForm.hidden = true;
  loginForm.hidden = false;
  accessGate.hidden = false;
  logoutButton.hidden = true;
  document.body.classList.remove('authenticated');
  examIndex = 0;
  correctAnswers = 0;
  examForm.hidden = false;
  examResult.hidden = true;
  renderStep(0);
  renderQuestion();
});

// Initial render is deferred until Zugang freigeschaltet ist
renderStep(currentStep);
renderQuestion();
