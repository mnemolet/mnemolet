document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    const messagesEl = document.getElementById("messages");
    const textarea = form.querySelector("textarea");

    textarea.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey && textarea.value.trim()) {
        e.preventDefault();      // stop newline
        form.requestSubmit();   // same as clicking "Send"
      }
    });

  if (!form || !messagesEl) return

  form.addEventListener("submit", async (e) => {
    e.preventDefault()
    const textarea = form.querySelector("textarea")
    const content = textarea.value.trim()
    if (!content) return
    textarea.value = ""

    // show user message immediately
    appendMessage("user", content)

    // prepare payload
    const payload = { message: content }
    if (form.dataset.sessionId) payload.session_id = form.dataset.sessionId
    console.log(payload.session_id);

    const res = await fetch("/api/chat/sessions/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })

    if (!res.ok) {
      const text = await res.text()
      console.error("API error:", text)
      return
    }

    // streaming assistant reply
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ""
    let assistantSpan = null

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split("\n")
      buffer = lines.pop() // incomplete line

      for (const line of lines) {
        if (!line.trim()) continue
        const data = JSON.parse(line)
        if (data.type === "chunk") {
          // create the assistant span once
          if (!assistantSpan) {
            assistantSpan = appendMessage("assistant", "")
          }
          // append chunk to the existing span
          assistantSpan.textContent += data.data
          // scroll to bottom
          messagesEl.scrollTop = messagesEl.scrollHeight
        }

        // store session id for next messages
        if (data.type === "done" && !form.dataset.sessionId) {
            form.dataset.sessionId = data.session_id;

            // update session title
            const title = document.getElementById("session-title");
            if (title) {
                title.textContent = `Session ${data.session_id}`;
            }

            // add to sidebar
            const list = document.getElementById("sessions-list");
            if (list) {
              const li = createSessionItem(data.session_id);
              list.prepend(li);
            }
        }
      }
    }

  })

    function createSessionItem(sessionId) {
        const li = document.createElement("li");
        li.className =
        "flex items-center justify-between px-4 py-2 hover:bg-gray-100 relative";
        li.dataset.sessionId = sessionId;

        // link
        const a = document.createElement("a");
        a.href = `/chat/${sessionId}`;
        a.textContent = sessionId;
        a.className = "session-title block px-4 py-2 hover:bg-gray-100";

        // menu button
        const button = document.createElement("button");
        button.className =
        "text-gray-500 hover:text-gray-800 focus:outline-none menu-toggle";
        button.innerHTML = "&#x22EE;";

        // menu
        const menu = document.createElement("div");
        menu.className =
        "absolute right-4 top-full mt-1 hidden bg-white border rounded shadow-md w-32 z-10 menu";

        menu.innerHTML = `
        <ul>
          <li data-action="export" class="px-3 py-2 hover:bg-gray-200 cursor-pointer">Export</li>
          <li data-action="rename" class="px-3 py-2 hover:bg-gray-200 cursor-pointer">Rename</li>
          <li data-action="delete" class="px-3 py-2 hover:bg-gray-200 cursor-pointer">Delete</li>
        </ul>
        `;

        li.appendChild(a);
        li.appendChild(button);
        li.appendChild(menu);

        return li;
    }

    // appendMessage helper returns the span for incremental updates
    function appendMessage(role, content) {
        const wrapper = document.createElement("div")
        wrapper.className = role === "user" ? "text-right" : "text-left"

        const span = document.createElement("span")
        span.className = `
          inline-block px-3 py-2 rounded
          ${role === "user" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-800"}
        `
        span.textContent = content

        wrapper.appendChild(span)
        messagesEl.appendChild(wrapper)

        // scroll to bottom
        messagesEl.scrollTop = messagesEl.scrollHeight

        return span
    }

    // === Menu toggle and outside click handling ===
    document.addEventListener("click", (e) => {
        const menuBtn = e.target.closest(".menu-toggle");
        const menu = e.target.closest(".menu");
        const menuItem = e.target.closest(".menu [data-action]");

        // === menu btn click
        if (menuBtn) {
            e.preventDefault();
            e.stopPropagation();
        
            const currentMenu = menuBtn.nextElementSibling;
            const isOpen = !currentMenu.classList.contains("hidden");

            document.querySelectorAll(".menu").forEach(m => 
                m.classList.add("hidden")
            );

            if (!isOpen) currentMenu.classList.remove("hidden");
                return;
        }

        // === menu item click
        if (menuItem) {
            e.stopPropagation();

            const action = menuItem.dataset.action;
            const sessionLi = menuItem.closest("li[data-session-id]");
            const sessionId = sessionLi?.dataset.sessionId;

            if (action === "rename") {
                e.preventDefault();
                e.stopPropagation();
                startRenameSession(sessionLi, sessionId);
                return;
            }
            
            if (action === "delete") {
                e.preventDefault();
                e.stopPropagation();
                deleteSession(sessionId);
                return;
            }
            
            if (action === "export") {
                e.preventDefault();
                e.stopPropagation();
                exportSession(sessionId);
                return;
            }

            // ==> For Debug only
            console.log("Menu action: ", action);
            console.log("Session ID: ", sessionId);
            // <==

            // close menu after click
            document.querySelectorAll(".menu").forEach( m => 
                m.classList.add("hidden")
            );
        }

        // clicked outside
        document.querySelectorAll(".menu").forEach(m => 
            m.classList.add("hidden")
        );
    });

    function startRenameSession(li, sessionId, event) {
        event?.preventDefault();
        event?.stopPropagation();

        // normalize target
        li = li.closest("li");
        if (!li) 
            return;

        const link = li.querySelector(".session-title");
        if (!link || li.querySelector("input")) 
            return;

        const oldTitle = link.textContent.trim();
        const linkClass = link.className;

        const input = document.createElement("input");
        input.type = "text";
        input.value = oldTitle;
        input.className = linkClass;
        input.style.width = "100%";
        input.style.minWidth = "0";
        input.style.flex = "1";

        link.replaceWith(input);
        input.focus();
        input.select();

        const finish = async (save) => {
            const newTitle = input.value.trim();

            const finalTitle = save && newTitle ? newTitle : oldTitle;

            const newLink = document.createElement("a");
            newLink.href = `/chat/${sessionId}`;
            newLink.className = linkClass;
            newLink.textContent = finalTitle;

            input.replaceWith(newLink);

            if (save && newTitle && newTitle !== oldTitle) {
                try {
                    await fetch(`/api/chat/sessions/${sessionId}`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ title: newTitle })
                })
                } catch (err) {
                    console.error("Rename failed", err);
                    newLink.textContent = oldTitle; // rollback on error
                }
            }
        }

        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") finish(true)
            if (e.key === "Escape") finish(false)
        })

        setTimeout(() => {
            input.addEventListener("blur", () => finish(true))
        }, 0)
    }


    async function deleteSession(sessionId, event) {
        event?.preventDefault()
        event?.stopPropagation()

        const li = document.querySelector(`li[data-session-id="${sessionId}"]`)
        const titleEl = li?.querySelector(".session-title")
        const sessionTitle = titleEl?.textContent?.trim() || "Unnamed session"

        const confirmed = window.confirm(
        `Are you sure you want to delete the session:\n\n` +
        `"${sessionTitle}" (ID: ${sessionId})\n\n` +
        `This action cannot be undone.`)

        if (!confirmed) return

        try {
        const resp = await fetch(`/api/chat/sessions/${sessionId}`, {
            method: "DELETE",
            headers: {
            "Accept": "application/json",
            },
        })

            if (!resp.ok) {
                if (resp.status === 404) {
                    alert("Session not found.")
                } else {
                    throw new Error(`Failed with status ${resp.status}`)
                }
                return
            }

            // Remove session from UI
            const li = document.querySelector(`li[data-session-id="${sessionId}"]`)
            li?.remove()

            // Redirect if user deleted currently open session
            if (window.location.pathname === `/chat/${sessionId}`) {
                window.location.href = "/chat"
            }

        } catch (err) {
            console.error("Delete session failed:", err)
            alert("Failed to delete session. Please try again.")
        }
    }

    function exportSession(sessionId) {
        // Remove existing dialog if any
        const existing = document.getElementById("export-dialog");
        if (existing) existing.remove();

        // Overlay
        const overlay = document.createElement("div");
        overlay.id = "export-dialog";
        overlay.className =
            "fixed inset-0 bg-black/50 flex items-center justify-center z-50";

        // Dialog
        const dialog = document.createElement("div");
        dialog.className =
            "bg-white rounded-lg shadow-lg w-96 p-6";

        dialog.innerHTML = `
            <h2 class="text-lg font-semibold mb-4">Export chat session</h2>

            <div class="space-y-2 mb-4">
                <label class="flex items-center gap-2">
                    <input type="radio" name="export-format" value="text" checked>
                    Plain text
                </label>
                <label class="flex items-center gap-2">
                    <input type="radio" name="export-format" value="json">
                    JSON
                </label>
            </div>

            <div class="flex justify-end gap-3">
                <button id="export-cancel"
                    class="px-4 py-2 border rounded hover:bg-gray-100">
                    Cancel
                </button>
                <button id="export-confirm"
                    class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                    Export
                </button>
            </div>
        `;

        overlay.appendChild(dialog);
        document.body.appendChild(overlay);

        // Cancel
        dialog.querySelector("#export-cancel").onclick = () => {
            overlay.remove();
        };

        // Export
        dialog.querySelector("#export-confirm").onclick = () => {
            const format = dialog.querySelector(
                'input[name="export-format"]:checked'
            ).value;

            const url = `/api/chat/sessions/${sessionId}?format=${format}`;

            // Create invisible download link
            const a = document.createElement("a");
            a.href = url;
            a.download = `chat-session-${sessionId}.${format === "json" ? "json" : "txt"}`;
            document.body.appendChild(a);
            a.click();
            a.remove();

            overlay.remove();
        };
    }

})
