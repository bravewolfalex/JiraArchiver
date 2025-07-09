#!/usr/bin/env python3
"""
Jira Archiver - Python Version
Uses only Python standard library modules
"""

import json
import os
import urllib.request
import urllib.parse
import urllib.error
import zipfile
import io
import tempfile
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class JiraClient:
    def __init__(self, base_url, cookie):
        self.base_url = base_url.rstrip('/')
        self.cookie = cookie
    
    def _make_request(self, url, params=None):
        """Make HTTP request to Jira API"""
        if params:
            url += '?' + urllib.parse.urlencode(params)
        
        req = urllib.request.Request(url)
        req.add_header('Cookie', self.cookie)
        req.add_header('Content-Type', 'application/json')
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTP Error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise Exception(f"URL Error: {e.reason}")
    
    def search_issues(self, jql):
        """Search for issues using JQL"""
        url = f"{self.base_url}/rest/api/2/search"
        params = {
            'jql': jql,
            'maxResults': 1000,
            'fields': '*all'
        }
        return self._make_request(url, params)
    
    def get_issue(self, issue_key):
        """Get detailed issue information"""
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"
        params = {'fields': '*all'}
        return self._make_request(url, params)
    
    def get_comments(self, issue_key):
        """Get comments for an issue"""
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment"
            data = self._make_request(url)
            return data.get('comments', [])
        except Exception as e:
            print(f"Failed to get comments for {issue_key}: {e}")
            return []


class HTMLGenerator:
    @staticmethod
    def generate_issue_html(issue, comments):
        """Generate HTML for a single issue"""
        fields = issue['fields']
        key = issue['key']
        
        # Generate comments HTML
        comments_html = ''
        if comments:
            comments_html = '''
            <div class="comments-section">
                <h3>Comments</h3>
                {}
            </div>
            '''.format(''.join([
                f'''
                <div class="comment">
                    <div class="comment-author">{comment.get('author', {}).get('displayName', 'Unknown')}</div>
                    <div class="comment-date">{datetime.fromisoformat(comment['created'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')}</div>
                    <div class="comment-body">{comment.get('body', '')}</div>
                </div>
                ''' for comment in comments
            ]))
        
        # Helper function to safely get nested values
        def safe_get(obj, *keys):
            for key in keys:
                if isinstance(obj, dict) and key in obj:
                    obj = obj[key]
                else:
                    return None
            return obj
        
        # Generate issue HTML
        html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{key} - {fields.get('summary', 'No title')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .issue-header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .issue-key {{ font-size: 24px; font-weight: bold; color: #0052cc; }}
        .issue-summary {{ font-size: 18px; margin: 10px 0; }}
        .issue-details {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
        .detail-group {{ background: #f9f9f9; padding: 15px; border-radius: 5px; }}
        .detail-label {{ font-weight: bold; color: #333; }}
        .detail-value {{ margin-top: 5px; }}
        .description {{ background: #fff; padding: 20px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 20px; }}
        .comments-section {{ background: #fff; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
        .comment {{ background: #f9f9f9; padding: 15px; margin-bottom: 10px; border-radius: 5px; }}
        .comment-author {{ font-weight: bold; color: #0052cc; }}
        .comment-date {{ color: #666; font-size: 0.9em; }}
        .comment-body {{ margin-top: 10px; }}
        .status {{ padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; background-color: #0052cc; }}
        .priority {{ padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; background-color: #ff5722; }}
    </style>
</head>
<body>
    <div class="issue-header">
        <div class="issue-key">{key}</div>
        <div class="issue-summary">{fields.get('summary', 'No summary')}</div>
    </div>
    
    <div class="issue-details">
        <div class="detail-group">
            <div class="detail-label">Status:</div>
            <div class="detail-value">
                <span class="status">{safe_get(fields, 'status', 'name') or 'Unknown'}</span>
            </div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Priority:</div>
            <div class="detail-value">
                <span class="priority">{safe_get(fields, 'priority', 'name') or 'None'}</span>
            </div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Issue Type:</div>
            <div class="detail-value">{safe_get(fields, 'issuetype', 'name') or 'Unknown'}</div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Reporter:</div>
            <div class="detail-value">{safe_get(fields, 'reporter', 'displayName') or 'Unknown'}</div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Assignee:</div>
            <div class="detail-value">{safe_get(fields, 'assignee', 'displayName') or 'Unassigned'}</div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Created:</div>
            <div class="detail-value">{datetime.fromisoformat(fields['created'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S') if fields.get('created') else 'Unknown'}</div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Updated:</div>
            <div class="detail-value">{datetime.fromisoformat(fields['updated'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S') if fields.get('updated') else 'Unknown'}</div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Project:</div>
            <div class="detail-value">{safe_get(fields, 'project', 'name') or 'Unknown'}</div>
        </div>
    </div>
    
    {f'''
    <div class="description">
        <h3>Description</h3>
        <div>{fields.get('description', 'No description')}</div>
    </div>
    ''' if fields.get('description') else ''}
    
    {comments_html}
</body>
</html>
        '''
        return html
    
    @staticmethod
    def generate_index_html(issues):
        """Generate HTML for the index page"""
        def safe_get(obj, *keys):
            for key in keys:
                if isinstance(obj, dict) and key in obj:
                    obj = obj[key]
                else:
                    return None
            return obj
        
        html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jira Issues Archive</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #0052cc; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .search-box {{ margin-bottom: 20px; }}
        .search-box input {{ width: 300px; padding: 10px; border: 1px solid #ddd; border-radius: 3px; }}
        .issues-table {{ width: 100%; border-collapse: collapse; }}
        .issues-table th, .issues-table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        .issues-table th {{ background: #f5f5f5; }}
        .issues-table tr:hover {{ background: #f9f9f9; }}
        .issue-key {{ color: #0052cc; text-decoration: none; font-weight: bold; }}
        .issue-key:hover {{ text-decoration: underline; }}
        .status {{ padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; background-color: #0052cc; }}
        .priority {{ padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; background-color: #ff5722; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Jira Issues Archive</h1>
        <p>Total Issues: {len(issues)}</p>
    </div>
    
    <div class="search-box">
        <input type="text" id="searchInput" placeholder="Search by issue key, summary, or assignee..." onkeyup="filterIssues()">
    </div>
    
    <table class="issues-table" id="issuesTable">
        <thead>
            <tr>
                <th>Key</th>
                <th>Summary</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Assignee</th>
                <th>Created</th>
                <th>Updated</th>
            </tr>
        </thead>
        <tbody>
            {''.join([f'''
                <tr>
                    <td><a href="{issue['key']}.html" class="issue-key">{issue['key']}</a></td>
                    <td>{issue['fields'].get('summary', 'No summary')}</td>
                    <td><span class="status">{safe_get(issue, 'fields', 'status', 'name') or 'Unknown'}</span></td>
                    <td><span class="priority">{safe_get(issue, 'fields', 'priority', 'name') or 'None'}</span></td>
                    <td>{safe_get(issue, 'fields', 'assignee', 'displayName') or 'Unassigned'}</td>
                    <td>{datetime.fromisoformat(issue['fields']['created'].replace('Z', '+00:00')).strftime('%Y-%m-%d') if issue['fields'].get('created') else 'Unknown'}</td>
                    <td>{datetime.fromisoformat(issue['fields']['updated'].replace('Z', '+00:00')).strftime('%Y-%m-%d') if issue['fields'].get('updated') else 'Unknown'}</td>
                </tr>
            ''' for issue in issues])}
        </tbody>
    </table>
    
    <script>
        function filterIssues() {{
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const table = document.getElementById('issuesTable');
            const rows = table.getElementsByTagName('tr');
            
            for (let i = 1; i < rows.length; i++) {{
                const cells = rows[i].getElementsByTagName('td');
                let found = false;
                
                for (let j = 0; j < cells.length; j++) {{
                    if (cells[j].textContent.toLowerCase().includes(filter)) {{
                        found = true;
                        break;
                    }}
                }}
                
                rows[i].style.display = found ? '' : 'none';
            }}
        }}
    </script>
</body>
</html>
        '''
        return html


class JiraArchiverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path == '/index.html':
            self.serve_file('static/index.html', 'text/html')
        else:
            self.send_error(404, "File not found")
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/export':
            self.handle_export()
        else:
            self.send_error(404, "Endpoint not found")
    
    def serve_file(self, filename, content_type):
        """Serve static files"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "File not found")
    
    def handle_export(self):
        """Handle Jira export request"""
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            jira_url = data.get('jiraUrl')
            jira_cookie = data.get('jiraCookie')
            jql = data.get('jql')
            
            if not all([jira_url, jira_cookie, jql]):
                self.send_error(400, "Missing required parameters")
                return
            
            # Initialize Jira client
            jira_client = JiraClient(jira_url, jira_cookie)
            
            # Search for issues
            search_result = jira_client.search_issues(jql)
            issues = search_result.get('issues', [])
            
            if not issues:
                self.send_error(404, "No issues found for the given JQL")
                return
            
            # Create ZIP file in memory
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Generate and add index.html
                index_html = HTMLGenerator.generate_index_html(issues)
                zip_file.writestr('index.html', index_html)
                
                # Generate and add individual issue files
                for issue in issues:
                    try:
                        comments = jira_client.get_comments(issue['key'])
                        issue_html = HTMLGenerator.generate_issue_html(issue, comments)
                        zip_file.writestr(f"{issue['key']}.html", issue_html)
                    except Exception as e:
                        print(f"Error processing issue {issue['key']}: {e}")
                        issue_html = HTMLGenerator.generate_issue_html(issue, [])
                        zip_file.writestr(f"{issue['key']}.html", issue_html)
            
            # Send ZIP file
            zip_buffer.seek(0)
            zip_data = zip_buffer.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition', 'attachment; filename="jira-export.zip"')
            self.send_header('Content-Length', str(len(zip_data)))
            self.end_headers()
            self.wfile.write(zip_data)
            
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")


def run_server(port=3000):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, JiraArchiverHandler)
    print(f"Server running on http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.shutdown()


if __name__ == '__main__':
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    run_server()