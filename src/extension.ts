import * as vscode from 'vscode';
import { spawn } from 'child_process';
import * as path from 'path';

export function activate(context: vscode.ExtensionContext) {
    let selectedFiles: string[] = [];
    let projectPath: string = '';

    context.subscriptions.push(
        vscode.commands.registerCommand('extension.testAngularComponents', () => {
            const panel = vscode.window.createWebviewPanel(
                'testAngularComponents',
                'Test Angular Components',
                vscode.ViewColumn.One,
                {
                    enableScripts: true
                }
            );

            panel.webview.html = getWebviewContent();

            panel.webview.onDidReceiveMessage(
                message => {
                    switch (message.command) {
                        case 'checkProject':
                            projectPath = message.projectPath;
                            listAngularFiles(projectPath, panel);
                            break;
                        case 'generateProject':
                            const fileIndices = message.fileIndices.split(',').map((index: string) => parseInt(index.trim(), 10) - 1);
                            const selectedFilesToGenerate = fileIndices.map((index: number) => selectedFiles[index]);
                            console.log("Selected Files to Generate: ", selectedFilesToGenerate); // Debugging line
                            generateProject(projectPath, selectedFilesToGenerate, panel);
                            break;
                    }
                },
                undefined,
                context.subscriptions
            );
        })
    );

    function listAngularFiles(projectPath: string, panel: vscode.WebviewPanel) {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('Workspace folder not found.');
            return;
        }

        const workspaceRoot = workspaceFolders[0].uri.fsPath;
        const pythonScriptPath = path.join(workspaceRoot, 'src', 'backend', 'backend.py');

        const pythonProcess = spawn('python', [pythonScriptPath, 'list', projectPath]);

        pythonProcess.stdout.on('data', (data: Buffer) => {
            const angularFiles = JSON.parse(data.toString());
            selectedFiles = angularFiles;
            let fileListHtml = '<ol>';
            angularFiles.forEach((file: string, index: number) => {
                fileListHtml += `<li>${file}</li>`;
            });
            fileListHtml += '</ol>';
            panel.webview.postMessage({
                command: 'updateFileList',
                html: fileListHtml
            });
        });

        pythonProcess.stderr.on('data', (data: Buffer) => {
            panel.webview.postMessage({ command: 'updateStatus', text: `Error: ${data.toString()}` });
        });

        pythonProcess.on('close', (code: number) => {
            if (code !== 0) {
                panel.webview.postMessage({ command: 'updateStatus', text: 'Failed to list Angular files.' });
            }
        });
    }

function generateProject(projectPath: string, selectedFiles: string[], panel: vscode.WebviewPanel) {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('Workspace folder not found.');
        return;
    }

    const workspaceRoot = workspaceFolders[0].uri.fsPath;
    const pythonScriptPath = path.join(workspaceRoot, 'src', 'backend', 'backend.py');

    const pythonProcess = spawn('python', [pythonScriptPath, 'generate', projectPath, ...selectedFiles], {
        cwd: workspaceRoot,
        env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    });

    panel.webview.postMessage({ command: 'updateStatus', text: 'Generating project...' });

    let output = '';

    pythonProcess.stdout.on('data', (data: Buffer) => {
        output += data.toString();
        panel.webview.postMessage({ command: 'updateStatus', text: data.toString() });
    });

    pythonProcess.stderr.on('data', (data: Buffer) => {
        output += `Error: ${data.toString()}`;
        panel.webview.postMessage({ command: 'updateStatus', text: `Error: ${data.toString()}` });
    });

    pythonProcess.on('close', (code: number) => {
        if (code === 0) {
            const match = output.match(/The test project has been set up at: (.+)/);
            const newProjectPath = match ? match[1].trim() : null;
            if (newProjectPath) {
                panel.webview.postMessage({ command: 'updateStatus', text: `Project generated successfully at ${newProjectPath}.\n${output}` });
                vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(newProjectPath), true);
            } else {
                panel.webview.postMessage({ command: 'updateStatus', text: `Project generated successfully but could not determine the project path.\n${output}` });
            }
        } else {
            panel.webview.postMessage({ command: 'updateStatus', text: `Project generation failed.\n${output}` });
        }
    });
}

}

function getWebviewContent() {
    return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Test Angular Components</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                form {
                    margin-bottom: 20px;
                }
                #status {
                    width: 80%;
                    max-width: 800px;
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    padding: 10px;
                    margin-top: 20px;
                    white-space: pre-wrap;
                    overflow-wrap: break-word;
                }
                #file-selection {
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body>
            <h1>Enter Angular Project Path</h1>
            <form id="project-path-form">
                <label for="projectPath">Project Path:</label>
                <input type="text" id="projectPath" name="projectPath">
                <button type="button" onclick="checkProject()">Check</button>
            </form>
            <div id="file-selection" style="display: none;">
                <h2>Select Files</h2>
                <div id="file-list"></div>
                <label for="fileIndices">Enter the numbers of the files to test (comma-separated):</label>
                <input type="text" id="fileIndices" name="fileIndices">
                <button type="button" onclick="generateProject()">Generate Project</button>
            </div>
            <div id="status"></div>
            <script>
                const vscode = acquireVsCodeApi();
                function checkProject() {
                    const projectPath = document.getElementById('projectPath').value;
                    vscode.postMessage({ command: 'checkProject', projectPath });
                }
                function generateProject() {
                    const fileIndices = document.getElementById('fileIndices').value;
                    vscode.postMessage({ command: 'generateProject', fileIndices });
                }
                window.addEventListener('message', event => {
                    const message = event.data;
                    switch (message.command) {
                        case 'updateFileList':
                            document.getElementById('file-list').innerHTML = message.html;
                            document.getElementById('file-selection').style.display = 'block';
                            break;
                        case 'updateStatus':
                            const statusDiv = document.getElementById('status');
                            statusDiv.innerText += message.text + '\\n';
                            statusDiv.scrollTop = statusDiv.scrollHeight;
                            break;
                    }
                });
            </script>
        </body>
        </html>
    `;
}

export function deactivate() {}
