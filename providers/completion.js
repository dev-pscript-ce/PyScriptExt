const vscode = require("vscode");
const cp = require("child_process");
const path = require("path");

function registerCompletionProvider(context) {
  const pscriptRoot = path.join(context.extensionPath);

  const provider = vscode.languages.registerCompletionItemProvider(
    "ps",

    {
      provideCompletionItems(document, position, token) {
        // Request đã bị hủy trước khi chạy Python
        if (token?.isCancellationRequested) {
          return null;
        }

        // Lấy buffer hiện tại của VS Code
        // Không đọc file trên disk
        const source = document.getText();

        const lineText = document.lineAt(position.line).text;

        const before = lineText.slice(0, position.character);

        const charBefore = before.slice(-1);

        if (charBefore === " ") {
          if (!isImportSpaceContext(before)) {
            return undefined;
          }
        }

        if (charBefore === ".") {
          if (!isMemberTriggerContext(before)) {
            return undefined;
          }
        }
        if (charBefore === ",") {
          if (!isImportCommaContext(before)) {
            return undefined;
          }
        }

        return new Promise((resolve) => {
          const process = cp.execFile(
            "python",

            [
              "-B",

              "-m",
              "pscript.analyzers.completion",

              String(position.line),

              String(position.character),
            ],

            {
              cwd: pscriptRoot,
              encoding: "utf8",
            },

            (error, stdout, stderr) => {
              // Request đã bị hủy
              if (token?.isCancellationRequested) {
                resolve(null);
                return;
              }

              if (error) {
                if (error.killed) {
                  resolve(null);
                  return;
                }

                console.error("[Pscript Completion]", stderr || error);

                resolve([]);

                return;
              }

              let items;

              try {
                items = JSON.parse(stdout);
              } catch (error) {
                console.error(
                  "[Pscript Completion] " + "Invalid JSON:",
                  stdout,
                );

                resolve([]);

                return;
              }

              // -------------------------
              // Python trả lỗi
              // -------------------------

              if (!Array.isArray(items)) {
                console.error("[Pscript Completion]", items);

                resolve([]);

                return;
              }
              // console.log(
              //   "[JP3][Completion] RETURN",
              //   items.map((x) => x.label),
              // );

              resolve(items.map(createCompletionItem));
            },
          );

          // Gửi buffer hiện tại cho Python
          process.stdin.write(source);

          process.stdin.end();

          if (token) {
            const disposable = token.onCancellationRequested(() => {
              if (!process.killed) {
                process.kill();
              }
            });
            process.on("close", () => {
              disposable.dispose();
            });
          }
        });
      },
    },
    ".",
    " ",
    ",",
  );

  context.subscriptions.push(provider);
}

// =========================================
// Helper_isImportCommaContext:
// =========================================

function isImportCommaContext(before) {
  // =========================================
  // import cv2,
  // import cv2, ocr,
  // import cv2, ocr, std,
  // =========================================

  if (/^\s*import\s+\w+(?:\s*,\s*\w+)*\s*,\s*$/.test(before)) {
    return true;
  }

  // =========================================
  // from cv2 import FIND_CLICK,
  // from cv2 import FIND_CLICK, FIND_TEXT,
  // =========================================

  if (/^\s*from\s+\w+\s+import\s+\w+(?:\s*,\s*\w+)*\s*,\s*$/.test(before)) {
    return true;
  }

  return false;
}

// =========================================
// Helper_isImportSpaceContext:
// =========================================

function isImportSpaceContext(before) {
  // =========================================
  // import
  //
  // import |
  // =========================================

  if (/^\s*import\s*$/.test(before)) {
    return true;
  }

  // =========================================
  // from
  //
  // from |
  // =========================================

  if (/^\s*from\s*$/.test(before)) {
    return true;
  }

  // =========================================
  // from ocr
  //
  // from ocr |
  // =========================================

  if (/^\s*from\s+\w+\s*$/.test(before)) {
    return true;
  }

  // =========================================
  // from ocr import
  //
  // from ocr import |
  // =========================================

  if (/^\s*from\s+\w+\s+import\s*$/.test(before)) {
    return true;
  }

  return false;
}

// =========================================
// Helper_isMemberTriggerContext:
// =========================================

function isMemberTriggerContext(before) {
  if (/^\s*import\b/.test(before)) {
    return false;
  }

  return /(?:[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\.$/.test(before);
}

// =========================================
// Create CompletionItem
// =========================================

function createCompletionItem(item) {
  let kind = vscode.CompletionItemKind.Text;

  switch (item.kind) {
    case "keyword":
      kind = vscode.CompletionItemKind.Keyword;
      break;

    case "constant":
      kind = vscode.CompletionItemKind.Constant;
      break;

    case "function":
      kind = vscode.CompletionItemKind.Function;
      break;

    case "method":
      kind = vscode.CompletionItemKind.Method;
      break;

    case "variable":
      kind = vscode.CompletionItemKind.Variable;
      break;

    case "module":
      kind = vscode.CompletionItemKind.Module;
      break;
  }

  const completion = new vscode.CompletionItem(item.label, kind);

  // =================================
  // Filtering
  // =================================

  // completion.filterText = item.filterText || item.label;

  // =================================
  // Sorting
  // =================================

  completion.sortText = item.sortText || item.label;

  // =================================
  // Detail
  // =================================

  completion.detail = item.detail || "";

  // =================================
  // Documentation
  // =================================

  if (item.documentation) {
    completion.documentation = new vscode.MarkdownString(item.documentation);
  }

  // =================================
  // Insert
  // =================================

  if (item.insertText) {
    if (item.insertTextFormat === 2) {
      completion.insertText = new vscode.SnippetString(item.insertText);
    } else {
      completion.insertText = item.insertText;
    }
  }

  return completion;
}

module.exports = {
  registerCompletionProvider,
};
