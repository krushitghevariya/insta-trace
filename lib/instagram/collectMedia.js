function pushBestImageFromNode(node, postId, acc) {
  const imageVersions = node.image_versions2;
  if (!imageVersions || !Array.isArray(imageVersions.candidates)) return;

  let best = null;
  let bestScore = -1;

  for (const cand of imageVersions.candidates) {
    const url = cand.url;
    if (!url) continue;
    const w = cand.width;
    const h = cand.height;
    const score =
      typeof w === "number" && typeof h === "number" ? w * h : 0;
    if (score > bestScore) {
      bestScore = score;
      best = cand;
    }
  }

  if (best && best.url) {
    const w = best.width ?? "?";
    const h = best.height ?? "?";
    const resolutionLabel = `${w}×${h}`;
    acc.push({
      postId,
      resolution: resolutionLabel,
      url: best.url,
      kind: "image"
    });
  }
}

function pushBestVideoFromNode(node, postId, acc) {
  const videoVersions = node.video_versions;
  if (!Array.isArray(videoVersions)) return;

  let best = null;
  let bestScore = -1;

  for (const cand of videoVersions) {
    const url = cand.url;
    if (!url) continue;
    const w = cand.width;
    const h = cand.height;
    const score =
      typeof w === "number" && typeof h === "number" ? w * h : 0;
    if (score > bestScore) {
      bestScore = score;
      best = cand;
    }
  }

  if (best && best.url) {
    const w = best.width ?? "?";
    const h = best.height ?? "?";
    const resolutionLabel = `${w}×${h} (video)`;
    acc.push({
      postId,
      resolution: resolutionLabel,
      url: best.url,
      kind: "video"
    });
  }
}

export function collectMediaFromTimeline(data, acc = [], currentPostId = null) {
  if (!data || typeof data !== "object") return acc;

  if (Array.isArray(data)) {
    for (const item of data) {
      collectMediaFromTimeline(item, acc, currentPostId);
    }
    return acc;
  }

  let postId = currentPostId;
  if (Object.prototype.hasOwnProperty.call(data, "pk")) {
    postId = String(data.pk ?? "unknown");
  }

  pushBestImageFromNode(data, postId, acc);
  pushBestVideoFromNode(data, postId, acc);

  for (const value of Object.values(data)) {
    collectMediaFromTimeline(value, acc, postId);
  }

  return acc;
}

