"""
User Input Demo

This module demonstrates the usage of the Aqueduct library 
for interactive user prompts and input handling. The demo
shows how to use the Aqueduct `input` function to prompt the 
user for input, pause the recipe execution, and retrieve
the input values.

The demo consists of two input prompts. The first prompt 
(`testing 1`) pauses the recipe execution until the user provides
an input value. The second prompt (`testing 2`) allows the 
recipe execution to continue without pausing. The demo also
illustrates how to check if an input value has been set and 
retrieve the input values using the `get_value` method.
"""
import time
from aqueduct.core.aq import Aqueduct

# Initialize Aqueduct
aq = Aqueduct()
aq.initialize()

# Prompt for input 1
p = aq.input(
    message="testing 1",
    pause_recipe=True,
    dtype=str.__name__,
)

# Get the value of input 1
v = p.get_value()
print(f"Input 1: {v}")

# Prompt for input 2
p = aq.input(
    message="testing 2",
    pause_recipe=False,
    dtype=str.__name__,
)

# Wait until input 2 is set
while not p.is_set():
    print(f"Input 1 value still: {v}")
    time.sleep(1)

# Get the value of input 2
v = p.get_value()
print(f"Input 2: {v}")
