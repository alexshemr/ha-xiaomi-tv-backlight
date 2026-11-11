"""Exercise the HTTP client against a real local HTTP server."""
import importlib.util
from pathlib import Path
import unittest
from aiohttp import web, ClientSession

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tv_api", root / "custom_components/xiaomi_tv_backlight/api.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.level = 40
        self.invalid = False
        async def endpoint(request):
            if request.path == "/info":
                return web.json_response({"id": "test-tv", "model": "Xiaomi", "api": 1})
            if request.path == "/pair":
                return web.json_response({"token": "x"*36}) if await request.text() == "123456" else web.Response(status=403)
            if request.headers.get("Authorization") != "Bearer test-token":
                return web.Response(status=401)
            if request.method == "PUT":
                self.level = int(await request.text())
            return web.json_response({"level": True if self.invalid else self.level})
        app = web.Application()
        app.router.add_route("*", "/{path}", endpoint)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "127.0.0.1", 0)
        await site.start()
        port = self.runner.addresses[0][1]
        self.session = ClientSession()
        self.api = module.BacklightApi(self.session, f"http://127.0.0.1:{port}", "test-token")

    async def asyncTearDown(self):
        await self.session.close()
        await self.runner.cleanup()

    async def test_read_write_bounds(self):
        self.assertEqual(await self.api.read(), 40)
        self.assertEqual(await self.api.write(0), 0)
        self.assertEqual(await self.api.write(100), 100)
        for value in (-1, 101, True, 4.5):
            with self.assertRaises(ValueError):
                await self.api.write(value)
        self.assertEqual(await self.api.read(), 100)

    async def test_invalid_response(self):
        self.invalid = True
        with self.assertRaises(ValueError):
            await self.api.read()

    async def test_pair_info(self):
        self.assertEqual((await self.api.info())["id"], "test-tv")
        self.assertEqual(await self.api.pair("123456"), "x"*36)
        from aiohttp import ClientResponseError
        with self.assertRaises(ClientResponseError):
            await self.api.pair("000000")

    async def test_auth_required(self):
        self.api.token = ""
        from aiohttp import ClientResponseError
        with self.assertRaises(ClientResponseError):
            await self.api.read()

if __name__ == "__main__":
    unittest.main()
