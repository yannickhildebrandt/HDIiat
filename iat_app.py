import streamlit as st
import random
import time
import pandas as pd

# --- Globale Konfiguration für das UI-Design ---
HDI_GREEN = "#007a52"
HDI_DARK_GRAY = "#333333"
HDI_LIGHT_GRAY = "#f5f5f5"

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

# --- 2. Definition der 7 Testblöcke ---
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
    """Initialisiert oder resettet den Testzustand im Streamlit Session State."""
    if 'test_phase' not in st.session_state:
        st.session_state.test_phase = 'start'
        st.session_state.current_block = 0
        st.session_state.current_trial = 0
        st.session_state.results = []
        st.session_state.stimuli_list = []
        st.session_state.start_time = 0
        st.session_state.show_feedback = False

def prepare_block(block_index):
    """Bereitet einen neuen Block vor, indem die Stimuli-Liste gemischt wird."""
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
    """Verarbeitet die Antwort des Nutzers, misst die Zeit und prüft die Korrektheit."""
    if st.session_state.start_time == 0:
        return  # Verhindert doppelte Aufzeichnung

    reaction_time = (time.time() - st.session_state.start_time) * 1000
    block_config = IAT_BLOCKS[st.session_state.current_block]
    current_stimulus = st.session_state.stimuli_list[st.session_state.current_trial]

    # Bestimmt, ob die Antwort korrekt war
    is_correct = (key_pressed == 'e' and current_stimulus['category'] in block_config['left']) or \
                 (key_pressed == 'i' and current_stimulus['category'] in block_config['right'])

    # Speichert das Ergebnis nur, wenn kein Feedback angezeigt wird (verhindert doppelte Speicherung bei Fehler)
    if not st.session_state.show_feedback:
        st.session_state.results.append({
            'block': st.session_state.current_block + 1,
            'is_critical': block_config.get('is_critical', False),
            'stimulus': current_stimulus['text'],
            'correct': is_correct,
            'rt': reaction_time
        })

    st.session_state.start_time = 0  # Zeit zurücksetzen

    if is_correct:
        st.session_state.show_feedback = False
        st.session_state.current_trial += 1
        # Prüfen, ob der Block beendet ist
        if st.session_state.current_trial >= len(st.session_state.stimuli_list):
            st.session_state.current_block += 1
            # Prüfen, ob der gesamte Test beendet ist
            if st.session_state.current_block >= len(IAT_BLOCKS):
                st.session_state.test_phase = 'end'
            else:
                st.session_state.test_phase = 'break'
    else:
        # Bei Fehler Feedback anzeigen
        st.session_state.show_feedback = True

# --- 4. UI-Komponenten und Styling ---

def load_css():
    """Lädt benutzerdefiniertes CSS für das HDI-Branding."""
    st.markdown(f"""
    <style>
        /* Globale Stile */
        body {{
            background-color: {HDI_LIGHT_GRAY};
        }}
        .stApp {{
            background-color: {HDI_LIGHT_GRAY};
        }}
        /* Hauptcontainer für Start- und Ergebnisseite */
        .main-container {{
            background-color: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            color: {HDI_DARK_GRAY};
        }}
        /* Buttons */
        .stButton>button {{
            background-color: {HDI_GREEN};
            color: white;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 1.1rem;
            font-weight: bold;
            border: none;
            transition: background-color 0.3s ease;
        }}
        .stButton>button:hover {{
            background-color: #005a41; /* Dunkleres Grün für Hover */
            color: white;
        }}
        .stButton>button:focus {{
            box-shadow: 0 0 0 2px {HDI_DARK_GRAY};
        }}
        /* IAT-Test Buttons */
        .iat-button button {{
            height: 150px;
            white-space: pre-wrap; /* Erlaubt Zeilenumbrüche */
            font-size: 1.2rem;
            background-color: white;
            color: {HDI_DARK_GRAY};
            border: 2px solid {HDI_DARK_GRAY};
        }}
        .iat-button button:hover {{
            background-color: #f0f0f0;
        }}
        /* Stimulus Text in der Mitte */
        .stimulus-text {{
            text-align: center;
            font-size: 2.5rem;
            font-weight: bold;
            padding: 50px 0;
            color: {HDI_GREEN};
        }}
        /* Feedback-Kreuz */
        .feedback-x {{
            color: red;
            font-size: 4rem;
            text-align: center;
            font-weight: bold;
        }}
        /* Metriken auf der Ergebnisseite */
        .stMetric {{
            background-color: #f9f9f9;
            border-left: 5px solid {HDI_GREEN};
            padding: 1rem;
            border-radius: 8px;
        }}
    </style>
    """, unsafe_allow_html=True)

def show_start_page():
    """Zeigt die Startseite mit Erklärungen und Anleitung."""
    st.title("Impliziter Assoziationstest (IAT)")
    st.subheader("Ihre unbewusste Einstellung zu PowerPoint")

    with st.container(border=True):
        st.markdown("""
        #### Was ist ein Impliziter Assoziationstest?
        Der IAT ist ein psychologisches Testverfahren, das entwickelt wurde, um die Stärke unbewusster Assoziationen zwischen Konzepten im Gedächtnis zu messen. 
        Die Grundidee ist einfach: Wenn zwei Konzepte in unserem Gehirn eng miteinander verknüpft sind (z.B. "Blume" und "positiv"), können wir sie schneller und mit weniger Fehlern zusammen sortieren als zwei Konzepte, die nicht oder nur schwach verknüpft sind.
        
        #### Worum geht es in diesem Test?
        Dieser spezifische IAT untersucht die implizite (also unbewusste) Assoziation zwischen den Konzepten **"PowerPoint-Anwendung"** und **"Nützlich"**. 
        Finden Sie PowerPoint-Tätigkeiten eher nützlich oder eher nutzlos? Ihre Reaktionsgeschwindigkeit verrät es!
        
        #### Anleitung
        1.  **Zwei Kategorien:** Oben links und rechts sehen Sie Kategorien (z.B. "Nützlich").
        2.  **Ein Begriff in der Mitte:** In der Mitte des Bildschirms erscheint ein Wort (z.B. "Präsentation").
        3.  **Schnell zuordnen:** Ihre Aufgabe ist es, das Wort in der Mitte so schnell und fehlerfrei wie möglich der passenden Kategorie zuzuordnen, indem Sie auf den **Button** auf der entsprechenden Seite klicken.
        4.  **Fehler:** Bei einer falschen Zuordnung erscheint ein rotes **X**. Korrigieren Sie Ihren Fehler, um fortzufahren.
        
        **Wichtig:** Versuchen Sie, so schnell wie möglich zu reagieren, aber machen Sie sich keine Sorgen über gelegentliche Fehler.
        """)

    if st.button("Test starten", use_container_width=True):
        st.session_state.test_phase = 'break'
        prepare_block(0)
        st.rerun()

def show_testing_interface():
    """Zeigt die Haupt-Testoberfläche mit Stimulus und Antwort-Buttons."""
    block_config = IAT_BLOCKS[st.session_state.current_block]
    current_stimulus = st.session_state.stimuli_list[st.session_state.current_trial]

    left_label = "\noder\n".join([CATEGORIES[cat] for cat in block_config['left']])
    right_label = "\noder\n".join([CATEGORIES[cat] for cat in block_config['right']])

    st.markdown(f'<div class="stimulus-text">{current_stimulus["text"]}</div>', unsafe_allow_html=True)

    if st.session_state.show_feedback:
        st.markdown('<p class="feedback-x">X</p>', unsafe_allow_html=True)
    else:
        # Platzhalter, damit das Layout nicht springt, wenn das X erscheint
        st.markdown('<p style="color:white; font-size: 4rem; text-align: center;">X</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.button(left_label, on_click=record_response, args=('e',), use_container_width=True, key=f'btn_e_{st.session_state.current_trial}', type="secondary")
    with col2:
        st.button(right_label, on_click=record_response, args=('i',), use_container_width=True, key=f'btn_i_{st.session_state.current_trial}', type="secondary")

    # Startet die Zeitmessung, wenn sie noch nicht läuft
    if st.session_state.start_time == 0:
        st.session_state.start_time = time.time()
        # Ein kleiner Trick, um die UI neu zu rendern, falls nötig
        time.sleep(0.01)


def calculate_and_show_results():
    """Berechnet die Ergebnisse und zeigt die Interpretationsseite an."""
    st.title("Ihr IAT-Ergebnis")

    with st.container(border=True):
        df = pd.DataFrame(st.session_state.results)
        
        # Nur korrekte Versuche aus den kritischen Blöcken verwenden
        critical_trials = df[df['is_critical'] & df['correct']]
        
        try:
            # Block 4: PowerPoint-Anwendung + Nützlich
            avg_rt_block4 = critical_trials[critical_trials['block'] == 4]['rt'].mean()
            # Block 7: PowerPoint-Anwendung + Nutzlos
            avg_rt_block7 = critical_trials[critical_trials['block'] == 7]['rt'].mean()

            if pd.isna(avg_rt_block4) or pd.isna(avg_rt_block7):
                raise ValueError("Nicht genügend Daten in einem der kritischen Blöcke.")
            
            # Der IAT-Effekt ist die Differenz der Reaktionszeiten
            iat_effect = avg_rt_block7 - avg_rt_block4

            st.subheader("Ihre Reaktionszeiten im Überblick")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Ø Zeit (PP + Nützlich)", value=f"{avg_rt_block4:.0f} ms")
            with col2:
                st.metric(label="Ø Zeit (PP + Nutzlos)", value=f"{avg_rt_block7:.0f} ms")
            with col3:
                st.metric(label="IAT-Effekt (Differenz)", value=f"{iat_effect:.0f} ms")
            
            st.divider()

            st.subheader("Was bedeutet dieses Ergebnis?")
            
            if iat_effect > 150:
                st.info("**Starker positiver Effekt:** Ihre Ergebnisse deuten auf eine starke implizite Assoziation zwischen 'PowerPoint-Anwendung' und 'Nützlich' hin. Sie haben die Begriffe deutlich schneller zugeordnet, als diese beiden Kategorien auf derselben Taste lagen.")
            elif iat_effect > 50:
                st.info("**Moderater positiver Effekt:** Ihre Ergebnisse deuten auf eine moderate implizite Assoziation zwischen 'PowerPoint-Anwendung' und 'Nützlich' hin. Sie waren schneller, als diese beiden Kategorien gepaart waren.")
            elif iat_effect < -150:
                st.warning("**Starker negativer Effekt:** Ihre Ergebnisse deuten auf eine starke implizite Assoziation zwischen 'PowerPoint-Anwendung' und 'Nutzlos' hin. Sie waren deutlich schneller, als 'PowerPoint-Anwendung' mit 'Nutzlos' gepaart war.")
            elif iat_effect < -50:
                 st.warning("**Moderater negativer Effekt:** Ihre Ergebnisse deuten auf eine moderate implizite Assoziation zwischen 'PowerPoint-Anwendung' und 'Nutzlos' hin.")
            else:
                st.success("**Geringer oder kein Effekt:** Ihre Reaktionszeiten zeigen keine klare Präferenz. Ihre implizite Assoziation zwischen PowerPoint-Anwendungen und Nützlichkeit bzw. Nutzlosigkeit scheint ausgeglichen zu sein.")

            st.markdown("""
            **Wie kommt das Ergebnis zustande?**
            - **Block 4** hat die Kategorien 'PowerPoint-Anwendung' und 'Nützlich' kombiniert. Wenn Sie diese Assoziation innerlich teilen, fällt Ihnen die Zuordnung hier leicht und Sie sind schnell.
            - **Block 7** hat 'PowerPoint-Anwendung' und 'Nutzlos' kombiniert. Wenn diese Kombination für Sie "unlogisch" ist, benötigen Sie unbewusst mehr Zeit, um die Begriffe zuzuordnen.
            - Die **Differenz** dieser Zeiten (der IAT-Effekt) ist ein Maß für die Stärke Ihrer automatischen Assoziation.

            **Wichtiger Hinweis:** Ein IAT misst unbewusste Assoziationen, nicht unbedingt Ihre bewussten Überzeugungen. Das Ergebnis kann durch viele Faktoren beeinflusst werden (z.B. kulturelle Prägung, persönliche Erfahrungen) und stellt keine endgültige "Wahrheit" über Ihre Einstellung dar. Es ist eine Momentaufnahme Ihrer mentalen Verknüpfungen.
            """)
            
            with st.expander("Rohdaten der Messung anzeigen"):
                st.dataframe(df)

        except (KeyError, ZeroDivisionError, ValueError) as e:
            st.error(f"Es konnten keine ausreichenden Daten gesammelt werden, um ein Ergebnis zu berechnen. Bitte versuchen Sie es erneut. Fehler: {e}")
            st.dataframe(df) # Zeigt die gesammelten Daten zur Fehlersuche an
    
    if st.button("Test neu starten", use_container_width=True):
        # Alle Session-State-Variablen löschen, um einen sauberen Neustart zu gewährleisten
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- 5. Hauptlogik der Streamlit App ---

st.set_page_config(layout="centered", page_title="IAT PowerPoint")
load_css()
initialize_state()

# Haupt-Router basierend auf der Testphase
if st.session_state.test_phase == 'start':
    show_start_page()

elif st.session_state.test_phase == 'break':
    block_config = IAT_BLOCKS[st.session_state.current_block]
    st.header(f"Block {st.session_state.current_block + 1} / {len(IAT_BLOCKS)}")
    st.subheader(f"Thema: {block_config['name']}")
    st.progress((st.session_state.current_block) / len(IAT_BLOCKS))
    
    # Automatisch zum Test übergehen
    time.sleep(3) # Pause von 3 Sekunden
    st.session_state.test_phase = 'testing'
    prepare_block(st.session_state.current_block)
    st.rerun()

elif st.session_state.test_phase == 'testing':
    # Die UI-Logik ist in einer eigenen Funktion für die Übersichtlichkeit
    show_testing_interface()

elif st.session_state.test_phase == 'end':
    calculate_and_show_results()
