import * as cheerio from "cheerio";

export function extractTimelineJson(html) {
  if (!html) return { timeline: null, error: "Empty HTML" };

  const $ = cheerio.load(html);
  const scripts = $('script[type="application/json"], script');

  for (let i = 0; i < scripts.length; i += 1) {
    const el = scripts[i];
    const text = $(el).text() || "";
    if (
      text.includes("image_versions2") ||
      text.includes("video_versions") ||
      text.includes("video_url") ||
      text.includes("polaris_timeline_connection") ||
      text.includes("clips")
    ) {
      try {
        const data = JSON.parse(text);
        return { timeline: data, error: null };
      } catch (e) {
        continue; // try next script
      }
    }
  }

  return { timeline: null, error: null };
}
