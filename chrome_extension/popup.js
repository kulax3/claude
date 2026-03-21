const BASE_URL = "https://tasks.googleapis.com/tasks/v1";

function setStatus(message, type = "loading") {
  const el = document.getElementById("status");
  el.textContent = message;
  el.className = `status-${type}`;
}

function setProgress(pct) {
  const bar = document.getElementById("progressBar");
  const fill = document.getElementById("progressFill");
  bar.style.display = pct > 0 ? "block" : "none";
  fill.style.width = `${pct}%`;
}

async function getToken() {
  return new Promise((resolve, reject) => {
    chrome.identity.getAuthToken({ interactive: true }, (token) => {
      if (chrome.runtime.lastError || !token) {
        reject(new Error(chrome.runtime.lastError?.message || "認証に失敗しました"));
      } else {
        resolve(token);
      }
    });
  });
}

async function apiFetch(token, url) {
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`API エラー: ${res.status} ${res.statusText}`);
  return res.json();
}

async function fetchTaskLists(token) {
  const data = await apiFetch(token, `${BASE_URL}/users/@me/lists?maxResults=100`);
  return data.items || [];
}

async function fetchTasks(token, listId, includeCompleted) {
  const tasks = [];
  let pageToken = "";

  do {
    const params = new URLSearchParams({
      maxResults: "100",
      showCompleted: String(includeCompleted),
      showHidden: String(includeCompleted),
    });
    if (pageToken) params.set("pageToken", pageToken);

    const data = await apiFetch(token, `${BASE_URL}/lists/${listId}/tasks?${params}`);
    tasks.push(...(data.items || []));
    pageToken = data.nextPageToken || "";
  } while (pageToken);

  return tasks;
}

function formatDate(isoString) {
  if (!isoString) return "";
  try {
    // 日付のみ (due) は YYYY-MM-DD、それ以外は datetime
    if (/^\d{4}-\d{2}-\d{2}T00:00:00\.000Z$/.test(isoString)) {
      return isoString.slice(0, 10);
    }
    return new Date(isoString).toLocaleString("ja-JP");
  } catch {
    return isoString;
  }
}

function buildCsvRow(values) {
  return values
    .map((v) => {
      const s = String(v ?? "").replace(/"/g, '""');
      return /[,"\n\r]/.test(s) ? `"${s}"` : s;
    })
    .join(",");
}

function tasksToCSV(allTasks, includeNotes) {
  const headers = ["タスクリスト", "タスク名", "ステータス", "期限", "完了日時"];
  if (includeNotes) headers.push("メモ");
  headers.push("更新日時", "親タスクID", "タスクID");

  const rows = [buildCsvRow(headers)];

  for (const { listTitle, task } of allTasks) {
    const status = task.status === "completed" ? "完了" : "未完了";
    const values = [
      listTitle,
      task.title || "",
      status,
      formatDate(task.due),
      formatDate(task.completed),
    ];
    if (includeNotes) values.push(task.notes || "");
    values.push(formatDate(task.updated), task.parent || "", task.id || "");
    rows.push(buildCsvRow(values));
  }

  return rows.join("\n");
}

function downloadCSV(csvContent) {
  // BOM付き UTF-8 (Excelで文字化けしない)
  const bom = "\uFEFF";
  const blob = new Blob([bom + csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const now = new Date();
  const timestamp = now.toISOString().slice(0, 19).replace(/[T:]/g, "-");
  const filename = `google_tasks_${timestamp}.csv`;

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();

  setTimeout(() => URL.revokeObjectURL(url), 1000);
  return filename;
}

document.getElementById("exportBtn").addEventListener("click", async () => {
  const btn = document.getElementById("exportBtn");
  const includeCompleted = document.getElementById("includeCompleted").checked;
  const includeNotes = document.getElementById("includeNotes").checked;

  btn.disabled = true;
  setStatus("認証中...", "loading");
  setProgress(10);

  try {
    const token = await getToken();
    setStatus("タスクリストを取得中...", "loading");
    setProgress(20);

    const lists = await fetchTaskLists(token);
    if (!lists.length) {
      setStatus("タスクリストが見つかりませんでした", "error");
      setProgress(0);
      return;
    }

    const allTasks = [];
    for (let i = 0; i < lists.length; i++) {
      const list = lists[i];
      setStatus(`取得中: ${list.title} (${i + 1}/${lists.length})`, "loading");
      setProgress(20 + ((i + 1) / lists.length) * 70);

      const tasks = await fetchTasks(token, list.id, includeCompleted);
      for (const task of tasks) {
        allTasks.push({ listTitle: list.title, task });
      }
    }

    setProgress(95);
    const csv = tasksToCSV(allTasks, includeNotes);
    const filename = downloadCSV(csv);
    setProgress(100);
    setStatus(`✓ ${allTasks.length} 件を ${filename} に保存しました`, "success");
  } catch (err) {
    setStatus(`エラー: ${err.message}`, "error");
    setProgress(0);
  } finally {
    btn.disabled = false;
  }
});
