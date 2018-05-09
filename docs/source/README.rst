aiko
======

aiko is a base asyncio's lightweight web application framework.
It is designed to make `koa`_ api.

Installing
----------

Install by code

.. code-block:: text

    $ git clone https://github.com/zeromake/aiko
    $ cd aiko
    $ python setup.py install

A Simple Example
----------------

.. code-block:: python

    import asyncio
    from aiko import App

    loop = asyncio.get_event_loop()
    app = App(loop)

    def hello(ctx, next_call):
        return "Hello, World!"

    app.use(hello)

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)

.. code-block:: text

    $ curl http://127.0.0.1:5000
    Hello, World!

Links
-----

.. _koa: https://github.com/koajs/koa

Todo
----

- [ ] request api like koa
    - [ ] method
        - [ ] `accepts`
        - [ ] `acceptsEncodings` -> `accepts_encodings`
        - [ ] `acceptsCharsets` -> `accepts_charsets`
        - [ ] `acceptsLanguages` -> `accepts_languages`
        - [ ] `is`
        - [x] `get`
    - [ ] getter, setter
        - [x] `header`
            - [x] getter
            - [ ] setter
        - [x] `headers`
            - [x] getter
            - [ ] setter
        - [x] `url`
        - [x] `origin`
        - [x] `href`
        - [x] `method`
        - [x] `path`
        - [x] `query`
        - [x] `querystring`
        - [x] `search`
    - [ ] getter
        - [x] `host`
        - [x] `hostname`
        - [ ] `URL`
        - [x] `fresh`
        - [x] `stale`
        - [x] `idempotent`
        - [x] `socket`
        - [x] `charset`
        - [x] `length`
        - [x] `protocol`
        - [x] `secure`
        - [x] `ips`
        - [ ] `subdomains`
        - [x] `type`
        - [x] `originalUrl` -> `original_url`
        - [x] `ip`
- [ ] response api like koa
- [x] proxy class property attr and method
- [x] like `fresh <https://github.com/jshttp/fresh>`_ method
