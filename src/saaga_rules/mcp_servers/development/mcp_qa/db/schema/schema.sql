-- Schema definitions for creating tables

-- Source files table
CREATE TABLE IF NOT EXISTS source_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    file_hash TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Pytest files table
CREATE TABLE IF NOT EXISTS pytest_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    source_file_id INTEGER,
    pytest_summary TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (source_file_id) REFERENCES source_files (id)
);

-- Pytest errors table
CREATE TABLE IF NOT EXISTS pytest_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT NOT NULL,
    test_file_id INTEGER NOT NULL,
    outcome TEXT NOT NULL,
    error_type TEXT NOT NULL,
    result TEXT DEFAULT '[]',
    longrepr TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    FOREIGN KEY (test_file_id) REFERENCES pytest_files (id)
);

-- Pytest collection errors table
CREATE TABLE IF NOT EXISTS pytest_collection_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT NOT NULL,
    test_file_id INTEGER NOT NULL,
    outcome TEXT NOT NULL,
    error_type TEXT NOT NULL,
    result TEXT DEFAULT '[]',
    longrepr TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    FOREIGN KEY (test_file_id) REFERENCES pytest_files (id)
);

-- Coverage issues table
CREATE TABLE IF NOT EXISTS coverage_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    source_file_id INTEGER,
    line_number INTEGER NOT NULL,
    is_excluded BOOLEAN DEFAULT FALSE,
    created_at TEXT NOT NULL,
    FOREIGN KEY (source_file_id) REFERENCES source_files (id)
);

-- Coverage branches table
CREATE TABLE IF NOT EXISTS coverage_branches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coverage_issue_id INTEGER NOT NULL,
    source_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    condition TEXT NOT NULL,
    branch_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (coverage_issue_id) REFERENCES coverage_issues (id) ON DELETE CASCADE
); 