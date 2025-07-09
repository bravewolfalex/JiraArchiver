# Manual Start Instructions for Windows

If the batch files don't work, follow these steps manually:

## Step 1: Open Command Prompt
1. Press `Win + R`
2. Type `cmd` and press Enter
3. Navigate to the project folder:
   ```
   cd C:\path\to\JiraArchiver
   ```

## Step 2: Install Dependencies
```
npm install
```

## Step 3: Start the Server
```
node server.js
```

## Step 4: Test
Open your browser and go to: http://localhost:3000

## Alternative: Use PowerShell
1. Press `Win + X` and select "Windows PowerShell"
2. Navigate to project folder:
   ```
   cd C:\path\to\JiraArchiver
   ```
3. Run:
   ```
   npm install
   node server.js
   ```

## Troubleshooting

### If you get "node is not recognized"
- Restart your computer after installing Node.js
- Or add Node.js to PATH manually:
  - Go to System Properties > Environment Variables
  - Add `C:\Program Files\nodejs\` to PATH

### If you get "npm is not recognized"
- npm comes with Node.js, so reinstall Node.js

### If port 3000 is busy
- Kill processes using port 3000:
  ```
  netstat -ano | findstr :3000
  taskkill /PID <PID_NUMBER> /F
  ```
- Or change port in server.js to 3001

### If dependencies fail to install
- Try:
  ```
  npm cache clean --force
  npm install
  ```

## Quick Test Commands
```
node --version
npm --version
npm install
node server.js
```