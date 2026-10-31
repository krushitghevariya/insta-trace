import { NextResponse } from "next/server";
import { fetchProfileHtml } from "../../../lib/instagram/fetchProfile";
import { extractTimelineJson } from "../../../lib/instagram/parseTimeline";
import { collectMediaFromTimeline } from "../../../lib/instagram/collectMedia";

export const dynamic = "force-dynamic";

export async function POST(req) {
  try {
    const body = await req.json();
    const usernameRaw = (body?.username || "").trim();

    if (!usernameRaw) {
      return NextResponse.json(
        { ok: false, error: "Username is required" },
        { status: 400 }
      );
    }

    const username = usernameRaw.replace(/^@+/, "");

    const html = await fetchProfileHtml(username);
    const { timeline, error: timelineError } = extractTimelineJson(html);

    if (timelineError) {
      return NextResponse.json(
        {
          ok: false,
          error: timelineError,
          vulnerable: false
        },
        { status: 500 }
      );
    }

    if (!timeline) {
      return NextResponse.json(
        {
          ok: true,
          vulnerable: false,
          username,
          media: [],
          message:
            "No private timeline data found. Account is likely not vulnerable (or empty / fully patched)."
        },
        { status: 200 }
      );
    }

    const media = collectMediaFromTimeline(timeline);

    const byPost = new Map();
    for (const item of media) {
      if (!byPost.has(item.postId)) byPost.set(item.postId, []);
      byPost.get(item.postId).push(item);
    }

    const postCount = byPost.size;

    return NextResponse.json(
      {
        ok: true,
        vulnerable: true,
        username,
        media,
        totalMedia: media.length,
        totalPosts: postCount
      },
      { status: 200 }
    );
  } catch (err) {
    console.error("scan error", err);
    return NextResponse.json(
      {
        ok: false,
        error: "Unexpected error while scanning profile"
      },
      { status: 500 }
    );
  }
}

