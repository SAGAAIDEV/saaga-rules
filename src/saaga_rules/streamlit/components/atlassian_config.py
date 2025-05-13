import streamlit as st


def render_atlassian_config():
    """
    Renders the Atlassian (Jira & Confluence) configuration section
    and returns the entered credentials.
    Initializes its own session state variables if they don't exist.
    """
    # Initialize session state for input fields if they don't exist
    if "component_jira_username" not in st.session_state:
        st.session_state.component_jira_username = ""
    if "component_jira_token" not in st.session_state:
        st.session_state.component_jira_token = ""
    if "component_confluence_username" not in st.session_state:
        st.session_state.component_confluence_username = ""
    if "component_confluence_token" not in st.session_state:
        st.session_state.component_confluence_token = ""

    with st.expander("Atlassian (Jira & Confluence) Configuration", expanded=True):
        st.markdown(
            "Enter your Jira and Confluence credentials. These will update the `mcp-atlassian` section in the configuration."
        )
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.component_jira_username = st.text_input(
                "Jira Username",
                value=st.session_state.component_jira_username,
                help="Your Jira email or username.",
                key="jira_user_comp",  # Unique key for component
            )
            st.session_state.component_confluence_username = st.text_input(
                "Confluence Username",
                value=st.session_state.component_confluence_username,
                help="Your Confluence email or username.",
                key="confluence_user_comp",  # Unique key for component
            )
        with col2:
            st.session_state.component_jira_token = st.text_input(
                "Jira API Token",
                type="password",
                value=st.session_state.component_jira_token,
                help="Your Jira API token. Stored as part of the command arguments.",
                key="jira_token_comp",  # Unique key for component
            )
            st.session_state.component_confluence_token = st.text_input(
                "Confluence API Token",
                type="password",
                value=st.session_state.component_confluence_token,
                help="Your Confluence API token. Stored as part of the command arguments.",
                key="confluence_token_comp",  # Unique key for component
            )

    return (
        st.session_state.component_jira_username,
        st.session_state.component_jira_token,
        st.session_state.component_confluence_username,
        st.session_state.component_confluence_token,
    )
