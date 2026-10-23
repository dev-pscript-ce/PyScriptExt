const vscode = require("vscode");
const cp = require("child_process");
const path = require("path");

function registerHoverProvider(context) {
  const pscriptRoot = path.join(context.extensionPath);

  const provider = vscode.languages.registerHoverProvider(
    "ps",

    {
      provideHover(document, position, token) {
        // =========================================
        // Request đã bị hủy trước khi chạy Python
        // =========================================

        if (token?.isCancellationRequested) {
          return null;
        }

        // =========================================
        // Lấy buffer hiện tại của VS Code
        // Không đọc file trên disk
        // =========================================

        const source = document.getText();

        return new Promise((resolve) => {
          // =======================================
          // Chạy Python
          // =======================================

          const process = cp.execFile(
            "python",

            [
              "-B",

              "-m",
              "pscript.analyzers.hover",

              String(position.line),

              String(position.character),
            ],

            {
              cwd: pscriptRoot,
              encoding: "utf8",
            },

            (error, stdout, stderr) => {
              // ---------------------------------
              // Request đã bị hủy
              // ---------------------------------

              if (token?.isCancellationRequested) {
                resolve(null);
                return;
              }

              // ---------------------------------
              // Python error
              // ---------------------------------

              if (error) {
                // Process bị kill do cancellation
                if (error.killed) {
                  resolve(null);
                  return;
                }

                console.error("[Pscript Hover]", stderr || error);

                resolve(null);
                return;
              }

              // ---------------------------------
              // Parse JSON
              // ---------------------------------

              let result;

              try {
                result = JSON.parse(stdout);
                console.log("[Pscript Hover Result]", result);
              } catch (error) {
                console.error("[Pscript Hover] " + "Invalid JSON:", stdout);

                resolve(null);
                return;
              }

              // ---------------------------------
              // Python trả lỗi / không có hover
              // ---------------------------------

              if (!result || result.error) {
                resolve(null);
                return;
              }

              // ---------------------------------
              // Tạo Hover
              // ---------------------------------
              console.log(
                "[Pscript Hover Create]",
                result.name,
                result.signature,
                result.type,
              );

              resolve(createHover(result));
            },
          );

          // =======================================
          // Gửi buffer hiện tại cho Python
          // =======================================

          process.stdin.write(source);

          process.stdin.end();

          // =======================================
          // Cancellation
          // =======================================

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
  );

  context.subscriptions.push(provider);
}

// =========================================
// Create VS Code Hover
// =========================================

function createHover(item) {
  console.log("[Pscript createHover]", item);
  const markdown = new vscode.MarkdownString();

  markdown.appendCodeblock(item.signature || item.name, "ps");

  if (item.description) {
    markdown.appendMarkdown(`\n\n${item.description}`);
  }

  if (item.type) {
    markdown.appendMarkdown(`\n\n**${item.type}**`);
  }

  return new vscode.Hover(markdown);
}

module.exports = {
  registerHoverProvider,
};
