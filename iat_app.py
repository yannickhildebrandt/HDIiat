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

# --- 4. UI-Komponenten und Styling ---
def load_css():
    st.markdown(f"""
    <style>
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        @keyframes slideInUp {{ from {{ transform: translateY(20px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}
        @keyframes shake {{ 0%, 100% {{ transform: translateX(0); }} 10%, 30%, 50%, 70%, 90% {{ transform: translateX(-5px); }} 20%, 40%, 60%, 80% {{ transform: translateX(5px); }} }}
        .fade-in {{ animation: fadeIn 0.5s ease-in-out; }}
        .slide-in-up {{ animation: slideInUp 0.5s ease-out; }}
        .stApp {{ background-color: {HDI_LIGHT_GRAY}; }}
        .stApp, .stMarkdown, h1, h2, h3, h4, h5, h6 {{ color: {HDI_DARK_GRAY}; }}
        h1, h2, h3 {{ animation: fadeIn 0.5s ease-in, slideInUp 0.5s ease-out; }}
        .card {{ background-color: white; padding: 2rem; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.05); margin-top: 1.5rem; animation: fadeIn 0.5s ease-in-out; }}
        .card p {{ margin-bottom: 0; }}
        .stButton>button {{ background-image: linear-gradient(to right, {HDI_GREEN} 0%, #009a6e 51%, {HDI_GREEN} 100%); color: white; border-radius: 10px; padding: 15px 30px; font-size: 1.2rem; font-weight: bold; border: none; transition: 0.5s; background-size: 200% auto; box-shadow: 0 4px 10px rgba(0, 122, 82, 0.3); }}
        .stButton>button:hover {{ background-position: right center; color: white; transform: translateY(-2px); box-shadow: 0 8px 15px rgba(0, 122, 82, 0.4); }}
        .stButton>button[kind="secondary"] {{ height: 180px; white-space: pre-wrap; font-size: 1.3rem; background: white; color: {HDI_DARK_GRAY}; border: 2px solid #ddd; box-shadow: none; }}
        .stButton>button[kind="secondary"]:hover {{ border-color: {HDI_GREEN}; background-color: #f9f9f9; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
        .stimulus-container.incorrect .stimulus-text {{ color: {HDI_RED}; animation: shake 0.5s ease-in-out; }}
        .stimulus-text {{ text-align: center; font-size: 3rem; font-weight: bold; padding: 60px 0; color: {HDI_GREEN}; animation: fadeIn 0.3s ease; }}
        .feedback-x {{ color: {HDI_RED}; font-size: 2.5rem; text-align: center; font-weight: bold; height: 40px; }}
        .iat-result-bar-container {{ width: 100%; background-color: #e9ecef; border-radius: 10px; height: 30px; position: relative; margin-top: 1rem; }}
        .iat-result-bar {{ height: 100%; border-radius: 10px; position: absolute; transition: width 1s ease-out, left 1s ease-out; }}
        .iat-result-bar.positive {{ background-color: {HDI_GREEN}; left: 50%; }}
        .iat-result-bar.negative {{ background-color: {HDI_RED}; right: 50%; }}
        .iat-result-center-line {{ position: absolute; left: 50%; top: 0; bottom: 0; border-left: 2px dashed #adb5bd; }}
        .metrics-container {{ display: flex; justify-content: space-between; text-align: center; margin: 1.5rem 0; }}
        .metric-col {{ flex: 1; padding: 0 10px; }}
        .metric-label {{ font-size: 0.9rem; color: #555; }}
        .metric-value {{ font-size: 1.8rem; font-weight: bold; color: {HDI_DARK_GRAY}; }}
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
    st.markdown("<h2 style='text-align:center; color: #555;'>Ihre unbewusste Einstellung zu PowerPoint</h2>", unsafe_allow_html=True)
    st.info("**Willkommen!** Dieser interaktive Test ist Teil des HDI-Workshops zum Thema **'Digitales Mindset'**.", icon="💡")
    st.markdown("""<div class="card">
        <h4>🧠 Was ist ein Impliziter Assoziationstest?</h4>
        <p>Der IAT misst die Stärke unbewusster Assoziationen. Die Logik: Wir reagieren schneller, wenn zwei Konzepte, die in unserem Gehirn stark verknüpft sind, auf derselben Antworttaste liegen. Dieser Test misst Ihre Reaktionszeit in Millisekunden, um diese verborgenen Verknüpfungen aufzudecken.</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("""<div class="card">
        <h4>🎯 Ihre Aufgabe</h4>
        <ol style="padding-left: 20px; margin-bottom: 1rem;">
            <li><b>Kategorien beachten:</b> Links und rechts werden Kategorien angezeigt.</li>
            <li><b>Begriff in der Mitte:</b> Ein Wort erscheint in der Mitte.</li>
            <li><b>Schnell zuordnen:</b> Klicken Sie so schnell und genau wie möglich auf den Button der passenden Seite. Bei Fehlern erscheint ein rotes <b>X</b> – korrigieren Sie sich, um weiterzumachen.</li>
        </ol>
        <p><b>Ziel ist Geschwindigkeit!</b> Zögern Sie nicht und folgen Sie Ihrem ersten Impuls.</p>
    </div>""", unsafe_allow_html=True)
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
    feedback_class = "incorrect" if st.session_state.show_feedback else ""
    stimulus_key = f"stimulus-{st.session_state.current_block}-{st.session_state.current_trial}"
    st.markdown(f'<div class="stimulus-container {feedback_class}" key="{stimulus_key}"><div class="stimulus-text">{current_stimulus["text"]}</div></div>', unsafe_allow_html=True)
    if st.session_state.show_feedback: st.markdown('<p class="feedback-x">X</p>', unsafe_allow_html=True)
    else: st.markdown('<p class="feedback-x"></p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: st.button(left_label, on_click=record_response, args=('e',), use_container_width=True, key=f'btn_e_{st.session_state.current_trial}', type="secondary")
    with col2: st.button(right_label, on_click=record_response, args=('i',), use_container_width=True, key=f'btn_i_{st.session_state.current_trial}', type="secondary")
    if st.session_state.start_time == 0:
        st.session_state.start_time = time.time()
        time.sleep(0.01)

def get_iat_effect_visualization_html(iat_effect):
    max_effect_for_scale = 500
    normalized_effect = max(min(iat_effect, max_effect_for_scale), -max_effect_for_scale)
    bar_width = abs(normalized_effect / max_effect_for_scale) * 50
    bar_class = "positive" if iat_effect >= 0 else "negative"
    return f"""<div style="font-size: 0.9rem; display: flex; justify-content: space-between; color: #555;">
            <span>Starke Assoziation mit <b>Nutzlos</b></span>
            <span>Starke Assoziation mit <b>Nützlich</b></span>
        </div>
        <div class="iat-result-bar-container">
            <div class="iat-result-center-line"></div>
            <div class="iat-result-bar {bar_class}" style="width: {bar_width}%;"></div>
        </div>"""

def calculate_and_show_results():
    st.title("📊 Ihr IAT-Ergebnis")
    df = pd.DataFrame(st.session_state.results)
    critical_trials = df[df['is_critical'] & df['correct']]
    try:
        avg_rt_block4 = critical_trials[critical_trials['block'] == 4]['rt'].mean()
        avg_rt_block7 = critical_trials[critical_trials['block'] == 7]['rt'].mean()
        if pd.isna(avg_rt_block4) or pd.isna(avg_rt_block7): raise ValueError("Nicht genügend Daten.")
        iat_effect = avg_rt_block7 - avg_rt_block4

        interpretation_html = ""
        if iat_effect > 50:
            interpretation_html = "<div style='background-color: #d4edda; color: #155724; padding: 1rem; border-radius: 8px;'><b>Positive Tendenz:</b> Sie assoziieren 'PowerPoint-Anwendung' implizit eher mit <b>'Nützlich'</b>.</div>"
        elif iat_effect < -50:
            interpretation_html = "<div style='background-color: #fff3cd; color: #856404; padding: 1rem; border-radius: 8px;'><b>Negative Tendenz:</b> Sie assoziieren 'PowerPoint-Anwendung' implizit eher mit <b>'Nutzlos'</b>.</div>"
        else:
            interpretation_html = "<div style='background-color: #d1ecf1; color: #0c5460; padding: 1rem; border-radius: 8px;'><b>Neutrale Tendenz:</b> Ihre impliziten Assoziationen sind weitgehend ausgeglichen.</div>"
        
        viz_html = get_iat_effect_visualization_html(iat_effect)
        st.markdown(f"""<div class="card">
            <h4>Ihre implizite Neigung auf einen Blick</h4>
            {interpretation_html}
            {viz_html}
        </div>""", unsafe_allow_html=True)
        
        st.markdown(f"""<div class="card">
            <h4>⏱️ Detailauswertung</h4>
            <div class="metrics-container">
                <div class="metric-col"><div class="metric-label">Ø Zeit (PP + Nützlich)</div><div class="metric-value">{avg_rt_block4:.0f} ms</div></div>
                <div class="metric-col"><div class="metric-label">Ø Zeit (PP + Nutzlos)</div><div class="metric-value">{avg_rt_block7:.0f} ms</div></div>
                <div class="metric-col"><div class="metric-label">IAT-Effekt (Differenz)</div><div class="metric-value">{iat_effect:.0f} ms</div></div>
            </div>
            <hr>
            <p><b>Wie kommt das Ergebnis zustande?</b><br>
            Ein <b>positiver IAT-Effekt</b> bedeutet, dass Sie im Block "PP + Nutzlos" langsamer waren. Ihr Gehirn brauchte mehr Zeit, um diese "unpassende" Kombination zu verarbeiten. Ein <b>negativer Effekt</b> würde das Gegenteil bedeuten.</p>
            <p style="margin-top: 1rem;"><b>Wichtiger Hinweis:</b> Dies ist eine Momentaufnahme Ihrer automatischen Assoziationen, nicht zwingend Ihre bewusste Meinung.</p>
        </div>""", unsafe_allow_html=True)
        
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
