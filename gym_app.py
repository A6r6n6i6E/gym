import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date
import json
import os
from PIL import Image

# Konfiguracja strony
st.set_page_config(
    page_title="💪 Tracker Siłowni",
    page_icon="💪",
    layout="wide"
)

# Ścieżka do pliku z danymi
DATA_FILE = "gym_progress.json"

# Mapowanie nazw ćwiczeń do nazw plików PNG
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

# Lista ćwiczeń z kolorami i opisami
EXERCISES = {
    "Wyciskanie na ławeczce poziomej": {
        "color": "#FF6B6B",
        "description": "Klatka piersiowa"
    },
    "Brzuszki na maszynie": {
        "color": "#4ECDC4",
        "description": "Mięśnie brzucha"
    },
    "Wypychanie nóg (Leg Press)": {
        "color": "#45B7D1",
        "description": "Mięśnie nóg"
    },
    "Biceps - uginanie ramion": {
        "color": "#96CEB4",
        "description": "Biceps"
    },
    "Wyciskanie nad głową": {
        "color": "#FFEAA7",
        "description": "Barki"
    },
    "Triceps - prostowanie": {
        "color": "#DDA0DD",
        "description": "Triceps"
    },
    "Wiosłowanie": {
        "color": "#FFB347",
        "description": "Plecy"
    },
    "Podciąganie": {
        "color": "#87CEEB",
        "description": "Plecy - szerokość"
    }
}

def load_data():
    """Wczytywanie danych z pliku JSON"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    """Zapisywanie danych do pliku JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def add_exercise_record(exercise_name, weight, date_str):
    """Dodawanie rekordu ćwiczenia"""
    data = load_data()

    if exercise_name not in data:
        data[exercise_name] = []

    record = {
        "date": date_str,
        "weight": weight
    }

    data[exercise_name].append(record)

    # Sortowanie po dacie
    data[exercise_name] = sorted(data[exercise_name], key=lambda x: x['date'])

    return save_data(data)

def get_exercise_data(exercise_name):
    """Pobieranie danych dla konkretnego ćwiczenia"""
    data = load_data()
    return data.get(exercise_name, [])

def create_progress_chart(exercise_name):
    """Tworzenie wykresu postępu"""
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
        name='Ciężar (kg)',
        line=dict(color=EXERCISES[exercise_name]["color"], width=4),
        marker=dict(size=10, color=EXERCISES[exercise_name]["color"],
                   line=dict(width=2, color='white'))
    ))

    fig.update_layout(
        title=f'📈 Postęp - {exercise_name}',
        title_font_size=20,
        xaxis_title='Data',
        yaxis_title='Ciężar (kg)',
        hovermode='x unified',
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(t=60, l=60, r=30, b=60)
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E8E8E8')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E8E8E8')

    st.plotly_chart(fig, use_container_width=True)

    # Statystyki
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Ostatni ciężar", f"{df['weight'].iloc[-1]} kg")
    with col2:
        st.metric("🏆 Rekord", f"{df['weight'].max()} kg")
    with col3:
        if len(df) > 1:
            progress = df['weight'].iloc[-1] - df['weight'].iloc[0]
            st.metric("📊 Postęp", f"{progress:+.1f} kg")
        else:
            st.metric("📊 Postęp", "Początek!")

def exercise_page(exercise_name):
    """Strona konkretnego ćwiczenia (bez obrazka)"""
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: {EXERCISES[exercise_name]['color']};">
            {exercise_name}
        </h1>
        <p style="font-size: 18px; color: #666;">{EXERCISES[exercise_name]['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Formularz dodawania
    with st.form(f"workout_form_{exercise_name}", clear_on_submit=True):
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            workout_date = st.date_input(
                "📅 Data treningu:",
                value=date.today()
            )

        with col2:
            weight = st.number_input(
                "⚖️ Ciężar (kg):",
                min_value=0.0,
                max_value=1000.0,
                value=50.0,
                step=2.5,
                format="%.1f"
            )

        with col3:
            st.write("")  # Spacer
            submit_button = st.form_submit_button(
                "💾 Zapisz",
                use_container_width=True,
                type="primary"
            )

        if submit_button:
            date_str = workout_date.strftime("%Y-%m-%d")

            if add_exercise_record(exercise_name, weight, date_str):
                st.success(f"✅ Zapisano: {weight} kg w dniu {workout_date}")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Błąd podczas zapisywania!")

    # Wykres postępu
    st.markdown("---")
    create_progress_chart(exercise_name)

    # Przycisk powrotu
    st.markdown("---")
    if st.button("⬅️ Powrót do ćwiczeń", use_container_width=True):
        st.session_state.selected_exercise = None
        st.rerun()

def main_page():
    """Strona główna z klikalnymi kafelkami"""
    st.title("💪 Tracker Siłowni")
    st.markdown("### Wybierz ćwiczenie:")

    # Wyświetlanie kafelków w siatce 2x4
    cols = st.columns(2)
    for idx, (exercise_name, exercise_data) in enumerate(EXERCISES.items()):
        with cols[idx % 2]:
            # Kafelek jako klikalny element
            image_file = EXERCISE_IMAGES.get(exercise_name)

            if image_file and os.path.exists(image_file):
                # Przycisk z obrazkiem jako tło
                st.markdown(
                    f"""
                    <style>
                        div[data-testid="stButton_{idx}"] > button {{
                            background: url('{image_file}') no-repeat center center;
                            background-size: contain;
                            height: 150px;
                            width: 100%;
                            border: 2px solid {exercise_data['color']};
                            border-radius: 10px;
                        }}
                        div[data-testid="stButton_{idx}"] > button:hover {{
                            opacity: 0.8;
                            border: 2px solid {exercise_data['color']};
                        }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )

            if st.button(
                label=exercise_name,
                key=f"btn_{idx}",
                use_container_width=True
            ):
                st.session_state.selected_exercise = exercise_name
                st.rerun()

            # Opis ćwiczenia
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {exercise_data['color']}15, {exercise_data['color']}25);
                border: 2px solid {exercise_data['color']};
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                text-align: center;
            ">
                <p style="color: #666; margin: 5px 0; font-size: 14px;">
                    {exercise_data['description']}
                </p>
            </div>
            """, unsafe_allow_html=True)

# Inicjalizacja session state
if 'selected_exercise' not in st.session_state:
    st.session_state.selected_exercise = None

# Główna logika aplikacji
if st.session_state.selected_exercise is not None:
    exercise_page(st.session_state.selected_exercise)
else:
    main_page()
