export async function onRequest(context) {
  const url = new URL(context.request.url);

  const res = await fetch("https://www.svenvg.com/gone.json");
  const data = await res.json();

  const gone = new Set(data.gone || []);

  if (gone.has(url.pathname)) {
    return new Response("Gone", { status: 410 });
  }

  return context.next();
}