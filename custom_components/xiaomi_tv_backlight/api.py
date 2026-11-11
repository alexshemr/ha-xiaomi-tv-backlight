"""Local API client for Xiaomi TV Backlight Control."""
import asyncio
from aiohttp import ClientSession
from yarl import URL

class BacklightApi:
    def __init__(self, session: ClientSession, host: str, token: str = "") -> None:
        url = URL(host if "://" in host else f"http://{host}:8765")
        if url.scheme not in ("http", "https") or not url.host or url.user or url.path not in ("", "/"):
            raise ValueError("Enter a hostname, IP address or local API URL")
        self.base = str(url).rstrip("/")
        self.session = session
        self.token = token

    async def request(self, method: str, path: str, body: str | None = None) -> dict:
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        async with asyncio.timeout(4):
            async with self.session.request(method, self.base + path, data=body, headers=headers) as response:
                response.raise_for_status()
                value = await response.json()
                if not isinstance(value, dict):
                    raise ValueError("Invalid response")
                return value

    async def info(self) -> dict:
        value = await self.request("GET", "/info")
        if not isinstance(value.get("id"), str) or not value["id"] or value.get("api") != 1:
            raise ValueError("Unsupported TV API")
        return value

    async def read(self) -> int:
        value = (await self.request("GET", "/backlight")).get("level")
        if type(value) is not int or not 0 <= value <= 100:
            raise ValueError("Invalid backlight level")
        return value

    async def write(self, value: int) -> int:
        if type(value) is not int or not 0 <= value <= 100:
            raise ValueError("Backlight must be an integer from 0 to 100")
        result = (await self.request("PUT", "/backlight", str(value))).get("level")
        if type(result) is not int or not 0 <= result <= 100:
            raise ValueError("Invalid backlight response")
        return result

    async def pair(self, code: str) -> str:
        value = (await self.request("POST", "/pair", code)).get("token")
        if not isinstance(value, str) or len(value) < 32:
            raise ValueError("Invalid pairing response")
        return value
