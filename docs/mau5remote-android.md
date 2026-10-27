# mau5remote — Android app design

The web page in `remote/index.html` covers shows today. This is the shape of
the native app that replaces it, written down now so the API surface it needs
does not drift while the rest of the suite is built.

Kotlin + Jetpack Compose, single module, no backend of its own. Everything it
talks to is FPP's REST API on the Pi's hotspot.

## Why native at all

The web page has three problems that only a native app fixes:

| problem | web page | native |
|---|---|---|
| Android kills the tab when backgrounded, playback state is lost from the UI | reconnects on resume, blank for a second | foreground service holds the poll |
| screen sleeps mid-set | `navigator.wakeLock` — Chrome only, revoked on tab hide | `FLAG_KEEP_SCREEN_ON` on the activity |
| first paint waits on the network | localStorage cache helps, but the tab is cold-started | Room cache, list is on screen before the socket opens |

Everything else — big targets, one tap to start, no internet — the web page
already does, and the native app should not regress it.

## Screens

Two, and no navigation graph worth the name.

**Now / playlists** (the only screen anyone uses at a show)

```
┌─────────────────────────────┐
│ ● mau5head            ⚙︎    │   status dot: green = polled < 2 s ago
├─────────────────────────────┤
│ ghosts n stuff              │   72 sp, one line, ellipsised
│ ghosts.mp3 · 1/1            │
│ ▓▓▓▓▓▓▓░░░░░░░░░░░░░░       │
│ 1:12                 -2:19  │
├─────────────────────────────┤
│  ▷  intro                   │   64 dp rows, 8 dp gaps
│  ▶  ghosts n stuff          │   playing row outlined
│  ▷  strobe test             │
├─────────────────────────────┤
│ [ stop now ] [ stop after ] │   56 dp, thumb reachable
│ vol ──────●────────  70     │
└─────────────────────────────┘
```

**Settings** — Pi address, hotspot SSID reminder, poll interval, "forget
cache". A dialog, not a destination.

## Architecture

```
ui/            NowScreen, PlaylistRow, SettingsDialog     (Compose, stateless)
  ↑ StateFlow<UiState>
PlayerViewModel                                            (single source of truth)
  ↑            ↑
FppRepository  PlaybackService                             (foreground service)
  ↑
FppApi (Retrofit + Moshi)      PlaylistDao (Room)
```

* `FppRepository` is the only thing that knows FPP exists. It merges the Room
  cache and the network so the UI never waits: `playlists()` emits the cached
  list immediately, then the fresh one.
* `PlaybackService` is a foreground service started when a playlist starts and
  stopped when playback ends. It owns the 1 Hz status poll and posts a
  `MediaStyle` notification with stop actions, which is what keeps the process
  alive and gives lock-screen controls for free.
* The activity sets `FLAG_KEEP_SCREEN_ON` whenever `uiState.isPlaying`.

## API surface

Exactly what the web page uses, so both stay in step:

| call | endpoint | notes |
|---|---|---|
| list playlists | `GET /api/playlists` | array of names |
| start | `GET /api/playlist/{name}/start` | url-encode the name |
| stop | `GET /api/playlists/stop` | |
| stop gracefully | `GET /api/playlists/stopgracefully` | finishes the current item |
| status | `GET /api/fppd/status` | `status_name`, `current_playlist`, `seconds_played`, `seconds_remaining`, `volume` |
| volume | `POST /api/system/volume` `{"volume":70}` | |

```kotlin
interface FppApi {
    @GET("api/playlists")                 suspend fun playlists(): List<String>
    @GET("api/playlist/{name}/start")     suspend fun start(@Path("name") n: String)
    @GET("api/playlists/stop")            suspend fun stop()
    @GET("api/playlists/stopgracefully")  suspend fun stopGracefully()
    @GET("api/fppd/status")               suspend fun status(): FppStatus
    @POST("api/system/volume")            suspend fun volume(@Body v: VolumeBody)
}
```

## The bits that are easy to get wrong

* **Cleartext HTTP.** The Pi has no certificate and no internet to get one.
  Ship a `network_security_config.xml` that permits cleartext to the hotspot
  subnet only, not `cleartextTrafficPermitted="true"` globally.
* **Android will not use a network with no internet.** When the phone joins
  the Pi's AP, Android keeps mobile data as the default route and the app's
  requests leave over LTE. Bind the OkHttp client to the WiFi network:
  `ConnectivityManager.requestNetwork(NetworkRequest(TRANSPORT_WIFI))`, then
  `network.socketFactory`. Without this the app works on WiFi-only tablets and
  fails on every phone — it is the single most likely reason a build "can't see
  the Pi".
* **Short timeouts.** 3 s connect, 5 s read. A hung request must not stall the
  1 Hz poll.
* **Idempotent start.** Tapping a playing row re-issues start, which restarts
  the show. Ignore taps on the playing row, or confirm.
* **Volume races the poll.** Do not let a status response overwrite the slider
  for ~2.5 s after the user last moved it. (The web page had this bug.)
* **Doze.** The foreground service plus an active WiFi connection is enough; do
  not ask for battery-optimisation exemptions.

## Build order

1. `FppApi` + models + the WiFi-bound OkHttp client, with a unit test against a
   recorded status payload.
2. `NowScreen` reading a hardcoded `UiState` — get the touch targets right on
   the actual phone before wiring anything.
3. `FppRepository` + Room cache.
4. `PlaybackService` + notification.
5. Settings dialog, then delete nothing — keep `remote/index.html` as the
   fallback that needs no install.

Minimum SDK 26 (foreground services), target the current SDK.
