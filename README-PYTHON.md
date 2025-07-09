# Jira Archiver - Python Version

A Python-based tool to export Jira issues to HTML files using only Python standard library modules. **No external dependencies required.**

## Features

- Uses only Python standard library (no pip install needed)
- Export Jira issues using JQL queries
- Authentication via Jira cookie
- Generate individual HTML files for each issue
- Create a searchable index.html with all issues
- Include issue details, comments, and metadata
- Download as ZIP file

## Requirements

- Python 3.6+ (no additional packages needed)
- Web browser

## Installation

**No installation required!** This version uses only Python standard library modules.

## Usage

### Windows
```cmd
start.py.bat
```

### Unix/Linux/macOS
```bash
./start.py.sh
```

### Manual Start
```bash
python server.py
```
or
```bash
python3 server.py
```

## Usage Instructions

1. Start the server using one of the methods above
2. Open your browser and go to `http://localhost:3000`
3. Fill in the form:
   - **Jira URL**: Your Jira instance URL (e.g., https://yourcompany.atlassian.net)
   - **Jira Cookie**: Copy the cookie from your browser's developer tools while logged into Jira
   - **JQL Query**: Enter a JQL query to filter issues
4. Click "Export to ZIP" to download the archive

## Getting Your Jira Cookie

1. Log into your Jira instance in your browser
2. Open Developer Tools (F12)
3. Go to the Application/Storage tab
4. Find "Cookies" in the left sidebar
5. Click on your Jira domain
6. Copy the entire cookie string (including JSESSIONID and other session tokens)

## Example JQL Queries

- `project = MYPROJECT AND status = Done`
- `assignee = currentUser() AND created >= -30d`
- `project = PROJ AND priority = High`
- `text ~ "bug" AND resolved >= -7d`

## Output Structure

The generated ZIP file contains:
- `index.html` - Searchable list of all issues
- `ISSUE-KEY.html` - Individual HTML file for each issue

## File Structure

```
JiraArchiver/
├── server.py           # Main Python server (uses only standard library)
├── static/
│   └── index.html      # Frontend interface
├── start.py.bat        # Windows startup script
├── start.py.sh         # Unix/Linux/macOS startup script
└── README-PYTHON.md    # This file
```

## Advantages of Python Version

- **No dependencies**: Uses only Python standard library
- **Corporate friendly**: Works in restricted environments
- **Lightweight**: No node_modules or package installations
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Simple**: Just run the Python script

## Modules Used (All Standard Library)

- `http.server` - Web server
- `urllib.request` - HTTP requests to Jira API
- `json` - JSON parsing
- `zipfile` - ZIP file creation
- `datetime` - Date/time handling
- `os` - File system operations
- `io` - In-memory file operations

## Troubleshooting

### Python not found
- Install Python from https://www.python.org/downloads/
- Make sure Python is in your system PATH

### Port 3000 in use
- Edit `server.py` and change the port number in the `run_server()` call

### Permission denied (Unix/Linux/macOS)
- Run: `chmod +x start.py.sh`

### Jira connection issues
- Verify your Jira URL is correct
- Check that your cookie is still valid
- Ensure you have permissions to access the issues in your JQL query

## Security Notes

- This tool uses cookie-based authentication
- Cookies are not stored on the server
- All processing happens server-side
- No sensitive data is logged or persisted