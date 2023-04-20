import asyncio
from reaktion.agent import ReaktionAgent
from rekuest.contrib.fakts.websocket_agent_transport import FaktsWebsocketAgentTransport
from rekuest.api.schema import (
    PortInput,
    DefinitionInput,
    TemplateFragment,
    acreate_template,
    adelete_node,
    afind,
)
from fakts.fakts import Fakts
from fluss.api.schema import (
    FlowFragment,
)
import socket
from rekuest.widgets import SliderWidget, StringWidget
from arkitekt.apps.fluss import FlussApp
from arkitekt.apps.unlok import UnlokApp
from arkitekt.apps.rekuest import ArkitektRekuest, RekuestApp
from reaktion.utils import infer_kind_from_graph
from fakts.fakts import Fakts
from fakts.grants.remote.static import StaticGrant
from fakts.discovery.well_known import WellKnownDiscovery
from herre.grants.oauth2.refresh import RefreshGrant
from herre.grants.fakts import FaktsGrant
from herre import Herre
import logging
from rich.logging import RichHandler
import rich_click as click
import logging

logging.basicConfig(level="INFO", handlers=[RichHandler()])


class ConnectedApp(FlussApp, RekuestApp, UnlokApp):
    pass


async def main(token, url, instance):
    app = ConnectedApp(
        fakts=Fakts(
            grant=StaticGrant(
                token=token,
                discovery=WellKnownDiscovery(url=url),
            ),
        ),
        herre=Herre(
            grant=RefreshGrant(grant=FaktsGrant()),
        ),
        rekuest=ArkitektRekuest(
            agent=ReaktionAgent(
                instance_id=instance,
                transport=FaktsWebsocketAgentTransport(fakts_group="rekuest.agent"),
            )
        ),
    )

    async with app:
        await app.rekuest.run()


@click.command()
@click.option("--token", type=click.STRING, envvar="FAKTS_TOKEN", required=True)
@click.option("--url", type=click.STRING, envvar="FAKTS_URL", required=True)
@click.option(
    "--instance", "-i", help="The fakts instance_id for connection", default="main", envvar="REKUEST_INSTANCE",
)
def cli(token, url, instance):
    asyncio.run(main(token, url, instance))


if __name__ == "__main__":
    cli()
