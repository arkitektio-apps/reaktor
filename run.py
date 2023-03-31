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

    @app.rekuest.register(
        widgets={"description": StringWidget(as_paragraph=True)},
        interfaces=["fluss:deploy"],
    )
    async def deploy_graph(
        flow: FlowFragment,
        name: str = None,
        description: str = None,
    ) -> TemplateFragment:
        """Deploy Flow

        Deploys a Flow as a Template

        Args:
            graph (FlowFragment): The Flow
            name (str, optional): The name of this Incarnation
            description (str, optional): The name of this Incarnation

        Returns:
            TemplateFragment: The created template
        """
        assert flow.name, "Graph must have a Name in order to be deployed"

        print([x.dict(by_alias=True) for x in flow.graph.args])
        print([x.dict(by_alias=True) for x in flow.graph.returns])

        args = [PortInput(**x.dict(by_alias=True)) for x in flow.graph.args]
        returns = [PortInput(**x.dict(by_alias=True)) for x in flow.graph.returns]

        template = await acreate_template(
            DefinitionInput(
                name=name or flow.workspace.name,
                interface=f"flow-{flow.id}",
                kind=infer_kind_from_graph(flow.graph),
                args=args,
                returns=returns,
                description=description,
                interfaces=[
                    "workflow",
                    f"diagram:{flow.workspace.id}",
                    f"flow:{flow.id}",
                ],
            ),
            instance_id=app.rekuest.agent.instance_id,
            params={"flow": flow.id},
            extensions=["flow"],
        )

        return template

    @app.rekuest.register()
    async def undeploy_graph(
        flow: FlowFragment,
    ):
        """Undeploy Flow

        Undeploys graph, no user will be able to reserve this graph anymore

        Args:
            graph (FlowFragment): The Flow

        """
        assert flow.name, "Graph must have a Name in order to be deployed"

        x = await afind(interface=flow.hash)

        await adelete_node(x)
        return None

    @app.rekuest.register(widgets={"interval": SliderWidget(min=0, max=100)})
    async def timer(interval: int = 4) -> int:
        """Timer

        A simple timer that prints the current time every interval seconds

        Args:
            interval (int, optional): The interval in seconds. Defaults to 4.

        Returns:
            int: The current interval (iteration)

        """
        i = 0
        while True:
            i += 1
            yield i
            await asyncio.sleep(interval)

    async with app:
        await app.rekuest.run()


@click.command()
@click.option("--token", type=click.STRING, envvar="FAKT_TOKEN", required=True)
@click.option("--url", type=click.STRING, envvar="FAKT_URL", required=True)
@click.option(
    "--instance", type=click.STRING, default=socket.gethostname(), required=True
)
def cli(token, url, instance):
    asyncio.run(main(token, url, instance))


if __name__ == "__main__":
    cli()
