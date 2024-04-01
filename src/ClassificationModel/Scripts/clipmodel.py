from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import requests

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def classify_single_image(image_path,labels_list,model=model,processor=processor):
    
    if not image_path.startswith(('http', 'https')):
        image = Image.open(image_path)
    else:
        image = Image.open(requests.get(image_path, stream=True).raw)
    inputs = processor(text=labels_list, images=[image], return_tensors="pt", padding=True)
    outputs = model(**inputs)

    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)

    classified_result = {cls: prob.item() for cls, prob in zip(labels_list, probs[0].detach().numpy())}

    results= classified_result


    return results


