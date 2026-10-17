// Notch site worker: serves the static site from ./public, plus a few small endpoints.
//
// Public:
//   POST /api/waitlist      a waitlist sign-up → KV key "email:<address>", value { email, at }
// Behind Cloudflare Access (everything under /app is locked with the passcode login):
//   POST /app/api/feedback  feedback from inside the app → KV key "fb:<time>:<random>", value { text, by, at, … }
//   GET  /app/api/list      the waitlist and the feedback, for the private page /app/list/
//
// The /app/api/* endpoints also check the Access login token themselves, so they stay private
// even if the Access settings were ever changed by mistake.
const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });

const TEAM = 'https://odd-water-2b0b.cloudflareaccess.com';
let certs = null, certsAt = 0;
const b64url = s => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((s.length + 3) % 4)), c => c.charCodeAt(0));

// Returns the logged-in email if the request carries a valid Cloudflare Access token, otherwise null.
async function accessUser(request) {
  const token = request.headers.get('cf-access-jwt-assertion');
  if (!token) return null;
  const [h, p, sig] = token.split('.');
  if (!h || !p || !sig) return null;
  try {
    const head = JSON.parse(new TextDecoder().decode(b64url(h)));
    const body = JSON.parse(new TextDecoder().decode(b64url(p)));
    if (body.iss !== TEAM || !body.exp || body.exp * 1000 < Date.now()) return null;
    if (!certs || Date.now() - certsAt > 3600e3) {
      const r = await fetch(TEAM + '/cdn-cgi/access/certs');
      certs = (await r.json()).keys || []; certsAt = Date.now();
    }
    const jwk = certs.find(k => k.kid === head.kid);
    if (!jwk) return null;
    const key = await crypto.subtle.importKey('jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
    const ok = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, b64url(sig), new TextEncoder().encode(h + '.' + p));
    return ok ? (body.email || 'signed in') : null;
  } catch { return null; }
}

async function readAll(kv, prefix) {
  const out = []; let cursor;
  do {
    const page = await kv.list({ prefix, cursor, limit: 1000 });
    for (const k of page.keys) { try { out.push(JSON.parse(await kv.get(k.name))); } catch {} }
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor && out.length < 5000);
  return out;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === '/api/waitlist') {
      if (request.method !== 'POST') return json({ error: 'Use POST' }, 405);
      const len = +(request.headers.get('content-length') || 0);
      if (len > 2000) return json({ error: 'Too large' }, 413);
      let data;
      try { data = await request.json(); } catch { return json({ error: 'Send JSON' }, 400); }
      if (data && data.website) return json({ ok: true });             // honeypot filled in: a bot, quietly ignored
      const email = String((data && data.email) || '').trim().toLowerCase();
      if (email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return json({ error: 'Check the email address' }, 400);
      const key = 'email:' + email;
      if (!(await env.WAITLIST.get(key))) await env.WAITLIST.put(key, JSON.stringify({ email, at: new Date().toISOString() }));
      return json({ ok: true });
    }

    if (url.pathname.startsWith('/app/api/')) {
      const user = await accessUser(request);
      if (!user) return json({ error: 'Not signed in' }, 401);

      if (url.pathname === '/app/api/feedback') {
        if (request.method !== 'POST') return json({ error: 'Use POST' }, 405);
        if (+(request.headers.get('content-length') || 0) > 10000) return json({ error: 'Too large' }, 413);
        let d;
        try { d = await request.json(); } catch { return json({ error: 'Send JSON' }, 400); }
        const text = String((d && d.text) || '').trim().slice(0, 4000);
        if (!text) return json({ error: 'Empty' }, 400);
        const at = new Date().toISOString();
        const rec = { text, by: user, at, file: String(d.file || '').slice(0, 200), screen: String(d.screen || '').slice(0, 20), phone: !!d.phone, ua: String(d.ua || '').slice(0, 200) };
        await env.WAITLIST.put('fb:' + at + ':' + Math.random().toString(36).slice(2, 8), JSON.stringify(rec));
        return json({ ok: true });
      }

      if (url.pathname === '/app/api/list') {
        const [waitlist, feedback] = await Promise.all([readAll(env.WAITLIST, 'email:'), readAll(env.WAITLIST, 'fb:')]);
        waitlist.sort((a, b) => (b.at || '').localeCompare(a.at || ''));
        feedback.sort((a, b) => (b.at || '').localeCompare(a.at || ''));
        return json({ waitlist, feedback });
      }
      return json({ error: 'Not found' }, 404);
    }

    return env.ASSETS.fetch(request);
  }
};
