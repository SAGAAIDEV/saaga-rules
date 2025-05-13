# saaga-rules

# Teamworking agreement

This is to avoid unclear expectations.


This is an AI-first organization. AI rules should be at the forefront of every task. This is what you use to build
S.A.A.G.A

#Onboard

The tutorial is built into the rule.

Everything is a rule.




## Adding as a Submodule

To add this repository as a submodule to another project, follow these steps:

1.  **Navigate to your other project's directory** in the terminal.
2.  **Run the `git submodule add` command** with the repository URL and a desired path:
    ```bash
    git submodule add https://github.com/SAGAAIDEV/saaga-rules.git ./.cursor/rules/saaga-rules
    ```
3.  **Stage the changes** in your main project:
    ```bash
    git add .gitmodules <path_to_submodule>
    ```
4.  **Commit the changes**:
    ```bash
    git commit -m "Add saaga-rules submodule"
    ```
5.  **Push the changes** to your remote repository:
    ```bash
    git push
    ```




## Running the MCP Configuration Tool

To run the MCP (Multi-Capability Provider) configuration Streamlit application using the `configure.sh` script:

1.  Ensure you have `uv` and `streamlit` installed and available in your Python environment.
2.  Make the script executable (this usually only needs to be done once):
    ```sh
    chmod +x configure.sh
    ```
3.  Execute the script from the project root directory:
    ```sh
    ./configure.sh
    ```

This will start the Streamlit server, and you can access the application in your web browser, typically at `http://localhost:8501`.



