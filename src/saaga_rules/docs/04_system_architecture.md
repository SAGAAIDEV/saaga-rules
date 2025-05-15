# 04: System Architecture

This document outlines the system architecture of the MCP Server Configuration Program, drawing from the technical specifications and core technologies employed.

## 1. Overview

The MCP Server Configuration Program is designed to provide a user-friendly interface for configuring various MCP server instances, managing their associated workflows, and generating their respective `MCP.json` files. The architecture prioritizes modularity, extensibility, and ease of use.

## 2. Core Components

The system is composed of the following core components:

### 2.1. User Interface (UI)

*   **Technology:** Streamlit
*   **Purpose:** Provides an interactive web interface for users to input server details, manage configurations, and initiate the generation of `MCP.json` files.
*   **Key Features:**
    *   Intuitive forms for configuration.
    *   Real-time feedback and error messaging.
    *   Management of multiple MCP server configurations.

### 2.2. Backend Logic

*   **Technology:** Python
*   **Purpose:** Handles the core application logic, including:
    *   Processing user inputs from the UI.
    *   Interacting with MCP Server Components.
    *   Orchestrating the generation of `MCP.json` files.
    *   Managing internal configuration storage (e.g., for sensitive data, potentially using environment variables or encrypted files initially).

### 2.3. MCP Server Components

*   **Concept:** These are modular, independent units, each representing a specific MCP server type (e.g., JIRA, GitHub, AWS).
*   **Location:** Organized within a dedicated Python package (e.g., `src/saaga_rules/mcp_servers`).
*   **Responsibilities of each component:**
    *   Define required configuration parameters.
    *   Validate user-provided inputs.
    *   Generate its specific section of the `MCP.json` file.
*   **Discoverability:** The main application can dynamically discover and load these components.
*   **Architectural Analogy:** Conceptually, these components are treated as submodules, promoting separation of concerns. While this configuration program centralizes their setup, each component mirrors the idea that the underlying MCP server often operates in its own distinct environment or requires unique credentials.

### 2.4. `MCP.json` File Generator

*   **Purpose:** Consolidates the configurations from all active MCP Server Components and produces the final `MCP.json` file.
*   **Output:** The generated file can be saved to a user-specified location or a default path. The system supports both creating new files and updating existing ones.

## 3. Data and Workflow

1.  **User Interaction:** The user launches the application (e.g., via `streamlit run app.py`) and interacts with the Streamlit UI.
2.  **Configuration Input:** The user selects MCP server types and provides the necessary credentials and parameters through the UI.
3.  **Input Validation:** The backend, leveraging the appropriate MCP Server Component, validates the inputs.
4.  **Configuration Compilation:** Validated configurations are compiled by the backend.
5.  **`MCP.json` Generation:** The `MCP.json` File Generator creates or updates the `MCP.json` file with the compiled configurations.

## 4. Key Architectural Principles

*   **Modularity:** Ensures that different MCP server types are handled by distinct, maintainable components.
*   **Extensibility:** New MCP server types can be added by creating new components without major changes to the core system.
*   **Separation of Concerns:** The UI, backend logic, and individual server configurations are kept distinct.
*   **User-Friendliness:** Prioritized through the use of Streamlit and clear feedback mechanisms.

## 5. Target Protocol

*   **MCP (Model Context Protocol):** The entire system is geared towards managing and generating configurations for server instances that adhere to the Model Context Protocol specification.

## 6. Future Architectural Considerations

*   **Formal Plugin System:** Transitioning the MCP Server Components into a more formal plugin architecture.
*   **Advanced Schema Validation:** Implementing robust schema validation for the generated `MCP.json` files.
*   **Enhanced Secrets Management:** Integrating with dedicated secrets management systems. 