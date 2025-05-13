import streamlit as st
import json
import os
from saaga_rules.streamlit.components.atlassian_config import render_atlassian_config
from saaga_rules.streamlit.components.github_config import render_github_config

# --- Configuration Paths ---
SRC_TEMPLATE_PATH = "src/saaga_rules/utils/mcp_template.json"
# OUTPUT_DIR is now dynamic
# OUTPUT_PATH is now dynamic


# --- Helper Functions ---
def load_or_create_template():
    """Loads the template from SRC_TEMPLATE_PATH. If not found, returns a default structure."""
    try:
        with open(SRC_TEMPLATE_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning(
            f"Template file not found at `{SRC_TEMPLATE_PATH}`. Using a default base structure."
        )
        # Default structure matching the expected schema if the template is missing
        return {
            "mcpServers": {
                "base": {
                    "command": "uv",
                    "args": [
                        "--directory=/Users/andrew/saga/saaga-mcp-base",
                        "run",
                        "server",
                    ],
                    "env": {"sqldb_path": "./saaga-mcp-base.sqlite3"},
                }
            },
            "mcp-atlassian": {
                "command": "uvx",
                "args": [
                    "--confluence-url=https://saaga-team.atlassian.net",  # Index 0
                    "--confluence-username=",  # Index 1
                    "--confluence-token=",  # Index 2
                    "--jira-url=https://saaga-team.atlassian.net",  # Index 3
                    "--jira-username=",  # Index 4
                    "--jira-token=",  # Index 5
                ],
            },
            "github": {
                "command": "docker",
                "args": [
                    "run",
                    "-i",
                    "--rm",
                    "-e",
                    "GITHUB_PERSONAL_ACCESS_TOKEN",
                    "ghcr.io/github/github-mcp-server",
                ],
                "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": ""},
            },
        }
    except json.JSONDecodeError:
        st.error(
            f"Error decoding JSON from `{SRC_TEMPLATE_PATH}`. Please check the file format."
        )
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while loading the template: {e}")
        return None


def save_config_to_output(config_data, output_dir, output_filename="mcp.json"):
    """Saves the configuration data to the specified path."""
    output_path = os.path.join(output_dir, output_filename)
    try:
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(config_data, f, indent=4)
        return True, output_path
    except Exception as e:
        st.error(
            f"An error occurred while saving the configuration to `{output_path}`: {e}"
        )
        return False, output_path


# --- Streamlit App UI ---
st.set_page_config(layout="wide")
st.title("MCP Configuration Generator")

# --- Output Directory Selection ---
st.subheader("Output Configuration")
if "output_directory" not in st.session_state:
    st.session_state.output_directory = ".cursor/rules"  # Default value

st.session_state.output_directory = st.text_input(
    "Output Directory for mcp.json",
    value=st.session_state.output_directory,
    help="Enter the directory path where the `mcp.json` file will be saved. It will be created if it doesn't exist.",
)
OUTPUT_DIR = st.session_state.output_directory  # Dynamically set OUTPUT_DIR
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "mcp.json")  # Dynamically set OUTPUT_PATH

st.caption(
    f"This tool helps configure MCP server settings. It reads from `{SRC_TEMPLATE_PATH}` (if available) and writes the final configuration to a `mcp.json` file in the directory specified above."
)
st.divider()


# --- Render Components ---
# Atlassian Configuration
(
    jira_username,
    jira_token,
    confluence_username,
    confluence_token,
) = render_atlassian_config()

st.divider()

# GitHub Configuration
github_token = render_github_config()

st.divider()

# --- Generate Button & Logic ---
if st.button("Generate/Update mcp.json", type="primary", use_container_width=True):
    if not OUTPUT_DIR:
        st.error("Output directory cannot be empty. Please specify a valid path.")
    else:
        mcp_config = load_or_create_template()

        if mcp_config:
            config_updated_flag = False  # To track if any changes were made

            # --- Update Atlassian Section ---
            if (
                "mcp-atlassian" in mcp_config
                and isinstance(mcp_config.get("mcp-atlassian"), dict)
                and "args" in mcp_config["mcp-atlassian"]
                and isinstance(mcp_config["mcp-atlassian"]["args"], list)
                and len(mcp_config["mcp-atlassian"]["args"]) >= 6
            ):
                args = mcp_config["mcp-atlassian"]["args"]
                if confluence_username:
                    args[1] = f"--confluence-username={confluence_username}"
                    config_updated_flag = True
                if confluence_token:
                    args[2] = f"--confluence-token={confluence_token}"
                    config_updated_flag = True
                if jira_username:
                    args[4] = f"--jira-username={jira_username}"
                    config_updated_flag = True
                if jira_token:
                    args[5] = f"--jira-token={jira_token}"
                    config_updated_flag = True
            elif jira_username or jira_token or confluence_username or confluence_token:
                st.warning(
                    "Attempted to update Atlassian credentials, but the 'mcp-atlassian' section or its 'args' are missing or malformed in the template. Atlassian configuration was not updated."
                )

            # --- Update GitHub Section ---
            if (
                "github" in mcp_config
                and isinstance(mcp_config.get("github"), dict)
                and "env" in mcp_config["github"]
                and isinstance(mcp_config["github"]["env"], dict)
            ):
                if github_token:
                    mcp_config["github"]["env"][
                        "GITHUB_PERSONAL_ACCESS_TOKEN"
                    ] = github_token
                    config_updated_flag = True
            elif github_token:
                st.warning(
                    "Attempted to update GitHub token, but the 'github' section or its 'env' are missing or malformed in the template. GitHub configuration was not updated."
                )

            # --- Save Configuration ---
            current_output_path = os.path.join(
                OUTPUT_DIR, "mcp.json"
            )  # Recalculate based on current OUTPUT_DIR
            if config_updated_flag:
                success, saved_path = save_config_to_output(mcp_config, OUTPUT_DIR)
                if success:
                    st.success(
                        f"Successfully generated/updated `{saved_path}` with your configurations."
                    )
                    st.balloons()
            else:
                st.info(
                    "No new values were provided to update the configuration. The file remains unchanged if it exists, or a base template might have been created if it didn't."
                )
                if not os.path.exists(current_output_path):
                    success, saved_path = save_config_to_output(mcp_config, OUTPUT_DIR)
                    if success:
                        st.info(
                            f"A new configuration file based on the template has been saved to `{saved_path}`."
                        )
        else:
            st.error(
                "MCP template could not be loaded or initialized. Configuration generation aborted."
            )

st.markdown("---")
st.caption(
    "Important: Always handle your tokens and credentials securely. This tool saves them into the `mcp.json` file as per the MCP server requirements."
)
