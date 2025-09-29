import streamlit as st
import random
import time
import pandas as pd

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
    # Ignoriere Klicks, wenn die Zeitmessung nicht läuft (Sicherheitsabfrage)
    if st.session_state.start_time == 0:
        return

    reaction_time = (time.time() - st.session_state.start_time) * 1000
    block_config = IAT_BLOCKS[st.session_state.current_block]
    current_stimulus = st.session_state.stimuli_list[st.session_state.current_trial]
    
    is_correct = (key_pressed == 'e' and current_stimulus['category'] in block_config['left']) or \
                 (key_pressed == 'i' and current_stimulus['category'] in block_config['right'])
        
    # Speichere nur die erste Antwort für jeden Versuch
    if not st.session_state.show_feedback:
        st.session_state.results.append({
            'block': st.session_state.current_block + 1, 'is_critical': block_config.get('is_critical', False),
            'stimulus': current_stimulus['text'], 'correct': is_correct, 'rt': reaction_time
        })
    
    # Stoppuhr nach JEDEM Klick zurücksetzen
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
    
    st.rerun()

def calculate_and_show_results():
    st.title("Testergebnis")
    df = pd.DataFrame(st.session_state.results)
    critical_trials = df[df['is_critical'] & df['correct']]
    
    try:
        avg_rt_block4 = critical_trials[critical_trials['block'] == 4]['rt'].mean()
        avg_rt_block7 = critical_trials[critical_trials['block'] == 7]['rt'].mean()
        iat_effect = avg_rt_block7 - avg_rt_block4

        st.metric(label="Ø Reaktionszeit Block 4 (kongruent)", value=f"{avg_rt_block4:.0f} ms")
        st.metric(
