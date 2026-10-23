const vscode = require("vscode");
const path = require("path");

let terminal;

// ---------- Register Run Command ----------

function registerRunCommand(context) {
  const runCommand = vscode.commands.registerCommand("ps.runFile", () => {
    const editor = vscode.window.activeTextEditor;

    // Check editor
    if (!editor) {
      vscode.window.showErrorMessage("No active Pscript file (.ps)");
      return;
    }

    // Check language
    if (editor.document.languageId !== "ps") {
      vscode.window.showErrorMessage("This is not a Pscript file (.ps)");
      return;
    }

    // Workspace
    const workspaceFolder = vscode.workspace.getWorkspaceFolder(
      editor.document.uri,
    );
    const workspacePath = workspaceFolder
      ? workspaceFolder.uri.fsPath
      : path.dirname(editor.document.fileName);

    const interpreter = path.join(
      context.extensionPath,
      "main_pscript.py"
    );

    // const interpreter = "pscript";
    const filePath = editor.document.fileName;

    const command =
      `python "${interpreter}" ` + `"${filePath}" ` + `"${workspacePath}"`;

    // Terminal
    const term = getTerminal();
    term.show();

    console.log("Pscript command:", command);

    term.sendText(command);
  });
  context.subscriptions.push(runCommand);
}

// --------- Helpers ---------

// Get terminal
function getTerminal() {
  if (!terminal || terminal.exitStatus) {
    terminal = vscode.window.createTerminal("Pscript");
  }
  return terminal;
}
function registerClosedTerminal(context) {
  const closedTerminal = vscode.window.onDidCloseTerminal((closedTerm) => {
    if (closedTerm === terminal) {
      terminal = undefined;
    }
  });
  context.subscriptions.push(closedTerminal);
}

// ---------- Export ----------

module.exports = { registerRunCommand, registerClosedTerminal };
