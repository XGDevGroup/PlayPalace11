/**
 * Markdown viewer dialog for rendering secure HTML from markdown content.
 */
const MARKDOWN_SANITIZE_CONFIG = {
  USE_PROFILES: { html: true },
  FORBID_TAGS: ["img", "svg", "math", "iframe", "object", "embed", "form", "style"],
  FORBID_ATTR: ["style", "srcset"],
  ALLOWED_URI_REGEXP: /^(https?|mailto):/i,
};

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

export function renderMarkdownHtml(rawMarkdown, markedImpl = window.marked, purifier = window.DOMPurify) {
  if (markedImpl && purifier) {
    const rawHtml = markedImpl.parse(String(rawMarkdown || ""), {
      breaks: true,
      gfm: true,
    });
    return purifier.sanitize(rawHtml, MARKDOWN_SANITIZE_CONFIG);
  }
  return `<p>Markdown renderer failed to load.</p><pre>${escapeHtml(rawMarkdown || "")}</pre>`;
}

export function createMarkdownViewer({ dialogEl, onSubmit }) {
  let currentDialogId = null;

  const container = document.createElement("div");
  container.className = "markdown-viewer-container";

  // Prompt/Title
  const promptEl = document.createElement("h2");
  promptEl.id = "markdown-viewer-prompt";
  promptEl.style.margin = "0 0 16px 0";
  container.appendChild(promptEl);

  // Markdown content area
  const contentEl = document.createElement("div");
  contentEl.id = "markdown-viewer-content";
  contentEl.className = "markdown-body";
  contentEl.style.maxHeight = "60vh";
  contentEl.style.overflowY = "auto";
  contentEl.style.marginBottom = "16px";
  // The content itself needs to be focusable or contain a focusable element
  // for a11y, let's make it tabindex="0"
  contentEl.tabIndex = 0;
  contentEl.setAttribute("role", "document");
  container.appendChild(contentEl);

  // Close button
  const btnRow = document.createElement("div");
  btnRow.className = "row";
  btnRow.style.justifyContent = "flex-end";

  const closeBtn = document.createElement("button");
  closeBtn.type = "button";
  closeBtn.textContent = "Close";
  
  btnRow.appendChild(closeBtn);
  container.appendChild(btnRow);
  dialogEl.appendChild(container);

  function closeDialog() {
    if (dialogEl.open) {
      dialogEl.close();
    }
  }

  function doClose() {
    if (!currentDialogId) return;
    
    // Submit empty string because server sent us a request_input.
    // We send back an empty string to allow it to navigate back/close.
    onSubmit({
      input_id: currentDialogId,
      text: "",
    });
    
    currentDialogId = null;
    closeDialog();
  }

  closeBtn.addEventListener("click", doClose);

  dialogEl.addEventListener("cancel", (event) => {
    event.preventDefault();
    doClose();
  });

  return {
    show: (packet) => {
      currentDialogId = packet.input_id || "";
      promptEl.textContent = packet.prompt || "Document";
      
      const rawMarkdown = packet.default_value || "";
      
      const htmlOutput = renderMarkdownHtml(rawMarkdown);
      
      contentEl.innerHTML = htmlOutput;
      
      // Attempt to ensure all links open in a new tab
      const links = contentEl.querySelectorAll("a");
      links.forEach(link => {
        link.setAttribute("target", "_blank");
        link.setAttribute("rel", "noopener noreferrer");
      });

      if (!dialogEl.open) {
        dialogEl.showModal();
      }
      
      requestAnimationFrame(() => {
        contentEl.focus(); // Focus the scrollable content area first for screen readers
      });
    },
    closeDialog
  };
}
