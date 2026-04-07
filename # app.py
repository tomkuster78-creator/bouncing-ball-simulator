# app.py
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Ball Simulator", layout="centered")

st.title("⚽ Bouncing Ball Simulator")
st.markdown("Met dit programma kan je zien hoe een bal op de grond stuitert met een zelf gekozen overdruk.") 
st.markdown("Dit programma is gebaseerd op echte metingen op linoleum en houdt rekening met luchtweerstand.") 
st.markdown("Dit programma is alleen realistisch als de bal op dezelfde plek blijft stuiteren.") 
st.markdown("De aanbevolen overdruk in een voetbal, basketbal en volleybal zijn respectievelijk 0.8, 0.55 en 0.3 bar. Om explosies te voorkomen, zijn de ballen in ons experiment niet harder opgepompt dan 1.74 bar")
st.markdown("De dichtheid van de lucht is op zeeniveau ongeveer 1.2 kg/m^3")
st.markdown("DE CODE WERKT NOG NIET BIJ EEN LUCHTDICHTHEID VAN 0. Hoewel de wiskunde dan een stuk makkelijker is, krijg je een 0/0 probleem als je dezelfde formules gebruikt waarbij er wel rekening wordt gehouden met luchtweerstand. Dit moet nog even worden opgelost door bij een aantal formules een if-statement te maken, dat als de luchtdichtheid 0 is, een andere (makkelijkere) berekening  moet worden uitgevoerd waarbij luchtweerstand geen rol speelt. Ik voer dit door als ik er tijd voor heb.")
st.markdown("Mocht je vragen hebben of de code/wiskunde erachter willen zien, stuur dan een mailtje naar tomkuster78@gmail.com")

# ------------------ UI ------------------
ball_type = st.selectbox(
    "Ball type",
    ["Volleyball 🏐", "Basketball 🏀", "Football ⚽"]
)

rho_air         = st.slider("Air density (kg/m^3)", 0.0, 5.0, 1.2)
g               = st.slider("Gravitational acceleration", 1.0, 40.0, 9.81)
overpressure    = st.slider("Overpressure (bar)", 0.1, 4.0, 0.5)
H               = st.number_input("Drop height (m):", value=1.0)
bounces         = st.slider("Number of bounces", 1, 10, 3)


# ------------------ BALL SETTINGS ------------------
if "Volleyball" in ball_type:
    color = "blue"
    m, circ, B, C, D = 0.25319, 0.647, 0.18270622, -0.0088571, 0.9544286

elif "Basketball" in ball_type:
    color = "orange"
    m, circ = 0.51222, 0.726
    B = 0.197165
    C = 0.0186 * np.log(overpressure) - 0.0164
    D = -0.1445 * overpressure + 1.2477

else:
    color = "green"
    m, circ, B, C, D = 0.42953, 0.677, 0.08746166, -0.0115714, 0.8928571

# ------------------ PHYSICS ------------------

cw_bal = 0.47
r_ball = circ / (2 * np.pi)
A_ball = np.pi * r_ball**2

k = 0.5 * cw_bal * A_ball * rho_air
F_z = m * g
E = np.sqrt(k * g / m)

def efficiency(v):
    return (C * v + D) * overpressure / (overpressure + B)

def h_end(eta, h_start):
    return m/(2*k) * np.log(eta * (1-np.exp(-2*k*h_start/m))+1)

def v_touchdown(h_start):
    return np.sqrt(F_z/k) * np.sqrt(1 - np.exp(-2*k*h_start/m))

def v_down(t):
    return np.sqrt(F_z/k) * np.tanh(np.sqrt(k * g/m) * t)

def v_up(t, F):
    return np.sqrt(F_z/k) * np.tan(-np.sqrt(k * g/m) * t + F)

def h_down(t):
    return m/k * np.log(np.cosh(np.sqrt(k * g/m) * t))

def h_up(t, t_T):
    return m/k * np.log(np.cos(E*(t_T-t))/np.cos(E*t_T))

# ------------------ RUN ------------------
if st.button("🚀 Run simulation"):

    timestep = 0.01
    velocities = np.array([])
    heights = np.array([])
    highest_points = np.array([H])
    ii = 0.0

    for _ in range(int(bounces)):

        velocity_touchdown = v_touchdown(H)

        t_G = np.sqrt(m/(k*g)) * np.arccosh(np.exp(k*H/m))
        while ii <= t_G:
            velocities = np.append(velocities, v_down(ii))
            heights = np.append(heights, H - h_down(ii))
            ii += timestep
        ii -= t_G

        eff = efficiency(velocity_touchdown)
        H = h_end(eff, H)
        highest_points = np.append(highest_points, H)

        F = np.arccos(np.exp(-k*H/m))
        t_T = np.sqrt(m/(k*g)) * F

        while ii <= t_T:
            velocities = np.append(velocities, v_up(ii, F))
            heights = np.append(heights, h_up(ii, t_T))
            ii += timestep
        ii -= t_T

    timepoints = np.arange(len(heights)) * timestep

    # ------------------ RESULTS ------------------
    st.subheader("📊 Results")

    max_height = np.max(highest_points)
    total_time = timepoints[-1]

    col1, col2 = st.columns(2)
    col1.metric("Max height", f"{max_height:.2f} m")
    col2.metric("Total time", f"{total_time:.2f} s")

    st.write("Highest points (m):", np.round(highest_points, 3))

    # ------------------ GRAPH ------------------
    fig, ax = plt.subplots()
    ax.plot(timepoints, heights, '.', color=color)
    ax.set_title("Ball trajectory")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Height (m)")
    st.pyplot(fig)

    fig, ax = plt.subplots()
    ax.plot(timepoints, velocities, '.', color=color)
    ax.set_title("Ball velocity")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Velocity (m/s)")
    st.pyplot(fig)
    # ------------------ SMOOTH ANIMATION ------------------

