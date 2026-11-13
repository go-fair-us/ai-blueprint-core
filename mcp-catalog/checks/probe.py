#!/usr/bin/env python3
"""Harmless MCP probe: initialize + tools/list over Streamable HTTP. No auth."""
import json, sys, urllib.request, urllib.error
def post(url, body, sid=None):
    h={"Content-Type":"application/json","Accept":"application/json, text/event-stream","MCP-Protocol-Version":"2025-06-18"}
    if sid: h["Mcp-Session-Id"]=sid
    req=urllib.request.Request(url,data=json.dumps(body).encode(),headers=h,method="POST")
    try:
        with urllib.request.urlopen(req,timeout=25) as r:
            txt=r.read().decode("utf-8","replace"); return r.status, r.headers.get("Mcp-Session-Id"), txt
    except urllib.error.HTTPError as e:
        return e.code, None, e.read().decode("utf-8","replace")[:300]
    except Exception as e:
        return None, None, str(e)[:200]
def parse(txt):
    for line in txt.splitlines()[::-1]:
        if line.startswith("data:"):
            try: return json.loads(line[5:])
            except: pass
    try: return json.loads(txt)
    except: return None
out={}
for url in sys.argv[1:]:
    st,sid,txt=post(url,{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"catalog-probe","version":"0.1"}}})
    r=parse(txt) if st==200 else None
    info=(r or {}).get("result",{}).get("serverInfo")
    tools=None
    if st==200:
        post(url,{"jsonrpc":"2.0","method":"notifications/initialized"},sid)
        st2,_,txt2=post(url,{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}},sid)
        r2=parse(txt2)
        if r2 and "result" in r2: tools=[t["name"] for t in r2["result"].get("tools",[])]
    out[url]={"status":st,"serverInfo":info,"tools":tools,"err":None if st==200 else txt[:200]}
    print(url, st, info, (len(tools) if tools is not None else None), (tools or [])[:60] if tools else txt[:160].replace("\n"," ") if st!=200 else "", flush=True)
json.dump(out,open("/workspace/mcp-catalog/checks/probe-results.json","a"),indent=1)
