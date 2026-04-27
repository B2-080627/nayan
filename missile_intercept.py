import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.title("3D Intercept Simulation")

# Simulation parameters
dt = 0.1
steps = st.slider("Simulation Steps", 50, 500, 200)

# Initial positions
missile_pos = np.array([0.0, 0.0, 0.0])
target_pos = np.array([100.0, 100.0, 50.0])
interceptor_pos = np.array([0.0, 100.0, 0.0])

# Speeds
missile_speed = st.slider("Missile Speed", 1.0, 10.0, 5.0)
interceptor_speed = st.slider("Interceptor Speed", 1.0, 15.0, 7.0)

missile_traj = []
interceptor_traj = []

for _ in range(steps):
    # Missile direction toward target
    direction_to_target = target_pos - missile_pos
    direction_to_target /= np.linalg.norm(direction_to_target)
    missile_pos = missile_pos + direction_to_target * missile_speed * dt

    # Interceptor guidance toward missile
    direction_to_missile = missile_pos - interceptor_pos
    if np.linalg.norm(direction_to_missile) > 0:
        direction_to_missile /= np.linalg.norm(direction_to_missile)
    interceptor_pos = interceptor_pos + direction_to_missile * interceptor_speed * dt

    missile_traj.append(missile_pos.copy())
    interceptor_traj.append(interceptor_pos.copy())

    # Stop if intercepted
    if np.linalg.norm(missile_pos - interceptor_pos) < 2:
        st.success("Intercept achieved!")
        break

missile_traj = np.array(missile_traj)
interceptor_traj = np.array(interceptor_traj)

# Plotly 3D plot
fig = go.Figure()

fig.add_trace(go.Scatter3d(
    x=missile_traj[:,0],
    y=missile_traj[:,1],
    z=missile_traj[:,2],
    mode='lines',
    name='Missile',
    line=dict(width=4)
))

fig.add_trace(go.Scatter3d(
    x=interceptor_traj[:,0],
    y=interceptor_traj[:,1],
    z=interceptor_traj[:,2],
    mode='lines',
    name='Interceptor',
    line=dict(width=4)
))

fig.add_trace(go.Scatter3d(
    x=[target_pos[0]],
    y=[target_pos[1]],
    z=[target_pos[2]],
    mode='markers',
    name='Target',
    marker=dict(size=5)
))

fig.update_layout(
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z'
    ),
    margin=dict(l=0, r=0, b=0, t=40)
)

st.plotly_chart(fig, use_container_width=True)