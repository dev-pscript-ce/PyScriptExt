const vscode = require("vscode");
const cp = require("child_process");
const path = require("path");

function registerSemanticTokensProvider(context) {
  // =========================================================
  // Pscript root
  // =========================================================

  const pscriptRoot = path.join(context.extensionPath);

  // =========================================================
  // Semantic token types
  // =========================================================

  const tokenTypes = ["class", "function", "method", "variable", "parameter"];

  const legend = new vscode.SemanticTokensLegend(tokenTypes);

  // =========================================================
  // Cache
  //
  // uri -> SemanticTokens
  //
  // Chỉ lưu kết quả semantic token hợp lệ cuối cùng.
  // =========================================================

  const semanticCache = new Map();

  // =========================================================
  // Version mới nhất của từng document
  //
  // uri -> document.version
  //
  // Dùng để tránh process cũ trả kết quả sau process mới.
  // =========================================================

  const semanticVersion = new Map();

  // =========================================================
  // Process đang chạy
  //
  // uri -> ChildProcess
  //
  // Khi document thay đổi, process cũ sẽ bị kill.
  // =========================================================

  const runningProcesses = new Map();

  // =========================================================
  // Event yêu cầu VS Code refresh semantic tokens
  // =========================================================

  const semanticTokensChanged = new vscode.EventEmitter();

  // =========================================================
  // Empty result
  // =========================================================

  function emptyTokens() {
    return new vscode.SemanticTokensBuilder(legend).build();
  }

  // =========================================================
  // Cache fallback
  // =========================================================

  function getCachedTokens(uri) {
    return semanticCache.get(uri) || emptyTokens();
  }

  // =========================================================
  // Resolve helper
  // =========================================================

  function resolveCached(resolve, uri) {
    resolve(getCachedTokens(uri));
  }

  // =========================================================
  // Provider
  // =========================================================

  const provider = {
    onDidChangeSemanticTokens: semanticTokensChanged.event,

    // =======================================================
    // Provide semantic tokens
    // =======================================================

    provideDocumentSemanticTokens(document, cancellationToken) {
      if (document.languageId !== "ps") {
        return null;
      }

      const uri = document.uri.toString();

      const version = document.version;

      // =====================================================
      // Document version mới nhất
      // =====================================================

      semanticVersion.set(uri, version);

      // =====================================================
      // Kill process cũ của cùng document
      //
      // Điều này rất quan trọng khi user gõ liên tục.
      // =====================================================

      const previousProcess = runningProcesses.get(uri);

      if (previousProcess) {
        try {
          previousProcess.kill();
        } catch {}
      }

      // =====================================================
      // Promise
      // =====================================================

      return new Promise((resolve) => {
        let settled = false;

        // ===================================================
        // Resolve một lần duy nhất
        // ===================================================

        function finish(result) {
          if (settled) {
            return;
          }

          settled = true;

          resolve(result);
        }

        // ===================================================
        // Current version check
        // ===================================================

        function isCurrentVersion() {
          return semanticVersion.get(uri) === version;
        }

        // ===================================================
        // Start Python
        // ===================================================

        const process = cp.execFile(
          "python",

          ["-B", "-m", "pscript.analyzers.semantic_tokens"],

          {
            cwd: pscriptRoot,
            encoding: "utf8",
          },

          (error, stdout, stderr) => {
            // ===========================================
            // Process không còn là process hiện tại
            // ===========================================

            if (runningProcesses.get(uri) === process) {
              runningProcesses.delete(uri);
            }

            // ===========================================
            // stderr
            // ===========================================

            if (stderr) {
              console.log("[Pscript SemanticTokens][stderr]", stderr.trim());
            }

            // ===========================================
            // Process bị kill / cancelled
            // ===========================================

            if (
              error &&
              (error.killed ||
                error.code === "ERR_CHILD_PROCESS_STDIO_MAXBUFFER")
            ) {
              // Không ghi đè cache.
              // Nếu request này không còn hợp lệ,
              // trả cache hiện tại.

              finish(getCachedTokens(uri));

              return;
            }

            // ===========================================
            // Python error
            // ===========================================

            if (error) {
              console.error(
                "[Pscript SemanticTokens] Python error:",
                error.message,
              );

              finish(getCachedTokens(uri));

              return;
            }

            // ===========================================
            // JSON parse
            // ===========================================

            let data;

            try {
              data = JSON.parse(stdout);
            } catch (parseError) {
              console.error("[Pscript SemanticTokens] Invalid JSON:");

              console.error(stdout);

              finish(getCachedTokens(uri));

              return;
            }

            // ===========================================
            // Python returned error object
            //
            // Ví dụ:
            //
            // {"error":"Expected INDENT..."}
            //
            // Khi source đang incomplete,
            // giữ token cũ.
            // ===========================================

            if (!Array.isArray(data)) {
              console.log(
                "[Pscript SemanticTokens]",
                "Python returned non-array:",
                data,
              );

              finish(getCachedTokens(uri));

              return;
            }

            // ===========================================
            // IMPORTANT
            //
            // Process này có thể đã cũ.
            //
            // Không được để kết quả cũ ghi đè
            // semantic cache của document mới.
            // ===========================================

            if (!isCurrentVersion()) {
              // console.log(
              //   "[Pscript SemanticTokens]",
              //   "STALE RESULT",
              //   "version =",
              //   version,
              //   "current =",
              //   semanticVersion.get(uri)
              // );

              finish(getCachedTokens(uri));

              return;
            }

            // ===========================================
            // Debug
            // ===========================================

            // console.log(
            //   "[Pscript SemanticTokens]",
            //   "version =",
            //   version,
            //   "tokens =",
            //   data,
            // );

            // ===========================================
            // Build SemanticTokens
            // ===========================================

            const builder = new vscode.SemanticTokensBuilder(legend);

            for (const item of data) {
              if (!item || typeof item !== "object") {
                continue;
              }

              const tokenType = item.type;

              const tokenIndex = tokenTypes.indexOf(tokenType);

              if (tokenIndex < 0) {
                continue;
              }

              // =========================================
              // Python semantic token dùng 1-based
              //
              // VS Code dùng 0-based
              // =========================================

              const line = Math.max(0, (item.line ?? 1) - 1);

              const character = Math.max(0, (item.column ?? 1) - 1);

              const length = Math.max(1, item.length ?? 1);

              builder.push(line, character, length, tokenIndex, 0);
            }

            // ===========================================
            // Build result
            // ===========================================

            const result = builder.build();

            // ===========================================
            // Check version lần cuối
            //
            // Trong lúc build có thể document đã đổi.
            // ===========================================

            if (!isCurrentVersion()) {
              // console.log(
              //   "[Pscript SemanticTokens]",
              //   "STALE AFTER BUILD",
              //   "version =",
              //   version,
              //   "current =",
              //   semanticVersion.get(uri),
              // );

              finish(getCachedTokens(uri));

              return;
            }

            // ===========================================
            // Cache kết quả hợp lệ
            // ===========================================

            semanticCache.set(uri, result);

            // ===========================================
            // Trả kết quả
            // ===========================================

            finish(result);
          },
        );

        // ===================================================
        // Ghi nhận process hiện tại
        // ===================================================

        runningProcesses.set(uri, process);

        // ===================================================
        // Gửi source vào stdin
        // ===================================================

        try {
          process.stdin.write(document.getText());

          process.stdin.end();
        } catch (error) {
          console.error("[Pscript SemanticTokens] stdin error:", error);

          try {
            process.kill();
          } catch {}

          finish(getCachedTokens(uri));
        }

        // ===================================================
        // VS Code cancellation
        // ===================================================

        cancellationToken.onCancellationRequested(() => {
          // Chỉ kill nếu đây vẫn là process
          // đang chạy của document.

          if (runningProcesses.get(uri) === process) {
            runningProcesses.delete(uri);

            try {
              process.kill();
            } catch {}
          }

          finish(getCachedTokens(uri));
        });
      });
    },
  };

  // =========================================================
  // Register provider
  // =========================================================

  context.subscriptions.push(
    vscode.languages.registerDocumentSemanticTokensProvider(
      {
        language: "ps",
      },
      provider,
      legend,
    ),
  );

  // =========================================================
  // Document changed
  // =========================================================

  context.subscriptions.push(
    vscode.workspace.onDidChangeTextDocument((event) => {
      const document = event.document;

      if (document.languageId !== "ps") {
        return;
      }

      const uri = document.uri.toString();

      const version = document.version;

      // ===============================================
      // Cập nhật version ngay lập tức
      //
      // Quan trọng:
      // process cũ sau đó sẽ trở thành STALE.
      // ===============================================

      semanticVersion.set(uri, version);

      // ===============================================
      // Kill process cũ
      // ===============================================

      const process = runningProcesses.get(uri);

      if (process) {
        try {
          process.kill();
        } catch {}

        runningProcesses.delete(uri);
      }

      // ===============================================
      // Yêu cầu VS Code lấy semantic tokens mới
      //
      // DocumentSemanticTokensProvider event
      // không truyền document/uri.
      //
      // fire() là đúng.
      // ===============================================

      semanticTokensChanged.fire();
    }),
  );

  // =========================================================
  // Document closed
  // =========================================================

  context.subscriptions.push(
    vscode.workspace.onDidCloseTextDocument((document) => {
      if (document.languageId !== "ps") {
        return;
      }

      const uri = document.uri.toString();

      // ===============================================
      // Kill process nếu còn chạy
      // ===============================================

      const process = runningProcesses.get(uri);

      if (process) {
        try {
          process.kill();
        } catch {}
      }

      // ===============================================
      // Xóa toàn bộ state
      // ===============================================

      runningProcesses.delete(uri);

      semanticCache.delete(uri);

      semanticVersion.delete(uri);
    }),
  );

  // =========================================================
  // Cleanup khi extension deactivate
  // =========================================================

  context.subscriptions.push({
    dispose() {
      for (const process of runningProcesses.values()) {
        try {
          process.kill();
        } catch {}
      }

      runningProcesses.clear();
      semanticCache.clear();
      semanticVersion.clear();

      semanticTokensChanged.dispose();
    },
  });
}

module.exports = {
  registerSemanticTokensProvider,
};
