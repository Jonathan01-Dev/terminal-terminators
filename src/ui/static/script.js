document.addEventListener("DOMContentLoaded", () => {
    
    // Elements
    const btnStart = document.getElementById("btn-start");
    const nodePortInput = document.getElementById("node-port");
    const nodeFolderInput = document.getElementById("node-folder");
    const msgStart = document.getElementById("msg-start");
    
    const dotStatus = document.getElementById("global-status-dot");
    const textStatus = document.getElementById("global-status-text");
    const textNodeId = document.getElementById("local-node-id");
    
    const btnRefreshPeers = document.getElementById("btn-refresh-peers");
    const peersTbody = document.getElementById("peers-table-body");
    const msgTargetSelect = document.getElementById("msg-target");
    
    const btnSendMsg = document.getElementById("btn-send-msg");
    const msgContent = document.getElementById("msg-content");
    const msgResult = document.getElementById("msg-result");
    
    const btnSendFile = document.getElementById("btn-send-file");
    const filePathInput = document.getElementById("file-path");
    const fileResult = document.getElementById("file-result");
    
    let isRunning = false;
    let peerInterval = null;

    // --- Helpers ---
    function showMessage(element, text, isError=false) {
        element.textContent = text;
        element.className = `status-msg ${isError ? 'status-error' : 'status-success'}`;
        setTimeout(() => element.textContent = "", 5000);
    }

    // --- 1. Start Node ---
    btnStart.addEventListener("click", async () => {
        if(isRunning) return;
        
        const port = parseInt(nodePortInput.value) || 5060;
        const folder = nodeFolderInput.value || "shared_files";
        
        btnStart.textContent = "LAUNCHING...";
        
        try {
            const res = await fetch("/api/start", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({port, folder})
            });
            const data = await res.json();
            
            if(data.status === "started" || data.status === "already_running") {
                isRunning = true;
                btnStart.textContent = "NODE ACTIVE";
                btnStart.classList.replace("btn-primary", "btn-secondary");
                btnStart.disabled = true;
                nodePortInput.disabled = true;
                nodeFolderInput.disabled = true;
                
                checkStatus();
                // Start polling peers every 3 seconds
                peerInterval = setInterval(fetchPeers, 3000);
            }
        } catch (err) {
            showMessage(msgStart, "Failed to reach backend API.", true);
            btnStart.textContent = "LAUNCH P2P NODE";
        }
    });

    // --- 2. Check Global Status ---
    async function checkStatus() {
        try {
            const res = await fetch("/api/status");
            const data = await res.json();
            
            if (data.status === "online") {
                dotStatus.classList.add("online");
                textStatus.textContent = "ONLINE & SECURE";
                textStatus.style.color = "var(--success)";
                textNodeId.textContent = data.node_id;
            }
        } catch(e) {}
    }

    // --- 3. Refresh Peers Table ---
    async function fetchPeers() {
        try {
            const res = await fetch("/api/peers");
            const peers = await res.json();
            
            updatePeersTable(peers);
            updateSelectDropdown(peers);
        } catch(e) {}
    }

    function updatePeersTable(peers) {
        if (!peers || peers.length === 0) {
            peersTbody.innerHTML = `<tr><td colspan="3" class="text-center empty-state">No peers discovered yet</td></tr>`;
            return;
        }

        peersTbody.innerHTML = "";
        peers.forEach(p => {
            const tr = document.createElement("tr");
            
            const tdId = document.createElement("td");
            tdId.textContent = p.ip_port;
            
            const tdStatus = document.createElement("td");
            tdStatus.innerHTML = p.status === "Online" 
                ? `<span style="color:var(--success)">● Online</span>` 
                : `<span style="color:var(--danger)">○ Offline</span>`;
                
            const tdTrust = document.createElement("td");
            if (p.trusted) {
                tdTrust.innerHTML = `<span style="color:#eab308">⭐ Trusted</span>`;
            } else {
                const btnTrust = document.createElement("button");
                btnTrust.textContent = "Approve";
                btnTrust.className = "badge";
                btnTrust.style.cursor = "pointer";
                btnTrust.onclick = () => trustPeer(p.id);
                tdTrust.appendChild(btnTrust);
            }
            
            tr.appendChild(tdId);
            tr.appendChild(tdStatus);
            tr.appendChild(tdTrust);
            peersTbody.appendChild(tr);
        });
    }

    function updateSelectDropdown(peers) {
        const currentValue = msgTargetSelect.value;
        msgTargetSelect.innerHTML = `<option value="">-- Select a peer --</option>`;
        peers.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p.ip_port;
            opt.textContent = p.ip_port;
            msgTargetSelect.appendChild(opt);
        });
        
        // Restore selection if it still exists
        Array.from(msgTargetSelect.options).forEach(opt => {
            if (opt.value === currentValue) msgTargetSelect.value = currentValue;
        });
    }

    async function trustPeer(nodeId) {
        try {
            await fetch("/api/trust", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({node_id: nodeId})
            });
            fetchPeers(); // refresh UI
        } catch(e) {}
    }

    btnRefreshPeers.addEventListener("click", () => {
        btnRefreshPeers.style.transform = "rotate(360deg)";
        setTimeout(() => btnRefreshPeers.style.transform = "", 300);
        fetchPeers();
    });

    // --- 4. Send Message ---
    btnSendMsg.addEventListener("click", async () => {
        const target = msgTargetSelect.value;
        const content = msgContent.value.trim();
        
        if (!target) return showMessage(msgResult, "Select a target peer first.", true);
        if (!content) return showMessage(msgResult, "Message cannot be empty.", true);
        
        btnSendMsg.textContent = "ENCRYPTING...";
        
        try {
            const res = await fetch("/api/message", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({target, content})
            });
            const data = await res.json();
            
            if(data.error) showMessage(msgResult, data.error, true);
            else {
                showMessage(msgResult, "Message sent & verified by peer.");
                msgContent.value = "";
            }
        } catch (e) {
            showMessage(msgResult, "Connection error.", true);
        }
        btnSendMsg.textContent = "SEND SECURE MESSAGE";
    });

    // --- 5. Send File ---
    btnSendFile.addEventListener("click", async () => {
        const target = msgTargetSelect.value; // Reusing the same select box
        const filepath = filePathInput.value.trim();
        
        if (!target) return showMessage(fileResult, "Select a target peer from the Message panel.", true);
        if (!filepath) return showMessage(fileResult, "Enter a valid local file path.", true);
        
        btnSendFile.textContent = "CHUNKING...";
        
        try {
            const res = await fetch("/api/sendfile", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({target, filepath})
            });
            const data = await res.json();
            
            if(data.error) showMessage(fileResult, data.error, true);
            else showMessage(fileResult, "File transferred successfully.");
        } catch (e) {
            showMessage(fileResult, "Connection error or file too large.", true);
        }
        btnSendFile.textContent = "SEND MANIFEST & FILE";
    });

});
