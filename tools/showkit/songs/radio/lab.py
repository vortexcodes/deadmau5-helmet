"""lab.py: try raw layers on the helmet without touching the show. Used from small scripts."""
import sys, os, json
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E, mau5preview as PV, mau5scene as S, mau5show
from PIL import Image, ImageDraw
BASE="deadmau5 - Some Chords (Radio Edit)"
_h=None;_sc=None;_music=None
def env():
    global _h,_sc,_music
    if _h is None:
        _h=E.Helmet(); _sc=PV.Scene(_h)
        show=json.load(open("shows/%s.json"%BASE))
        _music=mau5show._music_for(show,"shows/%s.mp3"%BASE)
    return _h,_sc,_music
GRID={"t0":0.124,"spb":0.46875,"holds":[]}
def tof(bar):
    t=0.124+4*bar*0.46875
    return t+0.032 if t>=135.1 else t
def sheet(tiles,palettes,out,cols=6,w=300,hh=245):
    """tiles: list of (label, bar, from_bar, to_bar, layers)"""
    h,sc,music=env()
    rows=(len(tiles)+cols-1)//cols
    o=Image.new("RGB",(cols*w,rows*hh),(0,0,0)); d=ImageDraw.Draw(o)
    for k,(lab,bar,b0,b1,layers) in enumerate(tiles):
        tr={"v":1,"show":BASE,"marks":{},"palettes":palettes,"motifs":{},"scenes":[{"name":"x","from":b0,"to":b1,"layers":layers}],"hits":[]}
        spec=S.compile_treatment(tr,{"t0":0.124,"spb":0.46875},112,h)
        s=S.Scenes(spec,h)
        f,g,l=s.frame(tof(bar),music)
        im=sc.frame(f*g).crop((60,40,700,560)).resize((w,hh))
        o.paste(im,((k%cols)*w,(k//cols)*hh))
        d.text(((k%cols)*w+5,(k//cols)*hh+3),lab,fill=(255,255,255))
    o.save(out); print(out,o.size)
