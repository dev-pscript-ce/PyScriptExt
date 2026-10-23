const vscode = require("vscode");
const cp = require("child_process");
const path = require("path");

function registerSignatureProvider(context) {
  const pscriptRoot = path.join(context.extensionPath);

  const signatureProvider = vscode.languages.registerSignatureHelpProvider(
    "ps",

    {
      provideSignatureHelp(document, position, token) {
        // -----------------------------------------
        // Nếu request đã bị hủy thì không chạy Python
        // -----------------------------------------

        if (token?.isCancellationRequested) {
          return null;
        }

        // -----------------------------------------
        // Lấy nội dung hiện tại trong VS Code buffer
        // Không đọc file đã save trên disk
        // -----------------------------------------

        const source = document.getText();

        return new Promise((resolve) => {
          const process = cp.execFile(
            "python",

            [
              "-B",

              "-m",
              "pscript.analyzers.signature",

              // line
              String(position.line),

              // character
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

                console.error("[Pscript Signature]", stderr || error);

                resolve(null);
                return;
              }

              // ---------------------------------
              // Parse JSON
              // ---------------------------------

              let result;

              try {
                result = JSON.parse(stdout);
              } catch (error) {
                console.error("[Pscript Signature] " + "Invalid JSON:", stdout);

                resolve(null);
                return;
              }

              // ---------------------------------
              // Python trả lỗi / không có signature
              // ---------------------------------

              if (!result || result.error) {
                resolve(null);
                return;
              }

              // ---------------------------------
              // Tạo VS Code SignatureHelp
              // ---------------------------------

              resolve(createSignatureHelp(result));
            },
          );

          // ---------------------------------------
          // Gửi buffer hiện tại cho Python
          // ---------------------------------------

          process.stdin.write(source);

          process.stdin.end();

          // ---------------------------------------
          // Nếu VS Code hủy request trong lúc
          // Python đang chạy -> kill process
          // ---------------------------------------

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

    "(",
    ",",
  );

  context.subscriptions.push(signatureProvider);
}

// =========================================
// VS Code SignatureHelp
// =========================================

function createSignatureHelp(item) {
  const signatureHelp = new vscode.SignatureHelp();

  const signature = new vscode.SignatureInformation(
    item.signature || item.name,
    item.description || "",
  );

  signature.parameters = (item.parameters || []).map(
    (parameter) =>
      new vscode.ParameterInformation(
        parameter.name || "",
        parameter.description || "",
      ),
  );

  signatureHelp.signatures = [signature];

  signatureHelp.activeSignature = 0;

  signatureHelp.activeParameter = Number.isInteger(item.activeParameter)
    ? item.activeParameter
    : 0;

  return signatureHelp;
}

module.exports = {
  registerSignatureProvider,
};
