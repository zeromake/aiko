import asyncio
from aiko import App

loop = asyncio.get_event_loop()
app = App(loop)

def hello(ctx, next_call):
    if ctx.request.path == "/":
        return "Hello, World!"
    elif ctx.request.path == "/test":
        amin = ctx.cookies.get("amin") or 0
        ctx.cookies["amin"] = str(int(amin) + 1)
        return "test cookie"
    else:
        del ctx.cookies["amin"]
        return "del amin"


app.use(hello)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
