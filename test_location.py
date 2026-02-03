from clawcity.core.models import Scene, Episode, DialogueLine
from src.prompt_builder import build_image_prompt

# Setup test data with a scene in the Cafe
current_scene = Scene(id=5, title="Ginas Morgen", location="Café Gemütlich", time="Morgen", duration="10s", 
                      image_prompt="Gina is drinking a latte",
                      dialogue=[DialogueLine(character="Gina", text="This coffee is better than my battery pack.")])

# Test
prompt = build_image_prompt(current_scene, [])

print("--- STABILIZED LOCATION PROMPT (CAFE) ---")
print(prompt)
print("-----------------------------------------")
