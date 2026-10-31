export function formatTxt(username, media) {
  if (!media?.length) return "";

  const byPost = new Map();
  for (const item of media) {
    if (!byPost.has(item.postId)) byPost.set(item.postId, []);
    byPost.get(item.postId).push(item);
  }

  const lines = [];
  lines.push(`InstaTrace – @${username} – ${media.length} media`);
  lines.push("======================================================================");
  lines.push("");
  lines.push(
    `Posts: ${byPost.size}    Media variants: ${media.length}`
  );
  lines.push("");

  for (const [postId, list] of Array.from(byPost.entries()).sort(
    ([a], [b]) => String(a).localeCompare(String(b))
  )) {
    lines.push(`Post ${postId}`);
    lines.push(`  ${list.length} variants`);
    lines.push("----------------------------------------------------------------------");
    list.forEach((item, idx) => {
      const label = item.kind === "video" ? "video" : "image";
      lines.push(
        `  ${String(idx + 1).padStart(2, " ")}. ${String(
          item.resolution
        ).padStart(10, " ")}   [${label}] ${item.url}`
      );
    });
    lines.push("");
  }

  return lines.join("\n");
}

export function formatCsv(media) {
  if (!media?.length) return "";

  const header = ["Post ID", "Resolution", "Kind", "URL"];
  const rows = [header.join(",")];

  const sorted = [...media].sort((a, b) =>
    String(a.postId).localeCompare(String(b.postId))
  );

  for (const item of sorted) {
    const row = [
      item.postId,
      item.resolution.replace(/,/g, "x"),
      item.kind,
      item.url
    ];
    rows.push(row.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(","));
  }

  return rows.join("\n");
}

export function formatJson(username, media) {
  if (!media?.length) {
    return JSON.stringify(
      { username, totalMedia: 0, totalPosts: 0, posts: {} },
      null,
      2
    );
  }

  const posts = {};
  for (const item of media) {
    if (!posts[item.postId]) posts[item.postId] = [];
    posts[item.postId].push({
      kind: item.kind,
      resolution: item.resolution,
      url: item.url
    });
  }

  const doc = {
    username,
    totalMedia: media.length,
    totalPosts: Object.keys(posts).length,
    posts
  };

  return JSON.stringify(doc, null, 2);
}

