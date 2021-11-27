# An Agent Based Artificial Market

## Running the Model

To run and interact with the model, run `analysis.ipynb` through Jupyter Notebook or a similiar Notebook viewer.

All logic is contained in `market.py`, `agent.py` and `model.py`, with `model.py` providing a method for initializing the model, view the notebook for example usage.

## Usage
```python
from model import MarketModel

# Parameterise the model (View the notebook for example parameters)

# Initialize the model
model = MarketModel(steps=timesteps, agents=agents, non_random=non_random, 
                    price=price, alpha=alpha,
                    beta=beta, gamma=gamma, rho=rho, 
                    network=network, convergence=convergence)

# Run the model
model.run()
```

### Dependencies (Python Packages)
- mesa
- networkx
- statsmodels
- numpy, pandas, matplotlib
