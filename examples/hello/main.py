import asyncio
from aiokoa import App

loop = asyncio.get_event_loop()
app = App(loop)

def hello(ctx, next_call):
    return "Hello, World!"

app.use(hello)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
