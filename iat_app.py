import streamlit as st
import random
import time
import pandas as pd

# --- 1. Konfiguration des Tests: Kategorien und Stimuli ---
STIMULI = {
    'ki_partner': ['KI-Assistent', 'Kreativpartner', 'Analysewerkzeug', 'Ideengeber', 'Co-Pilot', 'Lernhilfe', 'Problemlöser', 'Automatisierungshilfe'],
    'ki_ersatz': ['Job-Automatisierung', 'Menschlicher Ersatz', 'Konkurrent', 'Kontrollinstanz', 'Entscheider', 'Überwachung', 'Machtübernahme', 'Verdrängung'],
    'chance': ['Fortschritt', 'Potenzial', 'Hoffnung', 'Gewinn', 'Vorteil', 'Entwicklung', 'Innovation', 'Wachstum'],
    'gefahr': ['Risiko', 'Bedrohung', 'Verlust', 'Angst', 'Nachteil', 'Krise', 'Unsicherheit', 'Rückschritt']
}

CATEGORIES = {
    'ki_partner': 'KI als Partner',
    'ki_ersatz': 'KI als Ersatz',
    'chance': 'Chance',
    'gefahr': 'Gefahr'
}

# --- 2. Definition der 7 Testblöcke ---
IAT_BLOCKS = [
    # Block 1: Übung Zielkonzepte
    {'left': ['ki_partner'], 'right': ['ki_ersatz'], 'stimuli': ['ki_partner', 'ki_ersatz'], 'trials': 16, 'is_practice': True},
    # Block 2: Übung Attribute
    {'left': ['chance'], 'right': ['gefahr'], 'stimuli': ['chance', 'gefahr'], 'trials': 16, 'is_practice': True},
    # Block 3: Kombinierte Übung (kongruent)
    {'left': ['ki_partner', 'chance'], 'right': ['ki_ersatz', 'gefahr'], 'stimuli': ['ki_partner', 'chance', 'ki_ersatz', 'gefahr'], 'trials': 16, 'is_practice': True},
    # Block 4: Kombinierter Test (kongruent) - Messung
    {'left': ['ki_partner', 'chance'], 'right': ['ki_ersatz', 'gefahr'], 'stimuli': ['ki_partner', 'chance', 'ki_ersatz', 'gefahr'], 'trials': 32, 'is_critical': True},
    # Block 5: Übung Zielkonzepte (umgekehrt)
    {'left': ['ki_ersatz'], 'right': ['ki_partner'], 'stimuli': ['ki_partner', 'ki_ersatz'], 'trials': 16, 'is_practice': True},
    # Block 6: Kombinierte Übung (inkongruent)
    {'left': ['ki_ersatz', 'chance'], 'right': ['ki_partner', 'gefahr'], 'stimuli': ['ki_partner', 'chance', 'ki_ersatz', 'gefahr'], 'trials': 16, 'is_practice': True},
    # Block 7: Kombinierter Test (inkongruent) - Messung
    {'left': ['ki_ersatz', 'chance'], 'right': ['ki_partner', 'gefahr'], 'stimuli': ['ki_partner', 'chance', 'ki_ersatz', 'gefahr'], 'trials': 32, 'is_critical': True}
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
    
def prepare_block(block_index):
    """Bereitet die Stimuli-Liste für einen neuen Block vor."""
    block_config = IAT_BLOCKS[block_index]
    stimuli_for_block = []
    for cat in block_config['stimuli']:
        for stimulus_text in STIMULI[cat]:
            stimuli_for_block.append({'text': stimulus_text, 'category': cat})
    
    # Mische die Stimuli und kürze sie auf die gewünschte Anzahl an Versuchen
    random.shuffle(stimuli_for_block)
    st.session_state.stimuli_list = stimuli_for_block[:block_config['trials']]
    st.session_state.current_trial = 0

def record_response(key_pressed):
    """Verarbeitet die Antwort des Nutzers, misst die Zeit und speichert das Ergebnis."""
    # Nur reagieren, wenn eine Zeitmessung läuft
    if st.session_state.start_time == 0:
        return

    reaction_time = (time.time() - st.session_state.start_time) * 1000 # in Millisekunden
    
    block_config = IAT_BLOCKS[st.session_state.current_block]
    current_stimulus = st.session_state.stimuli_list[st.session_state.current_trial]
    
    # Korrektheit prüfen
    is_correct = False
    if key_pressed == 'e' and current_stimulus['category'] in block_config['left']:
        is_correct = True
    elif key_pressed == 'i' and current_stimulus['category'] in block_config['right']:
        is_correct = True
        
    # Ergebnis speichern
    st.session_state.results.append({
        'block': st.session_state.current_block + 1,
        'trial': st.session_state.current_trial + 1,
        'stimulus': current_stimulus['text'],
        'category': current_stimulus['category'],
        'is_critical': block_config.get('is_critical', False),
        'key_pressed': key_pressed,
        'correct': is_correct,
        'rt': reaction_time
    })
    
    st.session_state.start_time = 0 # Zeitmessung stoppen
    
    if is_correct:
        st.session_state.show_feedback = False
        # Zum nächsten Versuch übergehen
        st.session_state.current_trial += 1
        if st.session_state.current_trial >= len(st.session_state.stimuli_list):
            st.session_state.current_block += 1
            if st.session_state.current_block >= len(IAT_BLOCKS):
                st.session_state.test_phase = 'end'
            else:
                # Nächsten Block vorbereiten
                prepare_block(st.session_state.current_block)
    else:
        # Falsche Antwort: Feedback anzeigen
        st.session_state.show_feedback = True


def calculate_and_show_results():
    """Berechnet und zeigt das Endergebnis an."""
    st.title("Testergebnis")
    df = pd.DataFrame(st.session_state.results)
    
    # Nur korrekte Antworten in den kritischen Blöcken (4 und 7) berücksichtigen
    critical_trials = df[(df['is_critical'] == True) & (df['correct'] == True)]
    
    try:
        avg_rt_block4 = critical_trials[critical_trials['block'] == 4]['rt'].mean()
        avg_rt_block7 = critical_trials[critical_trials['block'] == 7]['rt'].mean()
        iat_effect = avg_rt_block7 - avg_rt_block4

        st.metric(label="Ø Reaktionszeit Block 4 (kongruent)", value=f"{avg_rt_block4:.0f} ms")
        st.metric(label="Ø Reaktionszeit Block 7 (inkongruent)", value=f"{avg_rt_block7:.0f} ms")
        st.metric(label="IAT-Effekt (Differenz)", value=f"{iat_effect:.0f} ms")

        if iat_effect > 200:
            result_text = "Ihr Ergebnis deutet auf eine **starke implizite Assoziation** zwischen 'KI als Partner' und 'Chance' hin. Sie waren deutlich schneller, als diese beiden Konzepte zusammengehörten."
        elif iat_effect > 50:
            result_text = "Ihr Ergebnis deutet auf eine **leichte bis moderate implizite Assoziation** zwischen 'KI als Partner' und 'Chance' hin."
        else:
            result_text = "Ihr Ergebnis deutet auf eine **schwache oder keine klare implizite Assoziation** hin."
        
        st.info(result_text)
        st.warning("Hinweis: Dies ist eine vereinfachte Demonstration und hat keine wissenschaftliche Validität aufgrund der technischen Limitierungen von Web-Frameworks wie Streamlit.")

        with st.expander("Rohdaten anzeigen"):
            st.dataframe(df)
            
    except (KeyError, ZeroDivisionError):
        st.error("Es konnten keine ausreichenden Daten gesammelt werden, um ein Ergebnis zu berechnen. Bitte versuchen Sie es erneut.")


# --- 4. Streamlit App Layout und Logik ---

# Initialisierung, falls der Test noch nicht gestartet wurde
if 'test_phase' not in st.session_state:
    initialize_state()

# --- Ansicht 1: Startbildschirm ---
if st.session_state.test_phase == 'start':
    st.title("Impliziter Assoziationstest (IAT) zur KI-Wahrnehmung")
    st.markdown("""
    Willkommen zu dieser Demonstration eines IAT.
    
    Ihnen werden in der Mitte des Bildschirms Begriffe angezeigt. Ihre Aufgabe ist es, diese Begriffe so schnell wie möglich einer der beiden Kategorien links oder rechts zuzuordnen.
    
    - Drücken Sie den **Button 'E'** für die linke Kategorie.
    - Drücken Sie den **Button 'I'** für die rechte Kategorie.
    
    **Wichtig:** Versuchen Sie, so schnell und fehlerfrei wie möglich zu sein. Bei einem Fehler erscheint ein rotes X und Sie müssen die korrekte Zuordnung treffen, um fortzufahren.
    """)
    if st.button("Test starten"):
        st.session_state.test_phase = 'testing'
        prepare_block(0) # Ersten Block vorbereiten
        st.rerun()

# --- Ansicht 2: Der eigentliche Test ---
elif st.session_state.test_phase == 'testing':
    block_config = IAT_BLOCKS[st.session_state.current_block]
    current_stimulus = st.session_state.stimuli_list[st.session_state.current_trial]
    
    # Kategorien anzeigen
    left_cat_text = "<br>/<br>".join([CATEGORIES[cat] for cat in block_config['left']])
    right_cat_text = "<br>/<br>".join([CATEGORIES[cat] for cat in block_config['right']])
    
    st.markdown(f"**Block {st.session_state.current_block + 1} von {len(IAT_BLOCKS)}**")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st.markdown(f'<p style="color:green; font-size: 20px; text-align: left;">{left_cat_text}</p>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<p style="color:blue; font-size: 20px; text-align: right;">{right_cat_text}</p>', unsafe_allow_html=True)
        
    # Stimulus anzeigen
    st.markdown(f'<div style="text-align: center; font-size: 32px; font-weight: bold; padding: 50px;">{current_stimulus["text"]}</div>', unsafe_allow_html=True)
    
    # Feedback für falsche Antwort
    if st.session_state.show_feedback:
        st.markdown('<p style="color:red; font-size: 40px; text-align: center;">X</p>', unsafe_allow_html=True)

    # Zeitmessung starten, kurz bevor die Buttons gerendert werden
    if st.session_state.start_time == 0 and not st.session_state.show_feedback:
        st.session_state.start_time = time.time()

    # Buttons für die Eingabe
    # WICHTIG: Die on_click-Funktion wird vor dem Neuladen der Seite ausgeführt.
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.button("E", on_click=record_response, args=('e',), use_container_width=True)
    with col_btn2:
        st.button("I", on_click=record_response, args=('i',), use_container_width=True)


# --- Ansicht 3: Endbildschirm ---
elif st.session_state.test_phase == 'end':
    calculate_and_show_results()
    if st.button("Test neu starten"):
        initialize_state()
        st.rerun()
