import asyncio
from aiko import App

loop = asyncio.get_event_loop()
app = App(loop)

def hello(ctx, next_call):
    if ctx.request.path == "/":
        yield "Hello, World!"
    elif ctx.request.path == "/test":
        amin = ctx.cookies.get("amin") or 0
        ctx.cookies["amin"] = str(int(amin) + 1)
        yield "test cookie"
    elif ctx.request.path == "/del":
        del ctx.cookies["amin"]
        yield "del amin"
    else:
        yield next_call()

def not_found(ctx, next_call):
    ctx.response.status = 404
    ctx.response.length = 9
    ctx.response.set("Content-Type", "text/plain")
    return b"Not Found"

app.use(hello)
app.use(not_found)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
