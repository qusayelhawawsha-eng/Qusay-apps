"""QUSAY Cases - a patient decision game
Run with:  streamlit run game.py

Each option is (text, points, feedback). 2 = best, 1 = acceptable, 0 = wrong.
To add a case, copy one block in CASES and change the text.
"""

import streamlit as st

st.set_page_config(page_title="QUSAY Cases", page_icon="🩺")

CASES = [
    {
        "title": "Chest pain in the emergency department",
        "intro": (
            "A 58-year-old man arrives with 40 minutes of crushing central chest pain "
            "spreading to his left arm. He is sweating. BP 150/90, HR 98, SpO2 97%."
        ),
        "steps": [
            {
                "q": "What is your first action?",
                "options": [
                    ("Record a 12-lead ECG within 10 minutes", 2,
                     "Correct. The ECG decides the pathway and should be done within 10 minutes of arrival."),
                    ("Send troponin and wait for the result", 0,
                     "Troponin takes time. A STEMI is diagnosed on the ECG and must not wait for blood tests."),
                    ("Give an antacid and observe", 0,
                     "Do not assume indigestion. Crushing chest pain with sweating needs an ECG first."),
                ],
            },
            {
                "q": "The ECG shows ST elevation in leads II, III and aVF. What now?",
                "options": [
                    ("Activate the primary PCI (cath lab) pathway immediately", 2,
                     "Correct. Primary PCI is the preferred reperfusion treatment when it can be done quickly."),
                    ("Give thrombolysis straight away", 1,
                     "Thrombolysis is an option only when PCI cannot be delivered in time. Where PCI is available, it is preferred."),
                    ("Wait for an echocardiogram first", 0,
                     "Time is muscle. Reperfusion should not wait for further imaging."),
                ],
            },
            {
                "q": "Which treatment do you give while arranging transfer?",
                "options": [
                    ("An aspirin loading dose (commonly 150-300 mg orally, per local protocol)", 2,
                     "Correct. Aspirin plus other antithrombotic treatment per protocol is standard."),
                    ("Ibuprofen for the pain", 0,
                     "NSAIDs are avoided in acute myocardial infarction. They raise cardiovascular risk. Use appropriate analgesia per protocol."),
                    ("High-flow oxygen to every patient", 1,
                     "Routine oxygen is not recommended when SpO2 is 90% or above. Give it only if saturation is low."),
                ],
            },
        ],
        "learning": [
            "STEMI is an ECG diagnosis. Do not wait for troponin.",
            "Primary PCI is preferred when it can be done in time.",
            "Avoid NSAIDs in acute MI, and give oxygen only if saturation is low.",
        ],
    },
    {
        "title": "Wasp sting and a collapsing patient",
        "intro": (
            "A 24-year-old woman was stung by a wasp 10 minutes ago. She has widespread hives, "
            "swollen lips, wheeze and dizziness. BP 80/50, HR 125."
        ),
        "steps": [
            {
                "q": "Which drug do you give first?",
                "options": [
                    ("Adrenaline intramuscularly into the outer thigh (adult dose 0.5 mg)", 2,
                     "Correct. IM adrenaline is first-line and must not be delayed."),
                    ("IV hydrocortisone", 0,
                     "Steroids act slowly and are not first-line. They never replace adrenaline."),
                    ("An oral antihistamine", 0,
                     "Antihistamines help the skin but do not treat airway or circulation problems."),
                ],
            },
            {
                "q": "What else do you do straight away?",
                "options": [
                    ("Lay her flat with legs raised, give oxygen and IV fluids", 2,
                     "Correct. This treats low blood pressure. If breathing is difficult, a semi-sitting position is acceptable, but do not make her stand."),
                    ("Sit her upright and let her walk to the next room", 0,
                     "Standing up with severe hypotension in anaphylaxis can cause cardiac arrest."),
                    ("Wait and watch for 30 minutes", 0,
                     "Anaphylaxis can worsen within minutes. Act at once."),
                ],
            },
            {
                "q": "After 5 minutes there is no improvement. What now?",
                "options": [
                    ("Repeat IM adrenaline", 2,
                     "Correct. The IM dose can be repeated after 5 minutes if there is no improvement."),
                    ("Start an IV adrenaline bolus on the ward", 1,
                     "IV adrenaline is for experienced specialists with continuous monitoring, not a routine step."),
                    ("Wait another 30 minutes", 0,
                     "Delay is dangerous. Repeat the adrenaline and call for help."),
                ],
            },
        ],
        "learning": [
            "Adrenaline IM is first-line, and steroids and antihistamines come later.",
            "Hypotensive patients lie flat with legs raised.",
            "Repeat IM adrenaline after 5 minutes if there is no response.",
        ],
    },
    {
        "title": "Swollen lips on a blood pressure drug (pharmacovigilance case)",
        "intro": (
            "A 67-year-old man has taken lisinopril and amlodipine for 3 years. Since this "
            "morning his lips and tongue are swollen. No hives, no itching. His voice is "
            "slightly muffled. SpO2 96%."
        ),
        "steps": [
            {
                "q": "What is your most urgent concern?",
                "options": [
                    ("Assess the airway and prepare for airway support", 2,
                     "Correct. Tongue swelling and a changed voice can threaten the airway."),
                    ("Give an antihistamine and send him home", 0,
                     "Unsafe. This type of angioedema may not respond to antihistamines and the airway can close."),
                    ("Take a full allergy history before doing anything else", 1,
                     "The history matters, but the airway comes first."),
                ],
            },
            {
                "q": "What is the likely cause, and what do you do about the medicine?",
                "options": [
                    ("Suspect ACE-inhibitor angioedema and stop lisinopril", 2,
                     "Correct. It can appear even after years of use. Do not restart it."),
                    ("Continue lisinopril and add an antihistamine", 0,
                     "Continuing the suspected drug risks a worse, life-threatening episode."),
                    ("Switch to another ACE inhibitor such as enalapril", 0,
                     "This is a class effect, so all ACE inhibitors should be avoided."),
                ],
            },
            {
                "q": "What is your pharmacovigilance action?",
                "options": [
                    ("Report it as a suspected adverse drug reaction (in Bulgaria, a yellow card to the Bulgarian Drug Agency)", 2,
                     "Correct. Serious reactions should be reported even when the effect is already known."),
                    ("Do not report because it is a known side effect", 0,
                     "Known reactions still need reporting. Reports show how often serious cases happen."),
                    ("Write it in the patient chart only", 1,
                     "Good for the patient's record, but it does not reach the safety system."),
                ],
            },
        ],
        "learning": [
            "ACE-inhibitor angioedema is a class effect and can occur years after starting.",
            "Airway first, then stop the drug and avoid the whole class.",
            "Report serious suspected reactions even when they are known.",
        ],
    },
]


# ---------------------------------------------------------------
# Game state
# ---------------------------------------------------------------
if "case" not in st.session_state:
    st.session_state.case = None
    st.session_state.step = 0
    st.session_state.score = 0
    st.session_state.answered = None


def start(index):
    st.session_state.case = index
    st.session_state.step = 0
    st.session_state.score = 0
    st.session_state.answered = None


def answer(choice):
    case = CASES[st.session_state.case]
    points = case["steps"][st.session_state.step]["options"][choice][1]
    st.session_state.score += points
    st.session_state.answered = choice


def next_step():
    st.session_state.step += 1
    st.session_state.answered = None


def to_menu():
    st.session_state.case = None


# ---------------------------------------------------------------
# Screens
# ---------------------------------------------------------------
st.title("QUSAY Cases")

if st.session_state.case is None:
    st.write(
        "Make decisions as the doctor in short patient cases. Each decision "
        "gives you feedback and points. Choose a case:"
    )
    for i, case in enumerate(CASES):
        st.button(case["title"], key=f"case{i}", on_click=start, args=(i,), width="stretch")
    st.caption(
        "For learning only. Cases are simplified and are not a substitute for "
        "current local guidelines."
    )
    st.stop()

case = CASES[st.session_state.case]
steps = case["steps"]
step = st.session_state.step
max_score = 2 * len(steps)

st.subheader(case["title"])
st.info(case["intro"])

if step >= len(steps):
    score = st.session_state.score
    st.progress(1.0)
    st.header(f"Score: {score} / {max_score}")
    ratio = score / max_score
    if ratio >= 0.85:
        st.success("Excellent. Strong clinical judgment.")
    elif ratio >= 0.5:
        st.warning("Good effort. Review the key points below and try again.")
    else:
        st.error("This case was hard. Read the key points and play it again.")
    st.markdown("**Key learning points**")
    for point in case["learning"]:
        st.write("- " + point)
    left, right = st.columns(2)
    left.button("Play this case again", on_click=start, args=(st.session_state.case,), width="stretch")
    right.button("Choose another case", on_click=to_menu, width="stretch")
    st.stop()

current = steps[step]
st.progress(step / len(steps))
st.markdown(f"**Decision {step + 1} of {len(steps)}:** {current['q']}")
options = current["options"]

if st.session_state.answered is None:
    choice = st.radio(
        "Your decision",
        range(len(options)),
        format_func=lambda i: options[i][0],
        index=None,
        key=f"radio_{st.session_state.case}_{step}",
    )
    st.button("Confirm decision", disabled=choice is None, on_click=answer, args=(choice,))
else:
    chosen = options[st.session_state.answered]
    text, points, feedback = chosen
    st.write(f"You chose: **{text}**")
    if points == 2:
        st.success(f"+2 points. {feedback}")
    elif points == 1:
        st.warning(f"+1 point. {feedback}")
    else:
        st.error(f"0 points. {feedback}")
        best = max(options, key=lambda o: o[1])
        st.write(f"Best answer: **{best[0]}**")
    last = step == len(steps) - 1
    st.button("See result" if last else "Next decision", on_click=next_step)

st.caption(f"Current score: {st.session_state.score} / {max_score}")
