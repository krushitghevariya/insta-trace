"use client";

import { useMemo, useState } from "react";
import { formatTxt, formatCsv, formatJson } from "../lib/formatters";

function groupByPost(media) {
  const byPost = new Map();
  for (const item of media || []) {
    if (!byPost.has(item.postId)) byPost.set(item.postId, []);
    byPost.get(item.postId).push(item);
  }
  return byPost;
}

function downloadBlob(filename, mime, text) {
  const blob = new Blob([text], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export default function HomePage() {
  const [username, setUsername] = useState("");
  const [scanState, setScanState] = useState("idle"); // idle | loading | error | success
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState("overview"); // overview | gallery | table | downloads

  const [showPreviews, setShowPreviews] = useState(false);
  const [galleryCols, setGalleryCols] = useState(3);
  const [maxPosts, setMaxPosts] = useState(12);
  const [maxVariants, setMaxVariants] = useState(6);

  const byPost = useMemo(
    () => groupByPost(result?.media || []),
    [result?.media]
  );
  const postIds = useMemo(
    () =>
      Array.from(byPost.keys()).sort((a, b) =>
        String(a).localeCompare(String(b)
      )),
    [byPost]
  );

  const [galleryFilter, setGalleryFilter] = useState("All");

  const totalMedia = result?.totalMedia ?? 0;
  const totalPosts = result?.totalPosts ?? 0;
  const avgPerPost =
    totalPosts > 0 ? (totalMedia / totalPosts).toFixed(1) : "0.0";

  async function runScan(e) {
    e.preventDefault();
    const clean = String(username || "").trim().replace(/^@+/, "");
    if (!clean) {
      setError("Username is required");
      setScanState("error");
      return;
    }
    setScanState("loading");
    setError("");
    setResult(null);

    try {
      const res = await fetch("/api/scan", {
        method: "POST",
        headers: {
          "content-type": "application/json"
        },
        body: JSON.stringify({ username: clean })
      });

      const data = await res.json();

      if (!res.ok || data.ok === false) {
        setError(data.error || "Scan failed");
        setScanState("error");
        return;
      }

      setResult(data);
      setScanState("success");
    } catch (err) {
      console.error(err);
      setError("Network error while scanning");
      setScanState("error");
    }
  }

  function renderStatusBanner() {
    if (scanState === "error" && error) {
      return (
        <div className="card-soft" style={{ borderColor: "#f97373" }}>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>Error</div>
          <div className="muted" style={{ fontSize: 13 }}>
            {error}
          </div>
        </div>
      );
    }

    if (result && result.vulnerable === false) {
      return (
        <div className="card-soft" style={{ borderColor: "#38bdf8" }}>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>Not vulnerable</div>
          <div className="muted" style={{ fontSize: 13 }}>
            No private timeline data was detected. The account is likely empty,
            blocked, or fully patched (expected behaviour).
          </div>
        </div>
      );
    }

    if (result && result.vulnerable === true) {
      return (
        <div className="card-soft" style={{ borderColor: "#fb7185" }}>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>Vulnerable POC</div>
          <div className="muted" style={{ fontSize: 13 }}>
            Private timeline-like data was extracted in this proof-of-concept
            simulation.
          </div>
        </div>
      );
    }

    return null;
  }

  function renderEmptyState() {
    if (scanState !== "idle" || result) return null;
    return (
      <div className="card" style={{ marginTop: "1rem" }}>
        <h3 style={{ marginTop: 0, marginBottom: 4 }}>Get started</h3>
        <p className="muted" style={{ fontSize: 13, marginBottom: 0 }}>
          Enter an Instagram username in the sidebar and run a scan. If data is
          found, you&apos;ll see overview metrics, a gallery, a table, and
          export options here.
        </p>
      </div>
    );
  }

  function renderOverviewTab() {
    if (!result) return null;
    return (
      <div className="card">
        <div className="kpi-grid" style={{ marginBottom: "1rem" }}>
          <div className="card-soft">
            <div className="muted" style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: 0.08 }}>
              Total Media
            </div>
            <div style={{ fontSize: 20, fontWeight: 600 }}>{totalMedia}</div>
          </div>
          <div className="card-soft">
            <div className="muted" style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: 0.08 }}>
              Total Posts
            </div>
            <div style={{ fontSize: 20, fontWeight: 600 }}>{totalPosts}</div>
          </div>
          <div className="card-soft">
            <div className="muted" style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: 0.08 }}>
              Avg per Post
            </div>
            <div style={{ fontSize: 20, fontWeight: 600 }}>{avgPerPost}</div>
          </div>
        </div>
        {!showPreviews && (
          <p className="muted" style={{ fontSize: 13, marginTop: 4 }}>
            Thumbnails are disabled for speed. Enable previews from the sidebar
            to visually inspect a subset of media.
          </p>
        )}
      </div>
    );
  }

  function renderGalleryTab() {
    if (!result) return null;

    const allIds = postIds;
    let ids = allIds;
    if (galleryFilter !== "All") ids = allIds.filter((id) => id === galleryFilter);
    if (ids.length > maxPosts) {
      ids = ids.slice(0, maxPosts);
    }

    return (
      <div className="card">
        <div
          style={{
            display: "flex",
            gap: "0.75rem",
            alignItems: "center",
            marginBottom: "0.75rem"
          }}
        >
          <div>
            <div className="field-label">Post filter</div>
            <select
              value={galleryFilter}
              onChange={(e) => setGalleryFilter(e.target.value)}
              className="text-input"
              style={{ maxWidth: 220 }}
            >
              <option value="All">All posts</option>
              {allIds.map((id) => (
                <option key={id} value={id}>
                  Post {id}
                </option>
              ))}
            </select>
          </div>
          <div className="muted" style={{ fontSize: 12 }}>
            Showing up to {maxPosts} posts, {maxVariants} variants per post.
          </div>
        </div>

        {!ids.length && (
          <p className="muted" style={{ fontSize: 13 }}>
            No media found for this filter.
          </p>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {ids.map((pid, index) => {
            const items = (byPost.get(pid) || []).slice(0, maxVariants);
            if (!items.length) return null;

            const gridCols = Math.max(2, Math.min(5, galleryCols));

            return (
              <div key={pid} className="card-soft">
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "0.5rem"
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600 }}>
                      📌 Post #{index + 1} – ID {pid}
                    </div>
                    <div className="muted" style={{ fontSize: 12 }}>
                      Showing {items.length} / {(byPost.get(pid) || []).length} variants
                    </div>
                  </div>
                  <button
                    className="btn-primary"
                    style={{ width: "auto", paddingInline: "0.9rem" }}
                    type="button"
                    onClick={() => {
                      const urls = (byPost.get(pid) || []).map((m) => m.url).join("\n");
                      downloadBlob(
                        `${result.username}_post_${pid}_urls.txt`,
                        "text/plain",
                        urls
                      );
                    }}
                  >
                    ⬇️ URLs for post
                  </button>
                </div>

                <div
                  className="gallery-grid"
                  style={{
                    gridTemplateColumns: `repeat(${gridCols}, minmax(0, 1fr))`
                  }}
                >
                  {items.map((item, idx) => {
                    const isVideo = item.kind === "video";
                    const downloadHref = `/api/download?url=${encodeURIComponent(
                      item.url
                    )}&username=${encodeURIComponent(
                      result.username
                    )}&postId=${encodeURIComponent(
                      item.postId
                    )}&res=${encodeURIComponent(
                      item.resolution
                    )}&kind=${encodeURIComponent(item.kind)}`;
                    return (
                      <div key={item.url + idx} className="card-soft">
                        <div
                          style={{
                            fontSize: 12,
                            marginBottom: 4,
                            display: "flex",
                            justifyContent: "space-between",
                            gap: 8
                          }}
                        >
                          <span>{item.resolution}</span>
                          <span className="muted">
                            {isVideo ? "video" : "image"}
                          </span>
                        </div>
                        {showPreviews && (
                          <div
                            style={{
                              borderRadius: 8,
                              overflow: "hidden",
                              marginBottom: 6,
                              backgroundColor: "#020617"
                            }}
                          >
                            {isVideo ? (
                              <video
                                src={item.url}
                                controls
                                style={{ width: "100%", display: "block" }}
                              />
                            ) : (
                              <img
                                src={item.url}
                                alt={item.resolution}
                                style={{ width: "100%", display: "block" }}
                              />
                            )}
                          </div>
                        )}
                        <div
                          style={{
                            display: "flex",
                            flexDirection: "column",
                            gap: 6
                          }}
                        >
                          <button
                            type="button"
                            className="btn-primary"
                            style={{ paddingBlock: 6 }}
                            onClick={() => window.open(downloadHref, "_blank")}
                          >
                            ⬇️ Download {isVideo ? "MP4" : "image"}
                          </button>
                          <details>
                            <summary
                              className="muted"
                              style={{ fontSize: 11, cursor: "pointer" }}
                            >
                              View URL
                            </summary>
                            <code
                              style={{
                                fontSize: 11,
                                wordBreak: "break-all",
                                display: "block",
                                marginTop: 4
                              }}
                            >
                              {item.url}
                            </code>
                          </details>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  function renderTableTab() {
    if (!result) return null;
    return (
      <div className="card" style={{ overflowX: "auto" }}>
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            fontSize: 13
          }}
        >
          <thead>
            <tr style={{ borderBottom: "1px solid rgba(148,163,184,0.4)" }}>
              <th style={{ textAlign: "left", padding: "0.45rem" }}>Post ID</th>
              <th style={{ textAlign: "left", padding: "0.45rem" }}>Kind</th>
              <th style={{ textAlign: "left", padding: "0.45rem" }}>
                Resolution
              </th>
              <th style={{ textAlign: "left", padding: "0.45rem" }}>URL</th>
            </tr>
          </thead>
          <tbody>
            {(result.media || []).map((item, idx) => (
              <tr
                key={item.url + idx}
                style={{
                  borderBottom:
                    "1px solid rgba(30,64,175,0.35)"
                }}
              >
                <td style={{ padding: "0.4rem" }}>{item.postId}</td>
                <td style={{ padding: "0.4rem" }}>{item.kind}</td>
                <td style={{ padding: "0.4rem" }}>{item.resolution}</td>
                <td style={{ padding: "0.4rem" }}>
                  <code
                    style={{
                      fontSize: 11,
                      wordBreak: "break-all"
                    }}
                  >
                    {item.url}
                  </code>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  function renderDownloadsTab() {
    if (!result) return null;

    const txt = formatTxt(result.username, result.media || []);
    const csv = formatCsv(result.media || []);
    const json = formatJson(result.username, result.media || []);

    return (
      <div className="card">
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
            gap: "0.75rem"
          }}
        >
          <button
            className="btn-primary"
            type="button"
            onClick={() =>
              downloadBlob(
                `${result.username}_urls.txt`,
                "text/plain",
                txt
              )
            }
          >
            📄 TXT
          </button>
          <button
            className="btn-primary"
            type="button"
            onClick={() =>
              downloadBlob(
                `${result.username}_urls.csv`,
                "text/csv",
                csv
              )
            }
          >
            📊 CSV
          </button>
          <button
            className="btn-primary"
            type="button"
            onClick={() =>
              downloadBlob(
                `${result.username}_urls.json`,
                "application/json",
                json
              )
            }
          >
            📋 JSON
          </button>
        </div>
        <div style={{ marginTop: "1rem" }}>
          <div className="section-title">Preview (TXT)</div>
          <pre
            style={{
              maxHeight: 320,
              overflow: "auto",
              fontSize: 11,
              background: "#020617",
              padding: "0.75rem",
              borderRadius: 8,
              marginTop: 6
            }}
          >
            {txt}
          </pre>
        </div>
      </div>
    );
  }

  const hasResult = !!result;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div style={{ marginBottom: "1.25rem" }}>
          <div className="pill">
            <span>📸</span>
            <span>InstaTrace Web</span>
          </div>
        </div>
        <form onSubmit={runScan} className="card" style={{ marginBottom: "1rem" }}>
          <div className="section-title">Run scan</div>
          <p className="section-caption">
            Only test accounts you own or have explicit permission for.
          </p>
          <div style={{ marginTop: "0.75rem" }}>
            <div className="field-label">Instagram username</div>
            <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
              <span style={{ color: "#9ca3af" }}>@</span>
              <input
                className="text-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="username"
              />
            </div>
          </div>
          <button
            type="submit"
            className="btn-primary"
            style={{ marginTop: "0.9rem" }}
            disabled={scanState === "loading"}
          >
            {scanState === "loading" ? "Scanning…" : "Run scan"}
          </button>
        </form>

        <div className="card" style={{ marginBottom: "1rem" }}>
          <div className="section-title">Display</div>
          <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 8 }}>
            <label style={{ display: "flex", gap: 8, alignItems: "center", fontSize: 13 }}>
              <input
                type="checkbox"
                checked={showPreviews}
                onChange={(e) => setShowPreviews(e.target.checked)}
              />
              <span>Show media previews</span>
            </label>
            <label style={{ fontSize: 13 }}>
              Gallery columns
              <input
                type="number"
                min={2}
                max={5}
                value={galleryCols}
                onChange={(e) =>
                  setGalleryCols(Math.min(5, Math.max(2, Number(e.target.value) || 3)))
                }
                className="text-input"
                style={{ marginTop: 2 }}
              />
            </label>
            <label style={{ fontSize: 13 }}>
              Max posts to render
              <input
                type="number"
                min={5}
                max={50}
                value={maxPosts}
                onChange={(e) =>
                  setMaxPosts(Math.min(50, Math.max(5, Number(e.target.value) || 12)))
                }
                className="text-input"
                style={{ marginTop: 2 }}
              />
            </label>
            <label style={{ fontSize: 13 }}>
              Max variants per post
              <input
                type="number"
                min={1}
                max={20}
                value={maxVariants}
                onChange={(e) =>
                  setMaxVariants(
                    Math.min(20, Math.max(1, Number(e.target.value) || 6))
                  )
                }
                className="text-input"
                style={{ marginTop: 2 }}
              />
            </label>
          </div>
        </div>

        <div className="card">
          <div className="section-title">About</div>
          <p className="section-caption">
            InstaTrace is a proof-of-concept interface for exploring how private
            media URLs could historically be enumerated via Instagram web data.
            The underlying issue has been patched by Meta.
          </p>
        </div>
      </aside>

      <main className="main">
        <header style={{ marginBottom: "1.25rem" }}>
          <h1 className="header-title">
            📸 InstaTrace <span style={{ color: "#fb7185" }}>Web</span>
          </h1>
          <p className="header-subtitle">
            Instagram Private Image URL Extractor (POC) – rebuilt as a modern web
            app.
          </p>
        </header>

        <div className="card" style={{ marginBottom: "1rem" }}>
          <div
            style={{
              fontWeight: 600,
              marginBottom: 4,
              color: "#facc15"
            }}
          >
            ⚠️ Research & educational use only
          </div>
          <p className="muted" style={{ fontSize: 13, marginBottom: 0 }}>
            This is a simulated proof-of-concept UI. The original vulnerability
            was fixed by Instagram/Meta in late 2025. Only test on accounts you
            own or have explicit permission to assess.
          </p>
        </div>

        {renderStatusBanner()}
        {renderEmptyState()}

        {hasResult && (
          <div style={{ marginTop: "1rem" }}>
            <div
              className="tabs"
              style={{
                marginBottom: "0.75rem"
              }}
            >
              <button
                type="button"
                data-active={activeTab === "overview"}
                onClick={() => setActiveTab("overview")}
              >
                Overview
              </button>
              <button
                type="button"
                data-active={activeTab === "gallery"}
                onClick={() => setActiveTab("gallery")}
              >
                Gallery
              </button>
              <button
                type="button"
                data-active={activeTab === "table"}
                onClick={() => setActiveTab("table")}
              >
                Table
              </button>
              <button
                type="button"
                data-active={activeTab === "downloads"}
                onClick={() => setActiveTab("downloads")}
              >
                Downloads
              </button>
            </div>

            {activeTab === "overview" && renderOverviewTab()}
            {activeTab === "gallery" && renderGalleryTab()}
            {activeTab === "table" && renderTableTab()}
            {activeTab === "downloads" && renderDownloadsTab()}
          </div>
        )}

        <footer style={{ marginTop: "2rem", fontSize: 12 }} className="muted">
          InstaTrace © 2025 — Educational POC only — Vulnerability patched by
          Instagram/Meta.
        </footer>
      </main>
    </div>
  );
}

