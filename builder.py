from reaktion.agent import ReaktionAgent
from rekuest.contrib.fakts.websocket_agent_transport import FaktsWebsocketAgentTransport


from arkitekt.apps.fluss import FlussApp
from arkitekt.apps.unlok import UnlokApp
from arkitekt.apps.rekuest import ArkitektRekuest, RekuestApp
from arkitekt.apps import Arkitekt
from fakts.grants.remote.device_code import DeviceCodeGrant
from fakts.fakts import Fakts
from fakts.grants import CacheGrant
from herre.grants import CacheGrant as HerreCacheGrant
from herre.grants.oauth2.refresh import RefreshGrant
from herre.grants.fakts import FaktsGrant
from fakts.discovery import StaticDiscovery
from herre import Herre
from arkitekt.apps.fluss import ConnectedFluss
import logging
from rich.logging import RichHandler

class ConnectedApp(Arkitekt, FlussApp):
    pass


def hello(identifier="fluss", version="latest", url="http://localhost:8000/f/"):
    print("hello")
    app = ConnectedApp(
        identifier=identifier,
        version=version,
        fakts=Fakts(
            grant=CacheGrant(
                cache_file=f"{identifier}-{version}_cache.json",
                hash=f"{identifier}-{version}-{url}",
                grant=DeviceCodeGrant(
                    identifier=identifier,
                    version=version,
                    discovery=StaticDiscovery(base_url=url),
                ),
            )
        ),
        herre=Herre(
            grant=HerreCacheGrant(
                cache_file=f"{identifier}-{version}_herre_cache.json",
                hash=f"{identifier}-{version}-{url}",
                grant=RefreshGrant(grant=FaktsGrant()),
            ),
        ),
        rekuest=ArkitektRekuest(
            agent=ReaktionAgent(
                transport=FaktsWebsocketAgentTransport(fakts_group="rekuest.agent")
            )
        ),
    )
    return app