import streamlit as st


def render_github_config():
    """
    Renders the GitHub configuration section and returns the entered token.
    Initializes its own session state variable if it doesn't exist.
    """
    # Initialize session state for input field if it doesn't exist
    if "component_github_token" not in st.session_state:
        st.session_state.component_github_token = ""

    with st.expander("GitHub Configuration", expanded=True):
        st.markdown(
            "Enter your GitHub Personal Access Token. This will update the `github` section's environment variables."
        )
        st.session_state.component_github_token = st.text_input(
            "GitHub Personal Access Token (PAT)",
            type="password",
            value=st.session_state.component_github_token,
            help="A GitHub PAT with appropriate permissions. Stored in the `env` block.",
            key="github_token_comp",  # Unique key for component
        )
    return st.session_state.component_github_token
