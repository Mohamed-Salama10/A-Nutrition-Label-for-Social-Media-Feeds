# !pip install -q -U transformers==4.37.2
# !pip install -q bitsandbytes==0.41.3 accelerate==0.25.0

import requests
from PIL import Image
from transformers import pipeline

def image_to_text_similarity(image_url, prompt):
    image = Image.open(requests.get(image_url, stream=True).raw)
    model_id = "llava-hf/llava-1.5-7b-hf"
    pipe = pipeline("image-to-text", model=model_id, model_kwargs={})
    outputs = pipe(image, prompt=prompt, generate_kwargs={"max_new_tokens": 200})
    return outputs[0]["generated_text"]

image_url = "https://llava-vl.github.io/static/images/view.jpg"
prompt = "USER: <image>\ngive a similarity value of 0 or 1 between each of the following labels and the image and return the result in a JSON format. Lifestyle & Entertainment, News & Politics, Travel & Exploration, Health & Wellness, Technology & Science, Food & Cuisine, Pet & Animal Content, Nature & Photography, Sports & Fitness, Cultural & Social Issues\nASSISTANT:"
result = image_to_text_similarity(image_url, prompt)
print(result)
