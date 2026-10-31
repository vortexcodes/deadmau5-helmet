# WLED 16.0.1, patched to keep its access point up

Official WLED 16.0.1 tears down its own access point whenever it retries the
home network. With the home network out of range, that is every 18 s with
nobody on the access point and every 5 minutes with a phone on it, and every
phone on it is dropped each time. WLED 0.15 left the access point alone. The
current upstream code does the same as 16.0.1.

`wled-16.0.1-keep-access-point.patch` changes two things in `wled00/wled.cpp`:

- A retry no longer tears down an access point that is set to always on.
- Nothing looks for the home network while somebody is on the access point. The
  search starts again when the last one leaves.

Everything else is the official `esp32_eth` build, which is what the helmet's
GLEDOPTO controller runs.

## Rebuild

```bash
git clone --depth 1 --branch v16.0.1 https://github.com/wled/WLED.git
cd WLED
git apply "/path/to/firmware/wled-16.0.1-keep-access-point.patch"
pio run -e esp32_eth
```

The result is `build_output/release/WLED_16.0.1_ESP32_Ethernet.bin`, about two
minutes after the first run's downloads. The built file is kept locally in this
folder and is not committed.

## Flash, and flash back

Over the air, with the page stopped. Settings are kept. To go back, send the
official `WLED_16.0.1_ESP32_Ethernet.bin` from the WLED releases page the same way.

```bash
curl -F "update=@firmware/WLED_16.0.1_ESP32_Ethernet_keep-ap.bin" http://192.168.10.172/update
```
