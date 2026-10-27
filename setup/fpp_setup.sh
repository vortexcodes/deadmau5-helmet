#!/usr/bin/env bash
# fpp_setup.sh -- configure a fresh Falcon Player for the mau5head.
#
#   scp setup/fpp_setup.sh fpp@<pi>:~
#   ssh fpp@<pi> 'sudo bash fpp_setup.sh'            # dry run, changes nothing
#   ssh fpp@<pi> 'sudo bash fpp_setup.sh --apply'
#
# It does four things, all idempotent -- re-running is a no-op:
#   1. turns on FPP's own WiFi hotspot (tethering), so the helmet and the
#      phone have a network with no infrastructure and no internet;
#   2. routes audio to the Pi's 3.5 mm jack (and re-enables the onboard audio
#      device, which several FPP images ship switched off);
#   3. adds a DDP channel output aimed at the controller, with the right
#      channel count;
#   4. restarts fppd.
#
# Every value has a default matching helmet.toml.  Run
# `setup/make_wled_config.py` on your laptop -- it prints the exact invocation
# for your current config.
#
# Nothing here is destructive: every file it edits is copied to
# <file>.mau5.bak-<timestamp> first, and it never deletes a playlist,
# sequence or media file.

set -euo pipefail

SSID="mau5head"
PSK="${PSK:-}"   # set with --psk; no default, so it cannot ship as one
CONTROLLER_IP="192.168.4.50"
CHANNELS="4218"
FPS="40"
DESC="mau5head"
APPLY=0
RESTART=1

usage() { sed -n '2,32p' "$0" | sed 's/^# \{0,1\}//'; exit 0; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ssid)          SSID="$2"; shift 2 ;;
    --psk)           PSK="$2"; shift 2 ;;
    --controller-ip) CONTROLLER_IP="$2"; shift 2 ;;
    --channels)      CHANNELS="$2"; shift 2 ;;
    --fps)           FPS="$2"; shift 2 ;;
    --apply)         APPLY=1; shift ;;
    --dry-run)       APPLY=0; shift ;;
    --no-restart)    RESTART=0; shift ;;
    -h|--help)       usage ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$PSK" ]]; then
  echo "refusing to run without --psk: a default hotspot password in a" >&2
  echo "public script is the same as no password at all." >&2
  exit 2
fi

MEDIA="${FPP_MEDIA:-/home/fpp/media}"   # override to rehearse against a copy
SETTINGS="$MEDIA/settings"
CO="$MEDIA/config/co-universes.json"
STAMP=$(date +%Y%m%d-%H%M%S)

say()  { printf '%s\n' "$*"; }
step() { printf '\n== %s\n' "$*"; }
run()  { if [[ $APPLY -eq 1 ]]; then eval "$@"; else say "   would run: $*"; fi }

# portable in-place sed (BSD sed needs an argument to -i, GNU sed does not)
sed_i() {
  local f="$1"; shift
  local tmp; tmp=$(mktemp)
  sed "$@" "$f" > "$tmp" && cat "$tmp" > "$f"
  rm -f "$tmp"
}

backup() {
  [[ -f "$1" ]] || return 0
  if [[ $APPLY -eq 1 ]]; then
    cp -p "$1" "$1.mau5.bak-$STAMP"
    say "   backed up $1 -> $1.mau5.bak-$STAMP"
  else
    say "   would back up $1"
  fi
}

# key = "value" in FPP's settings file; update in place or append
set_setting() {
  local key="$1" val="$2" cur=""
  [[ -f "$SETTINGS" ]] && cur=$(sed -n "s/^${key}[[:space:]]*=[[:space:]]*\"\{0,1\}\([^\"]*\)\"\{0,1\}[[:space:]]*$/\1/p" "$SETTINGS" | tail -1)
  if [[ "$cur" == "$val" ]]; then
    say "   $key already \"$val\""
    return 0
  fi
  say "   $key: \"${cur:-<unset>}\" -> \"$val\""
  if [[ $APPLY -eq 1 ]]; then
    touch "$SETTINGS"
    if grep -q "^${key}[[:space:]]*=" "$SETTINGS"; then
      sed_i "$SETTINGS" "s|^${key}[[:space:]]*=.*|${key} = \"${val}\"|"
    else
      printf '%s = "%s"\n' "$key" "$val" >> "$SETTINGS"
    fi
  fi
}

# --------------------------------------------------------------------------
step "checks"
if [[ ! -d "$MEDIA" ]]; then
  echo "   $MEDIA not found -- this is meant to run on the Falcon Player Pi." >&2
  exit 1
fi
if [[ $EUID -ne 0 && -z "${FPP_MEDIA:-}" ]]; then
  echo "   run me with sudo." >&2
  exit 1
fi
say "   FPP media dir  $MEDIA"
say "   mode           $([[ $APPLY -eq 1 ]] && echo APPLY || echo 'DRY RUN (add --apply to write)')"
say "   hotspot        $SSID"
say "   controller     $CONTROLLER_IP, $CHANNELS channels at $FPS fps"

backup "$SETTINGS"

# --------------------------------------------------------------------------
step "1. WiFi hotspot (FPP tethering)"
# 2 = always on.  FPP brings up the AP itself and runs the DHCP server; the
# controller and the phone both join it.  There is deliberately no uplink.
set_setting EnableTethering 2
set_setting TetherSSID "$SSID"
set_setting TetherPSK  "$PSK"
set_setting HostName   "mau5-fpp"

# --------------------------------------------------------------------------
step "2. audio out of the 3.5 mm jack"
BOOTCFG="${FPP_MEDIA:+$MEDIA/config.txt}"
[[ -n "$BOOTCFG" ]] || BOOTCFG=/boot/firmware/config.txt
[[ -f "$BOOTCFG" ]] || BOOTCFG=/boot/config.txt
if [[ -f "$BOOTCFG" ]]; then
  if grep -qE '^[[:space:]]*dtparam=audio=on' "$BOOTCFG"; then
    say "   onboard audio already enabled in $BOOTCFG"
  else
    backup "$BOOTCFG"
    say "   enabling onboard audio in $BOOTCFG (needs a reboot to take effect)"
    if [[ $APPLY -eq 1 ]]; then
      sed_i "$BOOTCFG" 's/^[[:space:]]*dtparam=audio=off.*/dtparam=audio=on/' 
      grep -qE '^[[:space:]]*dtparam=audio=on' "$BOOTCFG" || echo 'dtparam=audio=on' >> "$BOOTCFG"
    fi
    NEEDS_REBOOT=1
  fi
fi

CARD=$(aplay -l 2>/dev/null | sed -n 's/^card \([0-9]\{1,\}\).*[Hh]eadphones.*/\1/p' | head -1 || true)
if [[ -z "${CARD:-}" ]]; then
  CARD=$(aplay -l 2>/dev/null | sed -n 's/^card \([0-9]\{1,\}\).*bcm2835.*/\1/p' | head -1 || true)
fi
if [[ -n "${CARD:-}" ]]; then
  say "   headphone jack is ALSA card $CARD"
  set_setting AudioOutput "$CARD"
  # 1 = jack, 2 = HDMI on the bcm2835 driver; harmless if the control is absent
  run "amixer -c $CARD cset numid=3 1 >/dev/null 2>&1 || true"
  run "amixer -c $CARD sset PCM unmute >/dev/null 2>&1 || true"
else
  say "   !! no onboard audio card found."
  say "      If you just enabled dtparam=audio=on, reboot and re-run me."
  say "      Otherwise set Status/Control -> Audio Output by hand in the FPP UI."
fi
set_setting volume 70

# --------------------------------------------------------------------------
step "3. DDP output to the controller"
backup "$CO"
PY=$(command -v python3 || true)
if [[ -z "$PY" ]]; then
  echo "   python3 not found; cannot edit $CO safely." >&2
  exit 1
fi
CO_NEW=$("$PY" - "$CO" "$CONTROLLER_IP" "$CHANNELS" "$DESC" <<'PYEOF'
import json, os, sys
path, ip, channels, desc = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
try:
    with open(path) as fh:
        cfg = json.load(fh)
except Exception:
    cfg = {}
outs = cfg.setdefault("channelOutputs", [])
blk = next((o for o in outs if o.get("type") == "universes"), None)
if blk is None:
    blk = {"type": "universes", "enabled": 1, "startChannel": 1,
           "channelCount": -1, "universes": []}
    outs.append(blk)
blk["enabled"] = 1
unis = blk.setdefault("universes", [])
# DDP is universe type 4 in FPP's network-output list
entry = {"active": 1, "description": desc, "id": 1, "startChannel": 1,
         "type": 4, "address": ip, "channelCount": channels,
         "priority": 0, "monitor": 1, "deDuplicate": 0}
for u in unis:
    if u.get("address") == ip or u.get("description") == desc:
        u.update(entry)
        break
else:
    unis.append(entry)
print(json.dumps(cfg, indent=2))
PYEOF
)
if [[ -f "$CO" ]] && [[ "$(cat "$CO")" == "$CO_NEW" ]]; then
  say "   $CO already correct"
else
  say "   $CO: DDP -> $CONTROLLER_IP, channels 1..$CHANNELS"
  if [[ $APPLY -eq 1 ]]; then
    mkdir -p "$(dirname "$CO")"
    printf '%s\n' "$CO_NEW" > "$CO"
    chown fpp:fpp "$CO" 2>/dev/null || true
  else
    say "   --- would write ---"
    printf '%s\n' "$CO_NEW" | sed 's/^/   /'
  fi
fi
say "   confirm in the UI at Input/Output Setup -> Channel Outputs -> Network"
say "   that the row reads DDP (FPP has renumbered these types between releases)"

# --------------------------------------------------------------------------
step "4. restart"
if [[ $RESTART -eq 1 ]]; then
  run "systemctl restart fppd || /opt/fpp/scripts/fppd_start"
else
  say "   skipped (--no-restart)"
fi

step "done"
if [[ $APPLY -eq 0 ]]; then
  say "   nothing was written. Re-run with --apply."
else
  say "   hotspot SSID     $SSID"
  AP_IP=$(ip -4 addr show 2>/dev/null | sed -n 's/.*inet \([0-9.]*\).*wlan.*/\1/p' | head -1 || true)
  say "   this Pi's AP IP  ${AP_IP:-(check \`ip addr\`)}"
  say "   put that address in helmet.toml under [player] host"
  [[ "${NEEDS_REBOOT:-0}" == "1" ]] && say "   REBOOT REQUIRED for the audio change to take effect"
fi
