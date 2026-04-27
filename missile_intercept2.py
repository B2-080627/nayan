import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.title("3D Intercept Simulation (Live)")

# Controls
steps = st.slider("Simulation Steps", 50, 500, 200)
missile_speed = st.slider("Missile Speed", 1.0, 10.0, 5.0)
interceptor_speed = st.slider("Interceptor Speed", 1.0, 15.0, 7.0)

start = st.button("Start Simulation")

# Placeholder for animation
plot_placeholder = st.empty()

if start:
    dt = 0.1

    missile_pos = np.array([0.0, 0.0, 0.0])
    target_pos = np.array([100.0, 100.0, 50.0])
    interceptor_pos = np.array([0.0, 100.0, 0.0])

    missile_traj = []
    interceptor_traj = []

    for step in range(steps):
        # Missile moves toward target
        direction_to_target = target_pos - missile_pos
        direction_to_target /= np.linalg.norm(direction_to_target)
        missile_pos += direction_to_target * missile_speed * dt

        # Interceptor homes toward missile
        direction_to_missile = missile_pos - interceptor_pos
        if np.linalg.norm(direction_to_missile) > 0:
            direction_to_missile /= np.linalg.norm(direction_to_missile)
        interceptor_pos += direction_to_missile * interceptor_speed * dt

        missile_traj.append(missile_pos.copy())
        interceptor_traj.append(interceptor_pos.copy())

        # Create figure
        fig = go.Figure()

        # Missile path
        mt = np.array(missile_traj)
        fig.add_trace(go.Scatter3d(
            x=mt[:,0], y=mt[:,1], z=mt[:,2],
            mode='lines+markers',
            name='Missile'
        ))

        # Interceptor path
        it = np.array(interceptor_traj)
        fig.add_trace(go.Scatter3d(
            x=it[:,0], y=it[:,1], z=it[:,2],
            mode='lines+markers',
            name='Interceptor'
        ))

        # Target
        fig.add_trace(go.Scatter3d(
            x=[target_pos[0]],
            y=[target_pos[1]],
            z=[target_pos[2]],
            mode='markers',
            name='Target'
        ))

        fig.update_layout(
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z'
            ),
            margin=dict(l=0, r=0, b=0, t=40)
        )

        # Update plot
        plot_placeholder.plotly_chart(fig, use_container_width=True)

        # Check intercept
        if np.linalg.norm(missile_pos - interceptor_pos) < 2:
            st.success(f"Intercept achieved at step {step}!")
            break

        time.sleep(0.05)  # Controls animation speed