import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
import json
import os
from PIL import Image
from io import BytesIO
import base64
import urllib.parse

# === Konfiguracja strony ===
st.set_page_config(page_title="💪 Tracker Siłowni", page_icon="💪", layout="wide")

# === Stałe / mapowania ===
DATA_FILE = "gym_progress.json"

EXERCISE_IMAGES = {
    "Wyciskanie na ławeczce poziomej": "lawka.png",
    "Brzuszki na maszynie": "brzuszki.png",
    "Wypychanie nóg (Leg Press)": "legpress.png",
    "Biceps - uginanie ramion": "biceps.png",
    "Wyciskanie nad głową": "barki.png",
    "Triceps - prostowanie": "triceps.png",
    "Wiosłowanie": "wioslowanie.png",
    "Podciąganie": "podciaganie.png"
}

EXERCISES = {
    "Wyciskanie na ławeczce poziomej": {"color": "#FF6B6B", "description": "Klatka piersiowa"},
    "Brzuszki na maszynie": {"color": "#4ECDC4", "description": "Mięśnie brzucha"},
    "Wypychanie nóg (Leg Press)": {"color": "#45B7D1", "description": "Mięśnie nóg"},
    "Biceps - uginanie ramion": {"color": "#96CEB4", "description": "Biceps"},
    "Wyciskanie nad głową": {"color": "#FFEAA7", "description": "Barki"},
    "Triceps - prostowanie": {"color": "#DDA0DD", "description": "Triceps"},
    "Wiosłowanie": {"color": "#FFB347", "description": "Plecy"},
    "Podciąganie": {"color": "#87CEEB", "description": "Plecy - szerokość"}
}

# === Pomocnicze funkcje ===
def image_to_base64(image: Image.Image) -> str:
    buf = BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def add_exercise_record(exercise_name, weight, date_str):
    data = load_data()
    if exercise_name not in data:
        data[exercise_name] = []
    data[exercise_name].append({"date": date_str, "weight": weight})
    data[exercise_name] = sorted(data[exercise_name], key=lambda x: x['date'])
    return save_data(data)

def get_exercise_data(exercise_name):
    return load_data().get(exercise_name, [])

def create_progress_chart(exercise_name):
    data = get_exercise_data(exercise_name)
    if not data:
        st.info("🎯 Dodaj pierwsze dane, aby zobaczyć wykres postępu!")
        return
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['weight'],
        mode='lines+markers',
        line=dict(color=EXERCISES[exercise_name]["color"], width=4),
        marker=dict(size=8, color=EXERCISES[exercise_name]["color"], line=dict(width=2, color='white'))
    ))
    fig.update_layout(
        title=f'📈 Postęp - {exercise_name}',
        xaxis_title='Data',
        yaxis_title='Ciężar (kg)',
        hovermode='x unified',
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(t=60, l=60, r=30, b=60)
    )
    fig.update_xaxes(showgrid=True, gridcolor='#E8E8E8')
    fig.update_yaxes(showgrid=True, gridcolor='#E8E8E8')
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("🎯 Ostatni ciężar", f"{df['weight'].iloc[-1]} kg")
    with c2:
        st.metric("🏆 Rekord", f"{df['weight'].max()} kg")
    with c3:
        progress = df['weight'].iloc[-1] - df['weight'].iloc[0] if len(df) > 1 else 0
        st.metric("📊 Postęp", f"{progress:+.1f} kg" if len(df) > 1 else "Początek!")

# === Strona ćwiczenia ===
def exercise_page(exercise_name):
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:20px;">
        <h1 style="color:{EXERCISES[exercise_name]['color']}; margin:0;">{exercise_name}</h1>
        <p style="color:#666; margin-top:6px;">{EXERCISES[exercise_name]['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form(f"form_{exercise_name}", clear_on_submit=True):
        col1, col2, col3 = st.columns([2,2,1])
        with col1:
            workout_date = st.date_input("📅 Data treningu:", value=date.today())
        with col2:
            weight = st.number_input("⚖️ Ciężar (kg):", min_value=0.0, max_value=1000.0, value=50.0, step=2.5, format="%.1f")
        with col3:
            st.write("")
            submit = st.form_submit_button("💾 Zapisz", use_container_width=True, type="primary")
        if submit:
            date_str = workout_date.strftime("%Y-%m-%d")
            ok = add_exercise_record(exercise_name, weight, date_str)
            if ok:
                st.success(f"✅ Zapisano: {weight} kg w dniu {workout_date}")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Błąd podczas zapisu")

    st.markdown("---")
    create_progress_chart(exercise_name)
    st.markdown("---")
    if st.button("⬅️ Powrót do ćwiczeń", use_container_width=True):
        st.session_state.selected_exercise = None
        # czyścimy parametry w URL (powrót na główną)
        st.experimental_set_query_params()
        st.rerun()

# === Strona główna z klikalnymi obrazkami (anchor <a> wokół div -> cały kafelek klikalny) ===
def main_page():
    st.title("💪 Tracker Siłowni")
    st.markdown("### Wybierz ćwiczenie:")
    cols = st.columns(2)

    for idx, (exercise_name, exercise_data) in enumerate(EXERCISES.items()):
        with cols[idx % 2]:
            image_file = EXERCISE_IMAGES.get(exercise_name)
            if image_file and os.path.exists(image_file):
                try:
                    image = Image.open(image_file)
                    img_b64 = image_to_base64(image)
                    url = "?exercise=" + urllib.parse.quote_plus(exercise_name)
                    st.markdown(
                        f"""
                        <a href="{url}" style="text-decoration:none; color:inherit;">
                          <div style="
                            border: 3px solid {exercise_data['color']};
                            border-radius: 15px;
                            padding: 20px;
                            margin-bottom: 18px;
                            text-align: center;
                            background: white;
                            box-shadow: 0 6px 14px rgba(0,0,0,0.06);
                          ">
                            <img src="data:image/png;base64,{img_b64}"
                                 style="height:200px; width:auto; display:block; margin:0 auto; border-radius:8px;">
                            <h3 style="color:{exercise_data['color']}; margin:12px 0 6px 0; font-size:18px;">{exercise_name}</h3>
                          </div>
                        </a>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Błąd wczytywania obrazka: {e}")
                    # fallback: zwykły przycisk
                    if st.button(f"📌 Wybierz: {exercise_name}", key=f"btn_{idx}"):
                        st.session_state.selected_exercise = exercise_name
                        st.experimental_set_query_params(exercise=exercise_name)
                        st.rerun()
            else:
                # brak obrazka - pokazujemy przycisk
                if st.button(f"📌 Wybierz: {exercise_name}", key=f"btn_{idx}"):
                    st.session_state.selected_exercise = exercise_name
                    st.experimental_set_query_params(exercise=exercise_name)
                    st.rerun()

            # opis pod kafelkiem
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, {exercise_data['color']}15, {exercise_data['color']}25);
                    border-radius: 10px;
                    padding: 8px;
                    margin-bottom: 24px;
                    text-align: center;
                ">
                    <p style="color:#666; margin:0;">{exercise_data['description']}</p>
                </div>
            """, unsafe_allow_html=True)

# === Inicjalizacja st.session_state i obsługa parametrów URL ===
if 'selected_exercise' not in st.session_state:
    st.session_state.selected_exercise = None

params = st.query_params
if "exercise" in params:
    # st.query_params może zwracać listę lub string, bądźmy defensywni
    raw = params.get("exercise")
    exercise_name_from_url = raw[0] if isinstance(raw, (list, tuple)) else raw
    if exercise_name_from_url in EXERCISES:
        st.session_state.selected_exercise = exercise_name_from_url

# === Główna logika aplikacji ===
if st.session_state.selected_exercise is not None:
    exercise_page(st.session_state.selected_exercise)
else:
    main_page()
