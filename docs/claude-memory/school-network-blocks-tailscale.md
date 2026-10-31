---
name: school-network-blocks-tailscale
description: Tailscale is unusable from school two ways over; Cloudflare tunnels work, including over WARP
metadata:
  type: project
---

Measured 2026-10-29 on the school network, both directions:

- **Cloudflare WARP off:** every `*.tailscale.com` host completes the
  TCP handshake and is reset on the TLS ClientHello -- `tailscale.com`,
  `login.`, `controlplane.`, `derp1.`. github.com and example.com are
  unaffected. SNI filtering of the domain.
- **WARP on:** those hosts return 200/302, and Tailscale still does
  not work -- WARP and Tailscale are both whole-device VPNs and macOS
  will not run both. The tell is `BackendState: Running`,
  `InNetworkMap: true`, valid key, but `Online: false`,
  `InMagicSock: false`, `InEngine: false`, and health saying it
  cannot reach the coordination server.

`tunnel.ngrok.com` is blocked too. `trycloudflare.com` and
`api.trycloudflare.com` are reachable **with WARP on**, which is the
configuration the machine actually runs in.

**Why:** the login is not the problem and neither is the client.
Hours can go into a Tailscale setup that was never going to work from
there.

**How to apply:** remote access goes through `mau5relay.py --tunnel`
(and `--ssh` for a shell), which is Cloudflare and rides over WARP.
Tailscale is fine from a phone hotspot if it is ever needed. See
[[camera-page-must-be-started-by-hand]].
