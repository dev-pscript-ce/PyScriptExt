const vscode = require("vscode");
const cp = require("child_process");
const path = require("path");

function registerDiagnosticProvider(context) {
  const diagnosticCollection =
    vscode.languages.createDiagnosticCollection("Pscript");

  context.subscriptions.push(
    diagnosticCollection
  );

  const runningProcesses =
    new Map();

  const pscriptRoot = path.join(context.extensionPath)

  function analyzeDocument(document) {
    if (document.languageId !== "ps") {
      return;
    }

    // -----------------------------------------
    // Hủy Python process trước đó của document
    // -----------------------------------------

    const previousProcess =
      runningProcesses.get(
        document.uri.toString()
      );

    if (
      previousProcess &&
      !previousProcess.killed
    ) {
      previousProcess.kill();
    }

    // -----------------------------------------
    // Source hiện tại trong VS Code buffer
    // -----------------------------------------

    const source =
      document.getText();

    // -----------------------------------------
    // Chạy Python analyzer
    // -----------------------------------------

    const process =
      cp.execFile(
        "python",

        [
          "-B",

          "-m",
          "pscript.analyzers.diagnostic",
        ],

        {
          cwd: pscriptRoot,
          encoding: "utf8",
        },

        (
          error,
          stdout,
          stderr,
        ) => {

          // Process này không còn là process
          // mới nhất của document
          if (
            runningProcesses.get(
              document.uri.toString()
            ) !== process
          ) {
            return;
          }

          runningProcesses.delete(
            document.uri.toString()
          );

          // -----------------------------------
          // Process bị kill do user tiếp tục gõ
          // -----------------------------------

          if (
            error &&
            error.killed
          ) {
            return;
          }

          // -----------------------------------
          // Python error
          // -----------------------------------

          if (error) {

            console.error(
              "[Pscript Analyzer]",
              stderr || error,
            );

            return;
          }

          // -----------------------------------
          // Parse JSON
          // -----------------------------------

          let diagnostics;

          try {

            diagnostics =
              JSON.parse(stdout);

          } catch (error) {

            console.error(
              "[Pscript Analyzer] " +
              "Invalid JSON:",
              stdout,
            );

            return;
          }

          // -----------------------------------
          // Python trả lỗi
          // -----------------------------------

          if (
            !Array.isArray(
              diagnostics
            )
          ) {

            console.error(
              "[Pscript Analyzer]",
              diagnostics,
            );

            return;
          }

          const result = [];

          for (
            const item of diagnostics
          ) {

            const line =
              Math.max(
                0,
                item.line ?? 0,
              );

            const start =
              Math.max(
                0,
                item.start ?? 0,
              );

            const length =
              Math.max(
                1,
                item.length ?? 1,
              );

            const range =
              new vscode.Range(
                line,
                start,
                line,
                start + length,
              );

            let severity =
              vscode.DiagnosticSeverity.Error;

            if (
              item.severity ===
              "warning"
            ) {
              severity =
                vscode.DiagnosticSeverity.Warning;
            }

            const diagnostic =
              new vscode.Diagnostic(
                range,
                item.message || "",
                severity,
              );

            diagnostic.source =
              item.source ||
              "Pscript";

            if (
              item.code !== undefined
            ) {
              diagnostic.code =
                item.code;
            }

            result.push(
              diagnostic
            );
          }

          // -----------------------------------
          // Chỉ set kết quả cho document hiện tại
          // -----------------------------------

          diagnosticCollection.set(
            document.uri,
            result,
          );
        },
      );

    runningProcesses.set(
      document.uri.toString(),
      process,
    );

    // -----------------------------------------
    // Gửi buffer hiện tại cho Python
    // -----------------------------------------

    process.stdin.write(
      source
    );

    process.stdin.end();
  }

  // =========================================
  // File đang mở
  // =========================================

  if (
    vscode.window.activeTextEditor
  ) {
    analyzeDocument(
      vscode.window.activeTextEditor.document
    );
  }

  // =========================================
  // Open
  // =========================================

  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(
      analyzeDocument
    )
  );

  // =========================================
  // Save
  // =========================================

  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument(
      analyzeDocument
    )
  );

  // =========================================
  // Change
  // =========================================

  context.subscriptions.push(
    vscode.workspace.onDidChangeTextDocument(
      (event) => {
        analyzeDocument(
          event.document
        );
      }
    )
  );

  // =========================================
  // Dispose
  // =========================================

  context.subscriptions.push({
    dispose() {

      for (
        const process of
        runningProcesses.values()
      ) {

        if (
          !process.killed
        ) {
          process.kill();
        }
      }

      runningProcesses.clear();
    },
  });
}

module.exports = {
  registerDiagnosticProvider,
};
