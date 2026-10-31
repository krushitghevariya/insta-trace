export function inferDownloadMeta(url, resolutionLabel, kindHint) {
  const lower = (url || "").split("?", 1)[0].toLowerCase();
  const resLower = String(resolutionLabel || "").toLowerCase();
  const hint = (kindHint || "").toLowerCase();

  const looksVideo =
    lower.endsWith(".mp4") ||
    resLower.includes("video") ||
    hint === "video";

  if (looksVideo) {
    return { ext: "mp4", mime: "video/mp4" };
  }

  if (lower.endsWith(".png")) {
    return { ext: "png", mime: "image/png" };
  }
  if (lower.endsWith(".webp")) {
    return { ext: "webp", mime: "image/webp" };
  }
  if (lower.match(/\.(jpe?g|jfif)$/)) {
    return { ext: "jpg", mime: "image/jpeg" };
  }

  if (hint === "image") {
    return { ext: "jpg", mime: "image/jpeg" };
  }

  return { ext: "bin", mime: "application/octet-stream" };
}

