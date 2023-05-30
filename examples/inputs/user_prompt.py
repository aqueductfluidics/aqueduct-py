"""
User Prompt Demo

This module demonstrates the usage of the Aqueduct library 
for displaying prompts and controlling recipe execution
with and without pausing. The demo shows how to use the 
Aqueduct `prompt` function to display messages and control
the recipe flow based on user input.

The demo consists of two prompts. The first prompt (`testing with pause`)
pauses the recipe execution until the user
interacts with it, allowing the user to proceed by pressing a
continue button. The second prompt (`testing without pause`)
displays the message without pausing the recipe execution. 
The demo also demonstrates how to use a while loop to wait
for user input while the prompt is being displayed.
"""
import time
from aqueduct.core.aq import Aqueduct

aq = Aqueduct()
aq.initialize()

p = aq.prompt(
    message="testing with pause",
    pause_recipe=True,
)

p = aq.prompt(
    message="testing without pause",
    pause_recipe=False,
)

while p:
    print("Waiting...")
    time.sleep(.1)
