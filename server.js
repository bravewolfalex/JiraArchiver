const express = require('express');
const cors = require('cors');
const axios = require('axios');
const archiver = require('archiver');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

class JiraClient {
  constructor(baseUrl, cookie) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.cookie = cookie;
  }

  async searchIssues(jql) {
    try {
      const response = await axios.get(`${this.baseUrl}/rest/api/2/search`, {
        params: {
          jql: jql,
          maxResults: 1000,
          fields: '*all'
        },
        headers: {
          'Cookie': this.cookie,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to search issues: ${error.message}`);
    }
  }

  async getIssue(issueKey) {
    try {
      const response = await axios.get(`${this.baseUrl}/rest/api/2/issue/${issueKey}`, {
        params: {
          fields: '*all'
        },
        headers: {
          'Cookie': this.cookie,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get issue ${issueKey}: ${error.message}`);
    }
  }

  async getComments(issueKey) {
    try {
      const response = await axios.get(`${this.baseUrl}/rest/api/2/issue/${issueKey}/comment`, {
        headers: {
          'Cookie': this.cookie,
          'Content-Type': 'application/json'
        }
      });
      return response.data.comments || [];
    } catch (error) {
      console.log(`Failed to get comments for ${issueKey}: ${error.message}`);
      return [];
    }
  }
}

function generateIssueHTML(issue, comments) {
  const fields = issue.fields;
  const key = issue.key;
  
  let commentsHTML = '';
  if (comments && comments.length > 0) {
    commentsHTML = `
      <div class="comments-section">
        <h3>Comments</h3>
        ${comments.map(comment => `
          <div class="comment">
            <div class="comment-author">${comment.author.displayName}</div>
            <div class="comment-date">${new Date(comment.created).toLocaleString()}</div>
            <div class="comment-body">${comment.body}</div>
          </div>
        `).join('')}
      </div>
    `;
  }

  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${key} - ${fields.summary}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .issue-header { background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .issue-key { font-size: 24px; font-weight: bold; color: #0052cc; }
        .issue-summary { font-size: 18px; margin: 10px 0; }
        .issue-details { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .detail-group { background: #f9f9f9; padding: 15px; border-radius: 5px; }
        .detail-label { font-weight: bold; color: #333; }
        .detail-value { margin-top: 5px; }
        .description { background: #fff; padding: 20px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 20px; }
        .comments-section { background: #fff; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .comment { background: #f9f9f9; padding: 15px; margin-bottom: 10px; border-radius: 5px; }
        .comment-author { font-weight: bold; color: #0052cc; }
        .comment-date { color: #666; font-size: 0.9em; }
        .comment-body { margin-top: 10px; }
        .status { padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; }
        .priority { padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; }
    </style>
</head>
<body>
    <div class="issue-header">
        <div class="issue-key">${key}</div>
        <div class="issue-summary">${fields.summary}</div>
    </div>
    
    <div class="issue-details">
        <div class="detail-group">
            <div class="detail-label">Status:</div>
            <div class="detail-value">
                <span class="status" style="background-color: ${fields.status.statusCategory.colorName}">${fields.status.name}</span>
            </div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Priority:</div>
            <div class="detail-value">
                <span class="priority" style="background-color: #ff5722">${fields.priority ? fields.priority.name : 'None'}</span>
            </div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Issue Type:</div>
            <div class="detail-value">${fields.issuetype.name}</div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Reporter:</div>
            <div class="detail-value">${fields.reporter ? fields.reporter.displayName : 'Unknown'}</div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Assignee:</div>
            <div class="detail-value">${fields.assignee ? fields.assignee.displayName : 'Unassigned'}</div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Created:</div>
            <div class="detail-value">${new Date(fields.created).toLocaleString()}</div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Updated:</div>
            <div class="detail-value">${new Date(fields.updated).toLocaleString()}</div>
        </div>
        
        <div class="detail-group">
            <div class="detail-label">Project:</div>
            <div class="detail-value">${fields.project.name}</div>
        </div>
    </div>
    
    ${fields.description ? `
    <div class="description">
        <h3>Description</h3>
        <div>${fields.description}</div>
    </div>
    ` : ''}
    
    ${commentsHTML}
</body>
</html>
  `;
}

function generateIndexHTML(issues) {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jira Issues Archive</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #0052cc; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .search-box { margin-bottom: 20px; }
        .search-box input { width: 300px; padding: 10px; border: 1px solid #ddd; border-radius: 3px; }
        .issues-table { width: 100%; border-collapse: collapse; }
        .issues-table th, .issues-table td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        .issues-table th { background: #f5f5f5; }
        .issues-table tr:hover { background: #f9f9f9; }
        .issue-key { color: #0052cc; text-decoration: none; font-weight: bold; }
        .issue-key:hover { text-decoration: underline; }
        .status { padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; }
        .priority { padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Jira Issues Archive</h1>
        <p>Total Issues: ${issues.length}</p>
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
            ${issues.map(issue => `
                <tr>
                    <td><a href="${issue.key}.html" class="issue-key">${issue.key}</a></td>
                    <td>${issue.fields.summary}</td>
                    <td><span class="status" style="background-color: ${issue.fields.status.statusCategory.colorName}">${issue.fields.status.name}</span></td>
                    <td><span class="priority" style="background-color: #ff5722">${issue.fields.priority ? issue.fields.priority.name : 'None'}</span></td>
                    <td>${issue.fields.assignee ? issue.fields.assignee.displayName : 'Unassigned'}</td>
                    <td>${new Date(issue.fields.created).toLocaleDateString()}</td>
                    <td>${new Date(issue.fields.updated).toLocaleDateString()}</td>
                </tr>
            `).join('')}
        </tbody>
    </table>
    
    <script>
        function filterIssues() {
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const table = document.getElementById('issuesTable');
            const rows = table.getElementsByTagName('tr');
            
            for (let i = 1; i < rows.length; i++) {
                const cells = rows[i].getElementsByTagName('td');
                let found = false;
                
                for (let j = 0; j < cells.length; j++) {
                    if (cells[j].textContent.toLowerCase().includes(filter)) {
                        found = true;
                        break;
                    }
                }
                
                rows[i].style.display = found ? '' : 'none';
            }
        }
    </script>
</body>
</html>
  `;
}

app.post('/api/export', async (req, res) => {
  const { jiraUrl, jiraCookie, jql } = req.body;
  
  if (!jiraUrl || !jiraCookie || !jql) {
    return res.status(400).json({ error: 'Missing required parameters' });
  }

  try {
    const jiraClient = new JiraClient(jiraUrl, jiraCookie);
    const searchResult = await jiraClient.searchIssues(jql);
    
    if (!searchResult.issues || searchResult.issues.length === 0) {
      return res.status(404).json({ error: 'No issues found for the given JQL' });
    }

    const tempDir = path.join(__dirname, 'temp', Date.now().toString());
    fs.mkdirSync(tempDir, { recursive: true });

    const archive = archiver('zip', {
      zlib: { level: 9 }
    });

    res.attachment('jira-export.zip');
    archive.pipe(res);

    const indexHTML = generateIndexHTML(searchResult.issues);
    archive.append(indexHTML, { name: 'index.html' });

    for (const issue of searchResult.issues) {
      try {
        const comments = await jiraClient.getComments(issue.key);
        const issueHTML = generateIssueHTML(issue, comments);
        archive.append(issueHTML, { name: `${issue.key}.html` });
      } catch (error) {
        console.error(`Error processing issue ${issue.key}:`, error.message);
        const issueHTML = generateIssueHTML(issue, []);
        archive.append(issueHTML, { name: `${issue.key}.html` });
      }
    }

    archive.finalize();

    archive.on('end', () => {
      fs.rmSync(tempDir, { recursive: true, force: true });
    });

  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});