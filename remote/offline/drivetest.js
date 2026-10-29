// drivetest.js -- read a drive file under node and dump what the show
// would see, so test_mau5.py can compare it with mau5show.Music.
'use strict';
const fs = require('fs');
const D = require('./drive.js');

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', c => { raw += c; });
process.stdin.on('end', () => {
  const job = JSON.parse(raw);
  const buf = fs.readFileSync(job.file);
  const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
  const d = new D.TrackDrive(ab);
  const out = { duration: d.duration, bpm: d.bpm, beats: d.beats.length,
                bars: d.bars.length, rows: [] };
  for (const t of job.times) {
    out.rows.push({
      t,
      level: d.levelAt(t),
      bass: d.bandAt(t, 'bass', false),
      bassP: d.bandAt(t, 'bass', true),
      high: d.bandAt(t, 'high', false),
      phase: d.beatPhase(t),
      index: d.beatIndex(t),
      down: d.isDownbeat(t),
      pitch: d.pitchAt(t),
    });
  }
  process.stdout.write(JSON.stringify(out));
});
