import { NextResponse } from "next/server";
import { inferDownloadMeta } from "../../../lib/downloadMeta";

export const dynamic = "force-dynamic";

export async function GET(req) {
  try {
    const { searchParams } = new URL(req.url);
    const mediaUrl = searchParams.get("url");
    const username = searchParams.get("username") || "instatrace";
    const postId = searchParams.get("postId") || "post";
    const resLabel = searchParams.get("res") || "";
    const kind = searchParams.get("kind") || "";

    if (!mediaUrl) {
      return NextResponse.json(
        { ok: false, error: "Missing url parameter" },
        { status: 400 }
      );
    }

    const upstream = await fetch(mediaUrl);
    if (!upstream.ok) {
      return NextResponse.json(
        { ok: false, error: `Upstream returned ${upstream.status}` },
        { status: 502 }
      );
    }

    const { ext, mime } = inferDownloadMeta(mediaUrl, resLabel, kind);
    const safeRes = String(resLabel || "").replace(/\s+/g, "").replace(/×/g, "x");
    const filename = `${username}_${postId}_${safeRes || "media"}.${ext}`;

    const headers = new Headers(upstream.headers);
    headers.set("content-type", mime);
    headers.set(
      "content-disposition",
      `attachment; filename="${filename.replace(/"/g, "")}"`
    );

    return new NextResponse(upstream.body, {
      status: upstream.status,
      headers
    });
  } catch (err) {
    console.error("download error", err);
    return NextResponse.json(
      { ok: false, error: "Failed to proxy media download" },
      { status: 500 }
    );
  }
}

