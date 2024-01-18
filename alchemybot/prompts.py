import os

# Get path to current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Create path to prompts directory
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

PROMPTS = {}
# read each file in "prompts" folder
for filename in os.listdir(PROMPTS_DIR):
    with open(os.path.join(PROMPTS_DIR, filename), "r") as f:
        # add each prompt to the PROMPTS dict
        PROMPTS[filename] = f.read()
