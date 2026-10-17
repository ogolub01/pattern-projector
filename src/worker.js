// Notch site worker: serves the static site from ./public, plus one small endpoint for the waitlist.
// Sign-ups are kept in the KV namespace "notch-waitlist" (Cloudflare dashboard → Storage & databases → KV),
// one entry per email: key "email:<address>", value { email, at }.
const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });

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
    return env.ASSETS.fetch(request);
  }
};
