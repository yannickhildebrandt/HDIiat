import streamlit as st
import random
import time
import pandas as pd
from streamlit_keyboard_events import keyboard_events # Wichtig: Die neue Komponente importieren

# --- 1. Konfiguration des Tests: Kategorien und Stimuli aus dem Paper ---
STIMULI = {
    # Zielkonzept: Typische PowerPoint-Anwendungen
    'canonical': ['Trainings durchführen', 'Vorträge erstellen', 'Folien bearbeiten', 'Wissen teilen', 'Präsentation', 'Grafiken präsentieren', 'Verkaufspräsentation', 'Folien erstellen'],
    # Kontrastkonzept: Dinge, die mit PowerPoint nicht gehen
    'non_affordance': ['Datenverschlüsselung', 'Spiele herunterladen', 'Instant Messaging', 'Im Internet surfen', 'Dateien wiederherstellen', 'Musik streamen', 'Online bezahlen', 'Virenscan'],
    # Attribute
    'useful': ['Anwendbar', 'Nützlich', 'Effektiv', 'Praktisch', 'Produktiv', 'Profitabel', 'Wertvoll'],
    'useless': ['Ineffektiv', 'Irrelevant', 'Funktionslos', 'Zwecklos', 'Sinnlos', 'Wertlos', 'Unbrauchbar']
}

# Kategorienamen für die Anzeige (vereinfacht, wie im Paper beschrieben)
CATEGORIES = {
    'canonical': 'PowerPoint-Anwendung',
    'non_affordance': 'Keine PowerPoint-Anwendung',
    'useful': 'Nützlich',
    'useless': 'Nutzlos'
}

# --- 2. Definition der 7 Testblöcke (für IAT 1 aus dem Paper) ---
IAT_BLOCKS = [
    {'left': ['canonical'], 'right': ['non_affordance'], 'stimuli': ['canonical', 'non_affordance'], 'trials': 20, 'is_practice': True},
    {'left': ['useful'], 'right': ['useless'], 'stimuli': ['useful', 'useless'], 'trials': 20, 'is_practice': True},
    # Kongruenter Block (einfache Paarung)
    {'left': ['canonical', 'useful'], 'right': ['non_affordance', 'useless'], 'stimuli': ['canonical', 'useful', 'non_affordance', 'useless'], 'trials': 20, 'is_practice': True},
    {'left': ['canonical', 'useful'], 'right': ['non_affordance', 'useless'], 'stimuli': ['canonical', 'useful', 'non_affordance', 'useless'], 'trials': 40, 'is_critical': True},
    # Umkehrung
    {'left': ['non_affordance'], 'right': ['canonical'], 'stimuli': ['canonical', 'non_affordance'], 'trials': 20, 'is_practice': True},
    # Inkongruenter Block (schwierige Paarung)
    {'left': ['non_affordance', 'useful'], 'right': ['canonical', 'useless'], 'stimuli': ['canonical', 'useful', 'non_affordance', 'useless'], 'trials': 20, 'is_practice': True},
    {'left': ['non_affordance', 'useful'], 'right': ['canonical', 'useless'], 'stimuli': ['canonical', 'useful', 'non_affordance', 'useless'], 'trials': 40, 'is_critical': True}
]

# --- 3. Funktionen zur Steuerung des Tests ---

def initialize_state():
    """Initialisiert den Session State für einen neuen Testdurchlauf."""
    st.session_state.test_phase = 'start'
    st.session_state.current_block = 0
    st.session_state.current_trial = 0
    st.session_state.results = []
    st.session_state.stimuli_list = []
    st.session_state.start_time = 0
    st.session_state.show_feedback = False
    st.session_state.key_counter = 0 # Wichtig für die Keyboard-Komponente

def prepare_block(block_index):
    """Bereitet die Stimuli-Liste für einen neuen Block vor."""
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
    """Verarbeitet die Antwort des Nutzers, misst die Zeit und speichert das Ergebnis."""
    if not key_pressed or st.session_state.start_time == 0:
        return

    reaction_time = (time.time() - st.session_state.start_time) * 1000
    
    block_config = IAT_BLOCKS[st.session_state.current_block]
    current_stimulus = st.session_state.stimuli_list[st.session_state.current_trial]
    
    is_correct = False
    if key_pressed.lower() == 'e' and current_stimulus['category'] in block_config['left']:
        is_correct = True
    elif key_pressed.lower() == 'i' and current_stimulus['category'] in block_config['right']:
        is_correct = True
        
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
                st.session_state.test_phase = 'break' # Pause zwischen den Blöcken
    else:
        st.session_state.show_feedback = True

def calculate_and_show_results():
    st.title("Testergebnis")
    df = pd.DataFrame(st.session_state.results)
    
    critical_trials = df[(df['is_critical'] == True) & (df['correct'] == True)]
    
    try:
        avg_rt_block4 = critical_trials[critical_trials['block'] == 4]['rt'].mean()
        avg_rt_block7 = critical_trials[critical_trials['block'] == 7]['rt'].mean()
        iat_effect = avg_rt_block7 - avg_rt_block4

        st.metric(label="Ø Reaktionszeit Block 4 (kongruent)", value=f"{avg_rt_block4:.0f} ms")
        st.metric(label="Ø Reaktionszeit Block 7 (inkongruent)", value=f"{avg_rt_block7:.0f} ms")
        st.metric(label="IAT-Effekt (Differenz)", value=f"{iat_effect:.0f} ms")

        if iat_effect > 200:
            result_text = "Ihr Ergebnis deutet auf eine **starke implizite Assoziation** zwischen 'PowerPoint-Anwendung' und 'Nützlich' hin."
        else:
            result_text = "Ihr Ergebnis deutet auf eine **schwache oder keine klare implizite Assoziation** hin."
        
        st.info(result_text)
        st.warning("Hinweis: Dies ist eine Demonstration. Die Reaktionszeiten sind aufgrund technischer Latenzen nicht für wissenschaftliche Zwecke geeignet.")

        with st.expander("Rohdaten anzeigen"): st.dataframe(df)
            
    except (KeyError, ZeroDivisionError, ValueError):
        st.error("Es konnten keine ausreichenden Daten gesammelt werden, um ein Ergebnis zu berechnen.")

# --- 4. Streamlit App Layout und Logik ---

st.set_page_config(layout="centered")

if 'test_phase' not in st.session_state:
    initialize_state()

# --- Ansicht 1: Startbildschirm ---
if st.session_state.test_phase == 'start':
    st.title("IAT-Demonstration: PowerPoint-Wahrnehmung")
    st.markdown("""
    Willkommen! Diese App demonstriert den Impliziten Assoziationstest (IAT) basierend auf dem Paper.
    
    **Ihre Aufgabe:**
    Ordnen Sie die in der Mitte angezeigten Begriffe so schnell wie möglich einer der beiden Kategorien zu.
    
    - Drücken Sie die **Taste 'E'** für die linke Kategorie.
    - Drücken Sie die **Taste 'I'** für die rechte Kategorie.
    
    Seien Sie schnell, aber versuchen Sie, Fehler zu vermeiden.
    """)
    if st.button("Test starten", use_container_width=True):
        st.session_state.test_phase = 'break'
        prepare_block(0)
        st.rerun()

# --- Zwischenbildschirm für Pausen ---
elif st.session_state.test_phase == 'break':
    block_num = st.session_state.current_block + 1
    st.header(f"Block {block_num} von {len(IAT_BLOCKS)} beginnt in Kürze.")
    st.info("Machen Sie sich bereit, die Tasten 'E' und 'I' zu verwenden.")
    
    block_config = IAT_BLOCKS[st.session_state.current_block]
    left_cat_text = "<br>/<br>".join([CATEGORIES[cat] for cat in block_config['left']])
    right_cat_text = "<br>/<br>".join([CATEGORIES[cat] for cat in block_config['right']])
    
    col1, col2 = st.columns(2)
    with col1: st.markdown(f'<p style="color:green; font-size: 20px; text-align: left;">{left_cat_text}</p>', unsafe_allow_html=True)
    with col2: st.markdown(f'<p style="color:blue; font-size: 20px; text-align: right;">{right_cat_text}</p>', unsafe_allow_html=True)
    
    time.sleep(3) # Automatische Pause
    st.session_state.test_phase = 'testing'
    st.rerun()


# --- Ansicht 2: Der eigentliche Test ---
elif st.session_state.test_phase == 'testing':
    block_config = IAT_BLOCKS[st.session_state.current_block]
    current_stimulus = st.session_state.stimuli_list[st.session_state.current_trial]
    
    left_cat_text = "<br>/<br>".join([CATEGORIES[cat] for cat in block_config['left']])
    right_cat_text = "<br>/<br>".join([CATEGORIES[cat] for cat in block_config['right']])
    
    # Keyboard-Listener-Komponente. Sie fängt die Tastendrücke ab.
    key_event = keyboard_events(
        events=['e', 'i'],
        key=f"key_event_{st.session_state.key_counter}", # Einzigartiger Key, um Neuausführung zu erzwingen
    )

    if key_event:
        st.session_state.key_counter += 1
        record_response(key_event[0]['key'])
        st.rerun()

    col1, col2 = st.columns(2)
    with col1: st.markdown(f'<p style="color:green; font-size: 20px; text-align: left;">{left_cat_text}</p>', unsafe_allow_html=True)
    with col2: st.markdown(f'<p style="color:blue; font-size: 20px; text-align: right;">{right_cat_text}</p>', unsafe_allow_html=True)
    
    st.markdown(f'<hr style="margin-top: -10px;">', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: center; font-size: 32px; font-weight: bold; padding: 50px 0;">{current_stimulus["text"]}</div>', unsafe_allow_html=True)
    
    if st.session_state.show_feedback:
        st.markdown('<p style="color:red; font-size: 40px; text-align: center;">X</p>', unsafe_allow_html=True)

    if st.session_state.start_time == 0 and not st.session_state.show_feedback:
        st.session_state.start_time = time.time()
        
    st.markdown(f'<hr>', unsafe_allow_html=True)
    st.caption(f"Block {st.session_state.current_block + 1}/{len(IAT_BLOCKS)} | Versuch {st.session_state.current_trial + 1}/{len(st.session_state.stimuli_list)}")


# --- Ansicht 3: Endbildschirm ---
elif st.session_state.test_phase == 'end':
    calculate_and_show_results()
    if st.button("Test neu starten", use_container_width=True):
        initialize_state()
        st.rerun()
