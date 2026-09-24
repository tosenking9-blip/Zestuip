# -*- coding: utf-8 -*-
"""Safe match-control state for the Zesty dashboard.
This module manages only the dashboard's own match simulation/state.
It does not inject packets into third-party game clients.
"""
import json, os, threading, time, uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "match_state.json")
_lock = threading.RLock()

DEFAULT = {
    "match_id": "ZESTY-DEMO",
    "mode": "battle_royale",
    "running": False,
    "paused": False,
    "players": {},
    "updated_at": 0
}

def _load():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            x=json.load(f)
        return x if isinstance(x,dict) else dict(DEFAULT)
    except Exception:
        return dict(DEFAULT)

def _save(s):
    s["updated_at"]=int(time.time())
    tmp=STATE_FILE+".tmp"
    with open(tmp,"w",encoding="utf-8") as f: json.dump(s,f,indent=2)
    os.replace(tmp,STATE_FILE)

def snapshot():
    with _lock: return _load()

def set_mode(mode):
    mode=str(mode).lower()
    if mode not in ("lone_wolf","battle_royale","mix"):
        raise ValueError("invalid mode")
    with _lock:
        s=_load(); s["mode"]=mode; _save(s); return s

def set_running(running):
    with _lock:
        s=_load(); s["running"]=bool(running); _save(s); return s

def set_paused(paused):
    with _lock:
        s=_load(); s["paused"]=bool(paused); _save(s); return s

def upsert_player(name, x=0, y=0, z=0):
    with _lock:
        s=_load()
        pid=str(name).strip()[:64] or uuid.uuid4().hex[:8]
        p=s["players"].setdefault(pid, {"x":0.0,"y":0.0,"z":0.0,"alive":True})
        p.update({"x":float(x),"y":float(y),"z":float(z)})
        _save(s); return pid,p,s

def move_player(name, dx=0, dy=0, dz=0):
    with _lock:
        s=_load(); pid=str(name)
        if pid not in s["players"]: raise KeyError("player not found")
        p=s["players"][pid]
        p["x"]+=float(dx); p["y"]+=float(dy); p["z"]+=float(dz)
        _save(s); return s

def teleport_player(name, x, y, z):
    # Dashboard-only simulation teleport. No third-party client packet is emitted.
    with _lock:
        s=_load(); pid=str(name)
        if pid not in s["players"]: raise KeyError("player not found")
        s["players"][pid].update({"x":float(x),"y":float(y),"z":float(z)})
        _save(s); return s

def remove_player(name):
    with _lock:
        s=_load(); s["players"].pop(str(name),None); _save(s); return s

def clear_players():
    with _lock:
        s=_load(); s["players"]={}; _save(s); return s
