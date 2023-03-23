import asyncio
from arkitekt import register
from rekuest.api.schema import (
    PortInput,
    DefinitionInput,
    TemplateFragment,
    acreate_template,
    adelete_node,
    afind,
)

from fluss.api.schema import FlowFragment

from rekuest.widgets import SliderWidget, StringWidget
from reaktion.utils import infer_kind_from_graph


@register(
    widgets={"description": StringWidget(as_paragraph=True)},
    interfaces=["fluss:deploy"],
)
async def deploy_graph(
    flow: FlowFragment,
    name: str = None,
    description: str = None,
) -> TemplateFragment:
    """Deploy Flowd

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
            interfaces=["workflow", f"diagram:{flow.workspace.id}", f"flow:{flow.id}"],
        ),
        params={"flow": flow.id},
        extensions=["flow"],
    )

    return template


@register()
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


@register(widgets={"interval": SliderWidget(min=0, max=100)})
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

