const vscode = require("vscode");
const {
  registerRunCommand,
  registerClosedTerminal,
} = require("./commands/run");

const { registerCompletionProvider } = require("./providers/completion");
const { registerHoverProvider } = require("./providers/hover");
const { registerDiagnosticProvider } = require("./providers/diagnoctics");
const { registerSignatureProvider } = require("./providers/signature");
const {
  registerSemanticTokensProvider,
} = require("./providers/semanticToken");

// ------------------------------------
// Activate
// ------------------------------------

function activate(context) {
  console.log("Pscript activate start");

  registerRunCommand(context);
  registerClosedTerminal(context);

  registerCompletionProvider(context);
  registerHoverProvider(context);
  registerSignatureProvider(context);
  registerDiagnosticProvider(context);
  registerSemanticTokensProvider(context);

  console.log("Pscript activate end");
}

// ------------------------------------
// Deactivate
// ------------------------------------

function deactivate() {
  terminal?.dispose();
  
}

module.exports = {
  activate,
  deactivate,
};
