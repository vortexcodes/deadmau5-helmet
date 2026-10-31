global.window = global;
const S = require('/Users/jones/deadmau5 app/remote/offline/spotify.js');
const names = ["Fred again.. & Baby Keem - leavemealone","TIKI TIKI - Slowed","beneath (with raxaj)","deadmau5 - Ghosts n Stuff (Nero Remix)","deadmau5 - Strobe","deadmau5 - Strobe (Dimension Remix)",
 "deadmau5 - Harder Better Faster Stronger","Kaskade feat. deadmau5 - I Remember","deadmau5 - FN Pig","deadmau5 - Moar Ghosts n Stuff","deadmau5 - Raise Your Weapon","deadmau5 - Some Chords","deadmau5 - Some Chords (Radio Edit)","deadmau5 & Wolfgang Gartner - Animal Rights","deadmau5 - The Veldt","deadmau5 - Strobe (Special Features Remix)"];
const shows = {}; for (const n of names) shows[n] = {};
const dl = {
 "Deadmau5_-_12_Harder_Better_Faster_Stronger_Deadmau5_Rmx_Amsterdam_Dance_Event_10-23-2009_(mp3.pm).mp3":"deadmau5 - Harder Better Faster Stronger",
 "Kaskade_feat._Deadmau5_-_I_Remember_(mp3.pm).mp3":"Kaskade feat. deadmau5 - I Remember",
 "Deadmau5_-_Fn_Pig_(mp3.pm).mp3":"deadmau5 - FN Pig",
 "Deadmau5_-_Moar_Ghosts_n_STuff_(mp3.pm).mp3":"deadmau5 - Moar Ghosts n Stuff",
 "Deadmau5_-_Raise_Your_Weapon_(mp3.pm).mp3":"deadmau5 - Raise Your Weapon",
 "Deadmau5_-_Some_Chords_(mp3.pm).mp3":"deadmau5 - Some Chords",
 "Deadmau5_-_Some_Chords_Radio_Edit_(mp3.pm).mp3":"deadmau5 - Some Chords (Radio Edit)",
 "Deadmau5_Wolfgang_Gartner_-_Animal_Rights_(mp3.pm).mp3":"deadmau5 & Wolfgang Gartner - Animal Rights",
 "Deadmau5_-_The_Veldt_(mp3.pm).mp3":"deadmau5 - The Veldt",
 "Deadmau5_-_Strobe_Special_Features_Remix_(mp3.pm).mp3":"deadmau5 - Strobe (Special Features Remix)",
};
let bad = 0;
for (const n of names) { const g = S.showForFile(n + '.mp3', shows); if (g !== n) { bad++; console.log('SAVED NAME', n, '->', g); } }
for (const [f, want] of Object.entries(dl)) { const g = S.showForFile(f, shows); if (g !== want) { bad++; console.log('DOWNLOAD NAME', f, '->', g); } }
// the phone often appends " (1)" or renames spaces to underscores on save
for (const n of names) { for (const v of [n + ' (1).mp3', n.replace(/ /g, '_') + '.mp3']) { const g = S.showForFile(v, shows); if (g !== n) { bad++; console.log('VARIANT', v, '->', g); } } }
// and Spotify's way of naming them
for (const [t, a, want] of [['Some Chords', ['deadmau5'], 'deadmau5 - Some Chords'], ['Some Chords - Radio Edit', ['deadmau5'], 'deadmau5 - Some Chords (Radio Edit)'], ['Strobe', ['deadmau5'], 'deadmau5 - Strobe'], ['The Veldt', ['deadmau5', 'Chris James'], 'deadmau5 - The Veldt'], ['I Remember', ['deadmau5', 'Kaskade'], 'Kaskade feat. deadmau5 - I Remember'], ['Animal Rights', ['deadmau5', 'Wolfgang Gartner'], 'deadmau5 & Wolfgang Gartner - Animal Rights'], ['Raise Your Weapon', ['deadmau5'], 'deadmau5 - Raise Your Weapon'], ['FML', ['deadmau5'], null], ['Ghosts \'n\' Stuff', ['deadmau5', 'Rob Swire'], null], ['Harder, Better, Faster, Stronger', ['Daft Punk'], null]]) {
  const h = S.bestShow(t, a, shows); console.log('spotify', JSON.stringify(t), '->', h && h.name, h && h.score.toFixed(2), want && h && h.name !== want ? 'WRONG' : '');
}
console.log('bad', bad);
