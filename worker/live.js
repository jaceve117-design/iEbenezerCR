/**
 * Cloudflare Worker — estado de transmisión de Ministerios Ebenezer C.R
 *
 * Devuelve JSON:
 *   { live: bool, videoId: string|null, title: string|null,
 *     latest: { id, title, date } | null, ts: number }
 *
 * Por qué un Worker y no fetch directo desde el navegador:
 *   la API key de YouTube quedaría pública en el HTML. Aquí vive como secreto
 *   del Worker y el navegador solo ve el JSON ya resuelto.
 *
 * ── Deploy ──────────────────────────────────────────────────────────────
 *   npm i -g wrangler
 *   wrangler init ebenezer-live          (elegí "Hello World" Worker)
 *   # pegá este archivo en src/index.js
 *   wrangler secret put YT_API_KEY       # tu key de YouTube Data API v3
 *   wrangler deploy
 *
 *   Luego en site/index.html:
 *     CFG.liveEndpoint = 'https://ebenezer-live.<tu-subdominio>.workers.dev'
 *
 * ── wrangler.toml ───────────────────────────────────────────────────────
 *   name = "ebenezer-live"
 *   main = "src/index.js"
 *   compatibility_date = "2026-01-01"
 *
 *   [vars]
 *   CHANNEL_ID = "UCK6O7BIAhJAaTTSPqnF-o8g"
 *   ALLOW_ORIGIN = "https://tudominio.cr"   # o "*" mientras probás
 *
 * ── Cuota ───────────────────────────────────────────────────────────────
 *   search.list cuesta 100 unidades; el cupo diario gratuito es 10.000.
 *   Con el caché de 60 s de abajo, un día completo consume ~1.440 unidades
 *   sin importar cuánta gente entre al sitio.
 */

const CACHE_SECONDS = 60;

export default {
  async fetch(request, env, ctx) {
    const origin = env.ALLOW_ORIGIN || '*';
    const cors = {
      'access-control-allow-origin': origin,
      'access-control-allow-methods': 'GET,OPTIONS',
      'content-type': 'application/json; charset=utf-8',
      'cache-control': `public, max-age=${CACHE_SECONDS}`,
    };

    if (request.method === 'OPTIONS') return new Response(null, { headers: cors });
    if (request.method !== 'GET') return new Response('Method Not Allowed', { status: 405 });

    const channelId = env.CHANNEL_ID;
    const key = env.YT_API_KEY;
    if (!channelId || !key) {
      return json({ error: 'Faltan CHANNEL_ID o YT_API_KEY' }, 500, cors);
    }

    // Caché de borde: una sola llamada real a YouTube por minuto.
    const cache = caches.default;
    const cacheKey = new Request(new URL('/state', request.url).toString(), request);
    const hit = await cache.match(cacheKey);
    if (hit) return withCors(hit, cors);

    let payload;
    try {
      payload = await buildState(channelId, key);
    } catch (err) {
      // Nunca romper la web: si YouTube falla, el front cae a su modo sin API.
      payload = { live: false, videoId: null, title: null, latest: null, error: String(err), ts: Date.now() };
    }

    const res = json(payload, 200, cors);
    ctx.waitUntil(cache.put(cacheKey, res.clone()));
    return res;
  },
};

async function buildState(channelId, key) {
  // 1) ¿Hay transmisión activa?
  const liveUrl = new URL('https://www.googleapis.com/youtube/v3/search');
  liveUrl.search = new URLSearchParams({
    part: 'snippet', channelId, eventType: 'live', type: 'video', maxResults: '1', key,
  }).toString();

  const liveRes = await fetch(liveUrl, { cf: { cacheTtl: 45 } });
  if (!liveRes.ok) throw new Error(`search.live ${liveRes.status}`);
  const liveData = await liveRes.json();
  const liveItem = liveData.items && liveData.items[0];

  // 2) Último video subido (siempre, para el fallback del reproductor)
  const uploads = 'UU' + channelId.slice(2);
  const listUrl = new URL('https://www.googleapis.com/youtube/v3/playlistItems');
  listUrl.search = new URLSearchParams({
    part: 'snippet', playlistId: uploads, maxResults: '1', key,
  }).toString();

  let latest = null;
  const listRes = await fetch(listUrl, { cf: { cacheTtl: 300 } });
  if (listRes.ok) {
    const listData = await listRes.json();
    const it = listData.items && listData.items[0];
    if (it) {
      latest = {
        id: it.snippet.resourceId.videoId,
        title: it.snippet.title,
        date: it.snippet.publishedAt,
      };
    }
  }

  return {
    live: !!liveItem,
    videoId: liveItem ? liveItem.id.videoId : null,
    title: liveItem ? liveItem.snippet.title : null,
    latest,
    ts: Date.now(),
  };
}

function json(obj, status, headers) {
  return new Response(JSON.stringify(obj), { status, headers });
}
function withCors(res, cors) {
  const r = new Response(res.body, res);
  for (const [k, v] of Object.entries(cors)) r.headers.set(k, v);
  return r;
}
