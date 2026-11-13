#!/usr/bin/env python3
"""Spawn a stdio MCP server, initialize, list tools, exit. Usage: probe_stdio.py -- cmd args..."""
import json, subprocess, sys, select, time
cmd=sys.argv[sys.argv.index("--")+1:]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,bufsize=1)
def send(o): p.stdin.write(json.dumps(o)+"\n"); p.stdin.flush()
def recv(want_id,timeout=240):
    end=time.time()+timeout
    while time.time()<end:
        r,_,_=select.select([p.stdout],[],[],1)
        if r:
            line=p.stdout.readline()
            if not line: return None
            try: o=json.loads(line)
            except: continue
            if o.get("id")==want_id: return o
    return None
send({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"catalog-probe","version":"0.1"}}})
r=recv(1)
print("INIT", json.dumps((r or {}).get("result",{}).get("serverInfo")))
send({"jsonrpc":"2.0","method":"notifications/initialized"})
send({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})
r=recv(2)
print("TOOLS", json.dumps([t["name"] for t in (r or {}).get("result",{}).get("tools",[])]))
p.kill()
