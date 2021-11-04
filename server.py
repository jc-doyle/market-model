from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from model import MarketModel
from agent import Type


def agent_portrayal(agent):
    portrayal = {"Shape": "circle", "Filled": "true", "Layer": 1, "r": 0.5}

    if agent.type == Type.OPTIMIST:
        portrayal["Color"] = "red"
    if agent.type == Type.PESSIMIST:
        portrayal["Color"] = "green"
    if agent.type == Type.RANDOM:
        portrayal["Color"] = "grey"

    return portrayal


chart = ChartModule([{"Label": "Price", "Color": "Black"}], data_collector_name='data')

grid = CanvasGrid(agent_portrayal, 10, 10, 400, 400)
model_params = {"agents": 100, "price": 50}

server = ModularServer(
    MarketModel,
    [grid, chart],
    "Market Model",
    model_params=model_params,
)

server.port = 8521  # The default
server.launch()
