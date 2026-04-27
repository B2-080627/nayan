import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(layout="wide")
st.title("🚀 3D Intercept Simulation (Interactive)")

# --- Session State ---
if "running" not in st.session_state:
    st.session_state.running = False
if "paused" not in st.session_state:
    st.session_state.paused = False
if "step" not in st.session_state:
    st.session_state.step = 0

# --- Controls ---
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Start"):
        st.session_state.running = True
        st.session_state.paused = False
        st.session_state.step = 0

with col2:
    if st.button("⏸ Pause"):
        st.session_state.paused = True

with col3:
    if st.button("🔄 Reset"):
        st.session_state.running = False
        st.session_state.paused = False
        st.session_state.step = 0

# Sliders
steps = st.slider("Simulation Steps", 50, 500, 200)
missile_speed = st.slider("Missile Speed", 1.0, 10.0, 5.0)
interceptor_speed = st.slider("Interceptor Speed", 1.0, 15.0, 7.0)
animation_speed = st.slider("Animation Speed", 0.01, 0.2, 0.05)

plot_placeholder = st.empty()

# --- Simulation Setup ---
dt = 0.1
missile_pos = np.array([0.0, 0.0, 0.0])
target_pos = np.array([100.0, 100.0, 50.0])
interceptor_pos = np.array([0.0, 100.0, 0.0])

missile_traj = []
interceptor_traj = []

exploded = False
explosion_point = None

# --- Run Simulation ---
if st.session_state.running:

    for step in range(st.session_state.step, steps):

        if st.session_state.paused:
            st.session_state.step = step
            break

        # Missile motion
        direction_to_target = target_pos - missile_pos
        direction_to_target /= np.linalg.norm(direction_to_target)
        missile_pos += direction_to_target * missile_speed * dt

        # Interceptor guidance
        direction_to_missile = missile_pos - interceptor_pos
        if np.linalg.norm(direction_to_missile) > 0:
            direction_to_missile /= np.linalg.norm(direction_to_missile)
        interceptor_pos += direction_to_missile * interceptor_speed * dt

        missile_traj.append(missile_pos.copy())
        interceptor_traj.append(interceptor_pos.copy())

        # Check intercept
        if np.linalg.norm(missile_pos - interceptor_pos) < 2:
            exploded = True
            explosion_point = missile_pos.copy()
            st.success(f"💥 Intercept at step {step}")
            st.session_state.running = False

        # --- Plot ---
        fig = go.Figure()

        mt = np.array(missile_traj)
        it = np.array(interceptor_traj)

        fig.add_trace(go.Scatter3d(
            x=mt[:,0], y=mt[:,1], z=mt[:,2],
            mode='lines+markers',
            name='Missile'
        ))

        fig.add_trace(go.Scatter3d(
            x=it[:,0], y=it[:,1], z=it[:,2],
            mode='lines+markers',
            name='Interceptor'
        ))

        fig.add_trace(go.Scatter3d(
            x=[target_pos[0]],
            y=[target_pos[1]],
            z=[target_pos[2]],
            mode='markers',
            name='Target'
        ))

        # Explosion effect
        if exploded and explosion_point is not None:
            fig.add_trace(go.Scatter3d(
                x=[explosion_point[0]],
                y=[explosion_point[1]],
                z=[explosion_point[2]],
                mode='markers',
                marker=dict(size=10),
                name='Explosion'
            ))

        fig.update_layout(
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z'
            ),
            margin=dict(l=0, r=0, b=0, t=40)
        )

        plot_placeholder.plotly_chart(fig, use_container_width=True)

        time.sleep(animation_speed)