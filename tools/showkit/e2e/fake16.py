# The fake controller answering as WLED 16: binary DDP frames, counted and kept. Never touches the helmet.
import json, sys, time, os
os.chdir("/Users/jones/deadmau5 app")
sys.path.insert(0, ".")
import numpy as np, mau5fake
orig_info = mau5fake.Fake.info
orig_take = mau5fake.Fake.take
LOG = open(sys.argv[1], "w", buffering=1) if len(sys.argv) > 1 else None
buf = np.zeros(622 * 3, np.uint8)
n = [0, time.time(), 0]
def info(self):
    d = orig_info(self); d["ver"] = "16.0.1"; d["vid"] = 2606300; return d
def take(self, m):
    if m[:1] == b"\xff":
        return
    if m[:1] == b"\x02":
        off = int.from_bytes(m[5:9], "big"); ln = int.from_bytes(m[9:11], "big")
        buf[off:off + ln] = np.frombuffer(m[11:11 + ln], np.uint8)
        self.stats["ddp"] = self.stats.get("ddp", 0) + 1
        if m[1] & 1:
            n[0] += 1
            s = int(buf.sum())
            self.stats["frames"] = n[0]
            self.stats["lit"] = s
            now = time.time()
            if now - n[1] >= 0.5:
                if LOG:
                    LOG.write("%.2f frames=%d rate=%.1f lit=%d\n" % (now, n[0], (n[0] - n[2]) / (now - n[1]), s))
                n[1] = now; n[2] = n[0]
        return
    return orig_take(self, m)
mau5fake.Fake.info = info
mau5fake.Fake.take = take
mau5fake.serve(port=8770)
