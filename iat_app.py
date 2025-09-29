import streamlit as st
import random
import time
import pandas as pd

# --- Globale Konfiguration für das UI-Design ---
HDI_GREEN = "#007a52"
HDI_DARK_GRAY = "#333333"
HDI_LIGHT_GRAY = "#f5f5f5"
HDI_RED = "#d9534f"

# --- 1. Konfiguration des Tests: Kategorien und Stimuli ---
STIMULI = {
    'canonical': ['Trainings durchführen', 'Vorträge erstellen', 'Folien bearbeiten', 'Wissen teilen', 'Präsentation', 'Grafiken präsentieren', 'Verkaufspräsentation', 'Folien erstellen'],
    'non_affordance': ['Datenverschlüsselung', 'Spiele herunterladen', 'Instant Messaging', 'Im Internet surfen', 'Dateien wiederherstellen', 'Musik streamen', 'Online bezahlen', 'Virenscan'],
    'useful': ['Anwendbar', 'Nützlich', 'Effektiv', 'Praktisch', 'Produktiv', 'Profitabel', 'Wertvoll'],
    'useless': ['Ineffektiv', 'Irrelevant', 'Funktionslos', 'Zwecklos', 'Sinnlos', 'Wertlos', 'Unbrauchbar']
}
CATEGORIES = {
    'canonical': 'PowerPoint-Anwendung',
    'non_affordance': 'Keine PowerPoint-Anwendung',
    'useful': 'Nützlich',
    'useless': 'Nutzlos'
}
IAT_BLOCKS = [
    {'left': ['canonical'], 'right': ['non_affordance'], 'stimuli': ['canonical', 'non_affordance'], 'trials': 20, 'is_practice': True, 'name': 'Kategorisierung: Anwendung'},
    {'left': ['useful'], 'right': ['useless'], 'stimuli': ['useful', 'useless'], 'trials': 20, 'is_practice': True, 'name': 'Kategorisierung: Bewertung'},
    {'left': ['canonical', 'useful'], 'right': ['non_affordance', 'useless'], 'stimuli': ['canonical', 'useful', 'non_affordance', 'useless'], 'trials': 20, 'is_practice': True, 'name': 'Kombination 1 (Übung)'},
    {'left': ['canonical', 'useful'], 'right': ['non_affordance', 'useless'], 'stimuli': ['canonical', 'useful', 'non_affordance', 'useless'], 'trials': 40, 'is_critical': True, 'name': 'Kombination 1 (Test)'},
    {'left': ['non_affordance'], 'right': ['canonical'], 'stimuli': ['canonical', 'non_affordance'], 'trials': 20, 'is_practice': True, 'name': 'Umgewöhnung: Anwendung'},
    {'left': ['non_affordance', 'useful'], 'right': ['canonical', 'useless'], 'stimuli': ['canonical', 'useful', 'non_affordance', 'useless'], 'trials': 20, 'is_practice': True, 'name': 'Kombination 2 (Übung)'},
    {'left': ['non_affordance', 'useful'], 'right': ['canonical', 'useless'], 'stimuli': ['canonical', 'useful', 'non_affordance', 'useless'], 'trials': 40, 'is_critical': True, 'name': 'Kombination 2 (Test)'}
]

# --- 3. Funktionen zur Steuerung des Tests ---
def initialize_state():
    if 'test_phase' not in st.session_state:
        st.session_state.test_phase = 'start'
        st.session_state.current_block = 0
        st.session_state.current_trial = 0
        st.session_state.results = []
        st.session_state.stimuli_list = []
        st.session_state.start_time = 0
        st.session_state.show_feedback = False

def prepare_block(block_index):
    block_config = IAT_BLOCKS[block_index]
    stimuli_for_block = []
    for cat in block_config['stimuli']:
        for stimulus_text in STIMULI[cat]:
            stimuli_for_block.append({'text': stimulus_text, 'category': cat})
    full_stimulus_list = []
    while len(full_stimulus_list) < block_config['trials']:
        random.shuffle(stimuli_for_block)
        full_stimulus_list.extend(stimuli_for_block)
    st.session_state.stimuli_list = full_stimulus_list[:block_config['trials']]
    st.session_state.current_trial = 0

def record_response(key_pressed):
    if st.session_state.start_time == 0: return
    reaction_time = (time.time() - st.session_state.start_time) * 1000
    block_config = IAT_BLOCKS[st.session_state.current_block]
    current_stimulus = st.session_state.stimuli_list[st.session_state.current_trial]
    is_correct = (key_pressed == 'e' and current_stimulus['category'] in block_config['left']) or \
                 (key_pressed == 'i' and current_stimulus['category'] in block_config['right'])
    if not st.session_state.show_feedback:
        st.session_state.results.append({
            'block': st.session_state.current_block + 1, 'is_critical': block_config.get('is_critical', False),
            'stimulus': current_stimulus['text'], 'correct': is_correct, 'rt': reaction_time
        })
    st.session_state.start_time = 0
    if is_correct:
        st.session_state.show_feedback = False
        st.session_state.current_trial += 1
        if st.session_state.current_trial >= len(st.session_state.stimuli_list):
            st.session_state.current_block += 1
            if st.session_state.current_block >= len(IAT_BLOCKS):
                st.session_state.test_phase = 'end'
            else:
                st.session_state.test_phase = 'break'
    else:
        st.session_state.show_feedback = True

# --- 4. UI-Komponenten und Styling (Light Version) ---
def load_css():
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {HDI_LIGHT_GRAY}; }}
        .stApp, .stMarkdown, h1, h2, h3, h4, h5, h6 {{ color: {HDI_DARK_GRAY}; }}
        .stButton>button {{ background-color: {HDI_GREEN}; color: white; border-radius: 8px; padding: 12px 24px; font-size: 1.1rem; font-weight: bold; border: none; transition: background-color 0.3s ease; }}
        .stButton>button:hover {{ background-color: #005a41; color: white; }}
        .stButton>button[kind="secondary"] {{ height: 150px; white-space: pre-wrap; font-size: 1.2rem; background-color: white; color: {HDI_DARK_GRAY}; border: 2px solid #ddd; }}
        .stButton>button[kind="secondary"]:hover {{ border-color: {HDI_GREEN}; background-color: #f9f9f9; }}
        .stimulus-text {{ text-align: center; font-size: 2.8rem; font-weight: bold; padding: 50px 0; color: {HDI_GREEN}; }}
        .feedback-x {{ color: {HDI_RED}; font-size: 4rem; text-align: center; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

def show_footer():
    st.write("")
    st.markdown("---")
    st.markdown("""<div style='text-align: center; color: #888; font-size: 0.9rem;'>
        Ein Tool von <b>Eggers & Partner Consulting</b><br>
        entwickelt von <i>Dr. Yannick Hildebrandt</i>
        </div>""", unsafe_allow_html=True)

def jump_to_end_for_debug():
    st.session_state.results = [
        {'block': 4, 'is_critical': True, 'stimulus': 'Debug', 'correct': True, 'rt': 650 + random.randint(-50, 50)},
        {'block': 4, 'is_critical': True, 'stimulus': 'Debug', 'correct': True, 'rt': 750 + random.randint(-50, 50)},
        {'block': 7, 'is_critical': True, 'stimulus': 'Debug', 'correct': True, 'rt': 950 + random.randint(-50, 50)},
        {'block': 7, 'is_critical': True, 'stimulus': 'Debug', 'correct': True, 'rt': 1050 + random.randint(-50, 50)},
    ]
    st.session_state.test_phase = 'end'

def show_start_page():
    st.title("Impliziter Assoziationstest (IAT)")
    st.subheader("Ihre unbewusste Einstellung zu PowerPoint")
    st.info("**Willkommen!** Dieser interaktive Test ist Teil des HDI-Workshops zum Thema **'Digitales Mindset'**.", icon="💡")

    with st.container(border=True):
        st.markdown("#### 🧠 Was ist ein Impliziter Assoziationstest?")
        st.markdown("Der IAT misst die Stärke unbewusster Assoziationen...") # Gekürzt zur Lesbarkeit
    with st.container(border=True):
        st.markdown("#### 🎯 Ihre Aufgabe")
        st.markdown("1. **Kategorien beachten:** ...") # Gekürzt zur Lesbarkeit
    st.write("")
    if st.button("Ich bin bereit, den Test zu starten!", use_container_width=True):
        st.session_state.test_phase = 'break'
        prepare_block(0)
        st.rerun()
    with st.expander("⚙️ Debug-Optionen"):
        st.button("Direkt zur Ergebnisseite springen (Layout-Test)", on_click=jump_to_end_for_debug, use_container_width=True, type="secondary")
    show_footer()

def show_break_screen():
    block_config = IAT_BLOCKS[st.session_state.current_block]
    progress_percent = (st.session_state.current_block) / len(IAT_BLOCKS)
    st.header(f"Block {st.session_state.current_block + 1} von {len(IAT_BLOCKS)}")
    st.subheader(f"Thema: {block_config['name']}")
    st.progress(progress_percent, text=f"{int(progress_percent*100)}% abgeschlossen")
    st.write("")
    countdown_placeholder = st.empty()
    BREAK_DURATION = 5
    for i in range(BREAK_DURATION, 0, -1):
        countdown_placeholder.markdown(f"<h1 style='text-align: center; font-size: 5rem; color: {HDI_GREEN};'>{i}</h1>", unsafe_allow_html=True)
        time.sleep(1)
    countdown_placeholder.markdown(f"<h1 style='text-align: center; color: {HDI_GREEN};'>Los geht's!</h1>", unsafe_allow_html=True)
    time.sleep(1)
    st.session_state.test_phase = 'testing'
    prepare_block(st.session_state.current_block)
    st.rerun()

def show_testing_interface():
    block_config = IAT_BLOCKS[st.session_state.current_block]
    current_stimulus = st.session_state.stimuli_list[st.session_state.current_trial]
    left_label = "\noder\n".join([CATEGORIES[cat] for cat in block_config['left']])
    right_label = "\noder\n".join([CATEGORIES[cat] for cat in block_config['right']])

    st.markdown(f'<div class="stimulus-text">{current_stimulus["text"]}</div>', unsafe_allow_html=True)
    if st.session_state.show_feedback:
        st.markdown('<p class="feedback-x">X</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:white; font-size: 4rem;">X</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1: st.button(left_label, on_click=record_response, args=('e',), use_container_width=True, key=f'btn_e_{st.session_state.current_trial}', type="secondary")
    with col2: st.button(right_label, on_click=record_response, args=('i',), use_container_width=True, key=f'btn_i_{st.session_state.current_trial}', type="secondary")
    if st.session_state.start_time == 0:
        st.session_state.start_time = time.time()
        time.sleep(0.01)

def calculate_and_show_results():
    st.title("📊 Ihr IAT-Ergebnis")
    df = pd.DataFrame(st.session_state.results)
    critical_trials = df[df['is_critical'] & df['correct']]
    try:
        avg_rt_block4 = critical_trials[critical_trials['block'] == 4]['rt'].mean()
        avg_rt_block7 = critical_trials[critical_trials['block'] == 7]['rt'].mean()
        if pd.isna(avg_rt_block4) or pd.isna(avg_rt_block7): raise ValueError("Nicht genügend Daten.")
        iat_effect = avg_rt_block7 - avg_rt_block4

        with st.container(border=True):
            st.subheader("Ihre implizite Neigung auf einen Blick")
            if iat_effect > 50: st.success(f"**Positive Tendenz:** Sie assoziieren 'PowerPoint-Anwendung' implizit eher mit **'Nützlich'**.")
            elif iat_effect < -50: st.warning(f"**Negative Tendenz:** Sie assoziieren 'PowerPoint-Anwendung' implizit eher mit **'Nutzlos'**.")
            else: st.info("**Neutrale Tendenz:** Ihre impliziten Assoziationen sind weitgehend ausgeglichen.")
        
        with st.container(border=True):
            st.subheader("⏱️ Detailauswertung")
            col1, col2, col3 = st.columns(3)
            with col1: st.metric(label="Ø Zeit (PP + Nützlich)", value=f"{avg_rt_block4:.0f} ms")
            with col2: st.metric(label="Ø Zeit (PP + Nutzlos)", value=f"{avg_rt_block7:.0f} ms")
            with col3: st.metric(label="IAT-Effekt (Differenz)", value=f"{iat_effect:.0f} ms")
            st.markdown("---")
            st.markdown("""<p><b>Wie kommt das Ergebnis zustande?</b>...</p><p><b>Wichtiger Hinweis:</b>...</p>""", unsafe_allow_html=True)
            
    except (KeyError, ZeroDivisionError, ValueError) as e:
        st.error(f"Es konnten keine ausreichenden Daten gesammelt werden. Bitte versuchen Sie es erneut. Fehler: {e}")
    
    st.write("")
    if st.button("Test erneut durchführen", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    show_footer()

# --- 5. Hauptlogik der Streamlit App ---
st.set_page_config(layout="centered", page_title="IAT PowerPoint")
load_css()
initialize_state()

if st.session_state.test_phase == 'start': show_start_page()
elif st.session_state.test_phase == 'break': show_break_screen()
elif st.session_state.test_phase == 'testing': show_testing_interface()
elif st.session_state.test_phase == 'end': calculate_and_show_results()
