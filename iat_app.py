import streamlit as st
import random
import time
import pandas as pd
from streamlit_shortcuts import st_shortcuts # KORRIGIERTER IMPORT

# --- 1. Konfiguration des Tests: Kategorien und Stimuli aus dem Paper ---
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

# --- 2. Definition der 7 Testblöcke ---
IAT_BLOCKS = [
    {'left': ['canonical'], 'right': ['non_affordance'], 'stimuli': ['canonical', 'non_affordance'], 'trials': 20, 'is_practice': True},
    {'left': ['useful'], 'right': ['useless'], 'stimuli': ['useful', 'useless'], 'trials': 20, 'is_practice': True},
    {'left': ['canonical', 'useful'], 'right': ['non_affordance', 'useless'], 'stimuli': ['canonical', 'useful', 'non_affordance', 'useless'], 'trials': 20, 'is_practice': True},
    {'left': ['canonical', 'useful'], 'right': ['non_affordance', 'useless'], 'stimuli': ['canonical', 'useful', 'non_affordance', 'useless'], 'trials': 40, 'is_critical': True},
    {'left': ['non_affordance'], 'right': ['canonical'], 'stimuli': ['canonical', 'non_affordance'], 'trials': 20, 'is_practice': True},
    {'left': ['non_affordance', 'useful'], 'right': ['canonical', 'useless'], 'stimuli': ['canonical', 'useful', 'non_affordance', 'useless'], 'trials': 20, 'is_practice': True},
    {'left': ['non_affordance', 'useful'], 'right': ['canonical', 'useless'], 'stimuli': ['canonical', 'useful', 'non_affordance', 'useless'], 'trials': 40, 'is_critical': True}
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

def calculate_and_show_results():
    st.title("Testergebnis")
    df = pd.DataFrame(st.session_state.results)
    critical_trials = df[df['is_critical'] & df['correct']]
    
    try:
        avg_rt_block4 = critical_trials[critical_trials['block'] == 4]['rt'].mean()
        avg_rt_block7 = critical_trials[critical_trials['block'] == 7]['rt'].mean()
        iat_effect = avg_rt_block7 - avg_rt_block4

        st.metric(label="Ø Reaktionszeit Block 4 (kongruent)", value=f"{avg_rt_block4:.0f} ms")
        st.metric(label="Ø Reaktionszeit Block 7 (inkongruent)", value=f"{avg_rt_block7:.0f} ms")
        st.metric(label="IAT-Effekt (Differenz)", value=f"{iat_effect:.0f} ms")
        st.info("Ein positiver IAT-Effekt deutet auf eine implizite Assoziation zwischen 'PowerPoint-Anwendung' und 'Nützlich' hin.")
        with st.expander("Rohdaten anzeigen"): st.dataframe(df)
    except (KeyError, ZeroDivisionError, ValueError):
        st.error("Es konnten keine ausreichenden Daten gesammelt werden, um ein Ergebnis zu berechnen.")

# --- 4. Streamlit App Layout und Logik ---

st.set_page_config(layout="centered")
initialize_state()

if st.session_state.test_phase == 'start':
    st.title("IAT-Demonstration: PowerPoint-Wahrnehmung")
    st.markdown("Ihre Aufgabe: Ordnen Sie die Begriffe, die in der Mitte erscheinen, so schnell wie möglich zu, indem Sie die Tasten 'E' (links) und 'I' (rechts) drücken.")
    if st.button("Test starten", use_container_width=True):
        st.session_state.test_phase = 'break'
        prepare_block(0)
        st.rerun()

elif st.session_state.test_phase == 'break':
    st.header(f"Block {st.session_state.current_block + 1} von {len(IAT_BLOCKS)} beginnt...")
    time.sleep(2)
    st.session_state.test_phase = 'testing'
    st.rerun()

elif st.session_state.test_phase == 'testing':
    block_config = IAT_BLOCKS[st.session_state.current_block]
    current_stimulus = st.session_state.stimuli_list[st.session_state.current_trial]
    
    left_cat_text = "<br>/<br>".join([CATEGORIES[cat] for cat in block_config['left']])
    right_cat_text = "<br>/<br>".join([CATEGORIES[cat] for cat in block_config['right']])

    # === KORRIGIERTER AUFRUF ===
    st_shortcuts(['e', 'i'], key='key_handler')

    # Layout für die Kategorien
    col1, col2 = st.columns(2)
    with col1: st.markdown(f'<p style="color:green; font-size: 20px;">{left_cat_text}</p>', unsafe_allow_html=True)
    with col2: st.markdown(f'<p style="color:blue; font-size: 20px; text-align: right;">{right_cat_text}</p>', unsafe_allow_html=True)
    
    # Stimulus anzeigen
    st.markdown(f'<div style="text-align: center; font-size: 32px; font-weight: bold; padding: 50px 0;">{current_stimulus["text"]}</div>', unsafe_allow_html=True)
    
    if st.session_state.show_feedback:
        st.markdown('<p style="color:red; font-size: 40px; text-align: center;">X</p>', unsafe_allow_html=True)

    # Die Buttons sind jetzt nicht mehr direkt mit den Tasten verknüpft,
    # aber die on_click Logik bleibt für Mausklicks erhalten.
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.button("E", on_click=record_response, args=('e',), use_container_width=True)
    with col_btn2:
        st.button("I", on_click=record_response, args=('i',), use_container_width=True)
    
    # Logik, um auf den Tastendruck von st_shortcuts zu reagieren
    if 'key_handler' in st.session_state and st.session_state.key_handler:
        key_pressed = st.session_state.key_handler
        del st.session_state.key_handler # Reset nach Verarbeitung
        record_response(key_pressed)
        st.rerun()

    if st.session_state.start_time == 0 and not st.session_state.show_feedback:
        st.session_state.start_time = time.time()

elif st.session_state.test_phase == 'end':
    calculate_and_show_results()
    if st.button("Test neu starten", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
