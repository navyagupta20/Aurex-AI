import streamlit as st

from auth import login, signup


def show_auth_screen():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

        :root {
            --bg: #FAF9F7;
            --text: #242020;
            --muted: #77716E;
            --burgundy: #8F2945;
            --burgundy-dark: #702039;
            --border: #DED8D5;
        }

        /* Page background */
        .stApp {
            background: var(--bg);
        }

        /* Hide navigation and header */
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stHeader"] {
            display: none !important;
        }

        /* Main page width */
        [data-testid="stMainBlockContainer"] {
            max-width: 100% !important;
            padding: 0.5rem 1rem 2rem !important;
        }

        /* Centered content - no card or surrounding box */
        .auth-content {
            width: 100%;
            max-width: 390px;
            margin: 9vh auto 0;
            box-sizing: border-box;
        }

        /* Aurex wordmark */
        .auth-brand {
            text-align: center;
            color: var(--burgundy);
            font-family: 'Manrope', sans-serif;
            font-size: 3.2rem;
            font-weight: 800;
            letter-spacing: -0.09em;
            line-height: 1.15;
            margin: 0 0 12px;
        }

        /* Heading and subtitle */
        .auth-heading {
            text-align: center;
            color: var(--text);
            font-family: 'Manrope', sans-serif;
            font-size: 1.55rem;
            font-weight: 700;
            letter-spacing: -0.045em;
            line-height: 1.35;
            margin: 0 0 7px;
        }

        .auth-subtitle {
            text-align: center;
            color: var(--muted);
            font-family: 'DM Sans', sans-serif;
            font-size: 0.9rem;
            line-height: 1.6;
            margin: 0 0 30px;
        }

        /* Consistent spacing */
        [data-testid="stVerticalBlock"] {
            gap: 0.7rem;
        }

        /* Login/signup selector */
        div[data-testid="stRadio"] {
            margin: 0 0 14px;
        }

        div[data-testid="stRadio"] > label {
            display: none !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] {
            display: flex;
            width: 100%;
            gap: 5px;
            padding: 5px;
            background: #F0ECE9;
            border: 1px solid #E8E1DD;
            border-radius: 10px;
            box-sizing: border-box;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] > label {
            flex: 1;
            min-width: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 10px 5px;
            border-radius: 7px;
            color: var(--muted);
            font-family: 'DM Sans', sans-serif;
            font-size: 0.84rem;
            font-weight: 600;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
            background: #FFFFFF;
            color: var(--burgundy);
            box-shadow: 0 1px 4px rgba(30, 20, 20, 0.07);
        }

        /* Input labels */
        .stTextInput label {
            color: #383230 !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.83rem !important;
            font-weight: 600 !important;
        }

        /* Input fields */
        .stTextInput input {
            width: 100%;
            min-height: 45px;
            background: #FFFFFF !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 9px !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.9rem !important;
            box-sizing: border-box;
        }

        .stTextInput input:focus {
            border-color: var(--burgundy) !important;
            box-shadow: 0 0 0 1px var(--burgundy) !important;
        }

        .stTextInput input::placeholder {
            color: #AAA29E !important;
        }

        /* Remove form borders and backgrounds */
        [data-testid="stForm"] {
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
        }

        /* Primary action button */
        div.stFormSubmitButton > button {
            width: 100%;
            min-height: 46px;
            margin-top: 10px;
            background: var(--burgundy) !important;
            color: #FFFFFF !important;
            border: 1px solid var(--burgundy) !important;
            border-radius: 9px !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.9rem !important;
            font-weight: 700 !important;
            transition: background 160ms ease, transform 160ms ease;
        }

        div.stFormSubmitButton > button:hover {
            background: var(--burgundy-dark) !important;
            border-color: var(--burgundy-dark) !important;
            transform: translateY(-1px);
        }

        /* Feedback messages */
        [data-testid="stAlert"] {
            border-radius: 9px;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.85rem;
        }

        /* Remove extra space around widgets */
        [data-testid="stElementContainer"] {
            margin-bottom: 0;
        }

        /* Mobile layout */
        @media (max-width: 520px) {
            [data-testid="stMainBlockContainer"] {
                padding: 0.5rem 1rem 1rem !important;
            }

            .auth-content {
                max-width: 100%;
                margin-top: 6vh;
            }

            .auth-brand {
                font-size: 2.8rem;
            }

            .auth-heading {
                font-size: 1.4rem;
            }

            .auth-subtitle {
                margin-bottom: 25px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Center the entire form using equal-width side columns.
    left, center, right = st.columns([1, 1.25, 1], gap=None)

    with center:
        st.markdown(
            """
            <div class="auth-content">
                <div class="auth-brand">Aurex</div>
                <div class="auth-subtitle">
                    Sign in to continue your placement preparation
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        mode = st.radio(
            "Authentication",
            ["Login", "Create account"],
            horizontal=True,
            label_visibility="collapsed",
            key="auth_mode",
        )

        if mode == "Login":
            with st.form("aurex_login_form"):
                email = st.text_input(
                    "Email address",
                    placeholder="you@example.com",
                    key="login_email",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    key="login_password",
                )

                submitted = st.form_submit_button(
                    "Sign in",
                    use_container_width=True,
                )

            if submitted:
                if not email.strip() or not password:
                    st.error("Enter your email and password.")
                else:
                    try:
                        success, message, user = login(
                            email.strip(),
                            password,
                        )

                        if success:
                            st.session_state["user"] = user
                            st.session_state["authenticated"] = True
                            st.rerun()
                        else:
                            st.error(message)

                    except Exception:
                        st.error(
                            "We couldn't sign you in. Please try again."
                        )

        else:
            with st.form("aurex_signup_form"):
                full_name = st.text_input(
                    "Full name",
                    placeholder="Your name",
                    key="signup_name",
                )

                email = st.text_input(
                    "Email address",
                    placeholder="you@example.com",
                    key="signup_email",
                )

                password = st.text_input(
                    "Create password",
                    type="password",
                    placeholder="At least 8 characters",
                    key="signup_password",
                )

                confirm_password = st.text_input(
                    "Confirm password",
                    type="password",
                    placeholder="Re-enter your password",
                    key="signup_confirm_password",
                )

                submitted = st.form_submit_button(
                    "Create account",
                    use_container_width=True,
                )

            if submitted:
                try:
                    success, message = signup(
                        full_name.strip(),
                        email.strip(),
                        password,
                        confirm_password,
                    )

                    if success:
                        st.success(
                            "Account created successfully. Switch to Login."
                        )
                    else:
                        st.error(message)

                except Exception:
                    st.error(
                        "Account creation failed. Please try again."
                    )