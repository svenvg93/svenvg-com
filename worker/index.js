import { gonePaths } from "./gone-paths.js";

function normalizePath(pathname) {
  if (pathname === "/") {
    return pathname;
  }

  return pathname.endsWith("/") ? pathname : `${pathname}/`;
}

function buildGoneResponse() {
  return new Response("Gone", {
    status: 410,
    headers: {
      "content-type": "text/plain; charset=utf-8",
      "cache-control": "public, max-age=300",
      "x-robots-tag": "noindex, nofollow",
    },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const normalizedPath = normalizePath(url.pathname);

    if (gonePaths.has(normalizedPath)) {
      return buildGoneResponse();
    }

    return env.ASSETS.fetch(request);
  },
};
