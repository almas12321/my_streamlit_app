
import streamlit as st

st.set_page_config(page_title="Registration Form", page_icon="📝", layout="centered")

# ---------- Styling (background, card, button) ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Background */
    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(45, 212, 191, 0.35), transparent 40%),
            radial-gradient(circle at 85% 90%, rgba(99, 102, 241, 0.40), transparent 45%),
            linear-gradient(135deg, #0b1f3a 0%, #12355b 55%, #0f766e 100%);
        background-attachment: fixed;
    }

    /* Hide default header/footer */
    header[data-testid="stHeader"] { background: transparent; }
    footer { visibility: hidden; }

    /* Page heading */
    .page-title {
        color: #ffffff;
        font-size: 2.4rem;
        font-weight: 800;
        text-align: center;
        margin: 0.5rem 0 0.2rem 0;
        letter-spacing: -0.5px;
    }
    .page-sub {
        color: #bfe9e4;
        text-align: center;
        margin-bottom: 1.6rem;
        font-size: 1rem;
    }

    /* Form card */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.95);
        border: none;
        border-radius: 20px;
        padding: 2rem 1.8rem;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
    }
    div[data-testid="stForm"] label p {
        color: #12355b;
        font-weight: 700;
    }

    /* Submit button */
    div[data-testid="stFormSubmitButton"] > button {
        width: 100%;
        background: linear-gradient(90deg, #0f766e, #2563eb);
        color: #ffffff;
        font-weight: 700;
        font-size: 1.05rem;
        border: none;
        border-radius: 12px;
        padding: 0.7rem 1rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(15, 118, 110, 0.45);
        color: #ffffff;
    }
    div[data-testid="stFormSubmitButton"] > button:focus-visible {
        outline: 3px solid #99f6e4;
        outline-offset: 2px;
    }

    /* Result card */
    .result-card {
        background: rgba(255, 255, 255, 0.96);
        border-left: 6px solid #0f766e;
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        margin-top: 1.4rem;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
        color: #12355b;
    }
    .result-card h3 { margin: 0 0 0.8rem 0; color: #0f766e; }
    .result-card p { margin: 0.25rem 0; font-size: 1.02rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Heading ----------
st.markdown('<div class="page-title">Student Registration</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-sub">Fill in your details and press Submit</div>',
    unsafe_allow_html=True,
)

# ---------- Form ----------
with st.form("registration_form"):
    name = st.text_input("Full name *", placeholder="e.g. Almas Khan")

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age *", min_value=1, max_value=100, value=None, step=1)
    with col2:
        gender = st.selectbox(
            "Gender *",
            ["Male", "Female", "Other"],
            index=None,
            placeholder="Select gender",
        )

    salary = st.number_input("Monthly salary *", min_value=0, value=None, step=1000)

    submitted = st.form_submit_button("Submit")

# ---------- After submit ----------
if submitted:
    if not name.strip():
        st.error("Please enter your name.")
    elif age is None:
        st.error("Please enter your age.")

    elif gender is None:
        st.error("Please select your gender.")
    elif salary is None:
        st.error("Please enter your salary.")
    else:
        st.balloons()
        st.markdown(
            f"""
            <div class="result-card">
                <h3>Registration complete</h3>
                <p><b>Name:</b> {name.strip()}</p>
                <p><b>Age:</b> {int(age)}</p>
                <p><b>Gender:</b> {gender}</p>
                <p><b>Salary:</b> {int(salary):,}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )