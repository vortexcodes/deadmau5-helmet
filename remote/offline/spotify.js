// ----------------------------------------------------------------------
// spotify.js -- where in the track we are, from the thing that knows.
//
// Everything else offline is self-contained; this is the one piece
// that reaches the internet, and it is worth it for one number.
// `progress_ms` is the clock a show has had to do without, and asking
// for it also gets pause, seek and skip handled for nothing.
//
// What it deliberately does not ask for: audio-features and
// audio-analysis were restricted on 27 November 2024 to apps that
// already had extended access, so a new app gets 403 and there is no
// appeal.  We would not want them anyway -- mau5song analyses these
// tracks at 40 Hz against Spotify's onset-delimited segments, and
// mau5drive carries that to the controller.  Spotify supplies the
// clock; the laptop supplied everything else.
//
// The token is a refresh token for one read-only scope, kept in this
// page's localStorage on the phone.  It never touches the controller
// and it is not in the repository.  Refreshing is done here because a
// PKCE client has no secret to protect.
// ----------------------------------------------------------------------

(function (root) {
'use strict';

const KEY = 'mau5.spotify';
const TOKEN = 'https://accounts.spotify.com/api/token';
const NOW = 'https://api.spotify.com/v1/me/player/currently-playing';

// Titles never match exactly.  A show is named after a file --
// "deadmau5 - Strobe (Dimension Remix)" -- and Spotify says
// "Strobe - Dimension Remix" with the artist somewhere else.  So
// compare the words, not the string.
function words(s) {
  return new Set(String(s).toLowerCase()
    .replace(/\.(mp3|m4a|wav|flac)$/, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .split(' ')
    .filter(w => w && w !== 'the' && w !== 'a' && w !== 'with'));
}

// Jaccard, not containment.  "Strobe - Dimension Remix" contains
// every word of the show called "Strobe", so containment scores that
// a perfect match and picks the wrong show; dividing by the union
// makes a missing word cost something and the remix wins its own
// name back.
function overlap(a, b) {
  const A = words(a), B = words(b);
  if (!A.size || !B.size) return 0;
  let n = 0;
  for (const w of A) if (B.has(w)) n++;
  return n / (A.size + B.size - n);
}

function bestShow(title, artists, shows) {
  let best = null, score = 0;
  const hay = title + ' ' + (artists || []).join(' ');
  for (const name of Object.keys(shows || {})) {
    const s = overlap(name, hay);
    if (s > score) { score = s; best = name; }
  }
  return score >= 0.5 ? { name: best, score } : null;
}

class Spotify {
  constructor() {
    this.clientId = null;
    this.refresh = null;
    this.access = null;
    this.expires = 0;
    this.err = '';
    this.last = null;          // the most recent currently-playing
    this.at = 0;               // performance.now() when it arrived
    try {
      const raw = localStorage.getItem(KEY);
      if (raw) {
        const d = JSON.parse(raw);
        this.clientId = d.c; this.refresh = d.r;
      }
    } catch (e) {}
  }

  get connected() { return !!(this.clientId && this.refresh); }

  // "<client id>.<refresh token>", as mau5spotify.py prints it.
  connect(blob) {
    const i = String(blob).trim().indexOf('.');
    if (i < 8) throw new Error('that does not look like the line '
                               + 'mau5spotify.py printed');
    this.clientId = blob.slice(0, i).trim();
    this.refresh = blob.slice(i + 1).trim();
    this.access = null; this.expires = 0; this.err = '';
    try {
      localStorage.setItem(KEY, JSON.stringify({ c: this.clientId,
                                                 r: this.refresh }));
    } catch (e) {}
  }

  forget() {
    this.clientId = this.refresh = this.access = null;
    this.expires = 0;
    try { localStorage.removeItem(KEY); } catch (e) {}
  }

  async token() {
    if (this.access && Date.now() < this.expires - 30000) return this.access;
    const body = new URLSearchParams({
      grant_type: 'refresh_token', refresh_token: this.refresh,
      client_id: this.clientId,
    });
    const r = await fetch(TOKEN, {
      method: 'POST', body,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    if (!r.ok) throw new Error('Spotify refused the token (' + r.status + ')');
    const d = await r.json();
    this.access = d.access_token;
    this.expires = Date.now() + (d.expires_in || 3600) * 1000;
    // Spotify rotates refresh tokens; keep the new one or the next
    // refresh after this session fails for no visible reason.
    if (d.refresh_token && d.refresh_token !== this.refresh) {
      this.refresh = d.refresh_token;
      try {
        localStorage.setItem(KEY, JSON.stringify({ c: this.clientId,
                                                   r: this.refresh }));
      } catch (e) {}
    }
    return this.access;
  }

  async poll() {
    const tok = await this.token();
    const r = await fetch(NOW, { headers: { Authorization: 'Bearer ' + tok } });
    if (r.status === 204) { this.last = null; return null; }
    if (r.status === 401) { this.access = null; throw new Error('token expired'); }
    if (r.status === 429) { throw new Error('rate limited'); }
    if (!r.ok) throw new Error('Spotify said ' + r.status);
    const d = await r.json();
    this.last = d;
    this.at = performance.now();
    this.err = '';
    return d;
  }

  // Where the track is now, in seconds, carried forward from the last
  // poll by the local clock.  A poll a second would otherwise make
  // the show step rather than run.
  position() {
    const d = this.last;
    if (!d || d.progress_ms == null) return null;
    const base = d.progress_ms / 1000;
    if (!d.is_playing) return base;
    return base + (performance.now() - this.at) / 1000;
  }

  get playing() { return !!(this.last && this.last.is_playing); }

  get track() {
    const it = this.last && this.last.item;
    return it ? { name: it.name,
                  artists: (it.artists || []).map(a => a.name),
                  id: it.id } : null;
  }
}

const api = { Spotify, bestShow, overlap };
root.MAU5 = Object.assign(root.MAU5 || {}, api);
if (typeof module !== 'undefined' && module.exports) module.exports = api;

})(typeof globalThis !== 'undefined' ? globalThis : this);
