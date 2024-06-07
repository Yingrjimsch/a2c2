from oxen.datasets import download
from oxen.auth import config_auth
import json
import os
prompts = None
config_auth("SFMyNTY.g2gDbQAAAC9hcGlfa2V5X3YxOjc1N2VhMTJjLWIyOWYtNGE5Ni04ZDhlLTE1YTIyOWRkN2NiOG4GAEA4ZoqPAWIAAVGA.U7KlA902eCE4G3DWhZNF0l3LM0Ld0cHLx2t45vhjjvE") # do not push this to github
if not os.path.exists("prompts.json"):
    f = download("Yingrjimsch/a2c2_prompts", "prompts.json", revision="main")
with open("prompts.json", "r") as f:
    prompts = json.load(f)