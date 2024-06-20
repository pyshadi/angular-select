"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
const child_process_1 = require("child_process");
function activate(context) {
    context.subscriptions.push(vscode.commands.registerCommand('extension.testAngularComponents', () => {
        const panel = vscode.window.createWebviewPanel('testAngularComponents', 'Test Angular Components', vscode.ViewColumn.One, {
            enableScripts: true
        });
        panel.webview.html = getWebviewContent();
        panel.webview.onDidReceiveMessage(message => {
            switch (message.command) {
                case 'generateProject':
                    vscode.window.showInformationMessage('Generating project...');
                    generateProject(message.components);
                    break;
            }
        }, undefined, context.subscriptions);
    }));
}
exports.activate = activate;
function getWebviewContent() {
    return `
		<!DOCTYPE html>
		<html lang="en">
		<head>
			<meta charset="UTF-8">
			<meta name="viewport" content="width=device-width, initial-scale=1.0">
			<title>Test Angular Components</title>
		</head>
		<body>
			<h1>Select Angular Components/Services</h1>
			<form id="component-form">
				<!-- Dynamically generate checkboxes for components/services -->
				<div>
					<label>
						<input type="checkbox" value="component1"> Component 1
					</label>
				</div>
				<div>
					<label>
						<input type="checkbox" value="component2"> Component 2
					</label>
				</div>
				<!-- Add more components as needed -->
			</form>
			<button onclick="generateProject()">Generate Project</button>
			<script>
				const vscode = acquireVsCodeApi();
				function generateProject() {
					const form = document.getElementById('component-form');
					const selectedComponents = Array.from(form.elements)
						.filter(input => input.checked)
						.map(input => input.value);
					vscode.postMessage({ command: 'generateProject', components: selectedComponents });
				}
			</script>
		</body>
		</html>
	`;
}
function generateProject(components) {
    const componentsStr = components.join(' ');
    const pythonProcess = (0, child_process_1.spawn)('python', ['src/backend/backend.py', ...components]);
    pythonProcess.stdout.on('data', (data) => {
        vscode.window.showInformationMessage(data.toString());
    });
    pythonProcess.stderr.on('data', (data) => {
        vscode.window.showErrorMessage(`Error: ${data.toString()}`);
    });
    pythonProcess.on('close', (code) => {
        if (code === 0) {
            vscode.window.showInformationMessage('Project generated successfully.');
        }
        else {
            vscode.window.showErrorMessage('Project generation failed.');
        }
    });
}
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map