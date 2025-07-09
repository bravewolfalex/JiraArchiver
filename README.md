# Jira Archiver

A tool to export Jira issues to HTML files based on JQL queries. Creates a ZIP file containing individual HTML pages for each issue plus a searchable index.

## Features

- Export Jira issues using JQL queries
- Authentication via Jira cookie
- Generate individual HTML files for each issue
- Create a searchable index.html with all issues
- Include issue details, comments, and metadata
- Download as ZIP file

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

## Usage

1. Start the server:
   ```bash
   npm start
   ```

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

Each issue HTML file includes:
- Issue summary and key
- Status, priority, and other metadata
- Description
- Comments
- Creation and update dates
- Assignee and reporter information

## Development

For development with auto-restart:
```bash
npm run dev
```

## Dependencies

- Express.js for the web server
- Axios for HTTP requests to Jira API
- Archiver for ZIP file creation
- CORS for cross-origin requests

## Security Notes

- This tool uses cookie-based authentication
- Cookies are not stored on the server
- All processing happens server-side
- No sensitive data is logged or persisted