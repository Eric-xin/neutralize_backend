from openai import OpenAI
import os
from dotenv import load_dotenv
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, CLIPProcessor, CLIPModel
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from PIL import Image

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load bias analysis model
tokenizer = AutoTokenizer.from_pretrained("textattack/bert-base-uncased-yelp-polarity")
model = AutoModelForSequenceClassification.from_pretrained("textattack/bert-base-uncased-yelp-polarity")

# Load CLIP model for multimodal reasoning
# clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
# clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
# Load CLIP model and processor
clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

# Load GPT-2 model and tokenizer for text generation
gpt_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
gpt_model = GPT2LMHeadModel.from_pretrained("gpt2")

def NLP_ana(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        logits = model(**inputs).logits
        probabilities = logits.softmax(dim=-1)[0].tolist()
    
    categories = ["Left", "Middle", "Right"]
    bias_result = {categories[i]: probabilities[i] for i in range(len(categories))}
    
    return bias_result

def multimodal_reasoning(image_path=None):
    if not image_path:
        return "No image provided."
    
    try:
        # Load and preprocess the image using CLIP
        image = Image.open(image_path).convert("RGB")
        inputs = clip_processor(images=image, return_tensors="pt")
        with torch.no_grad():
            image_features = clip_model.get_image_features(**inputs)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        
        # Define a few base descriptive prompts
        base_prompts = [
            "An intricate scene with a vibrant composition, capturing a moment full of depth and detail.",
            "A richly detailed image that tells a complex story with subtle nuances and vivid colors.",
            "A dynamic portrayal that combines textures, light, and shadow to reveal a captivating narrative.",
            "A visually striking scene that blends emotion and detail in a sophisticated manner."
        ]
        
        # Use CLIP to determine which base prompt best aligns with the image
        text_inputs = clip_processor(text=base_prompts, return_tensors="pt", padding=True)
        with torch.no_grad():
            text_features = clip_model.get_text_features(**text_inputs)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        
        similarity = (image_features @ text_features.T).squeeze(0)
        best_prompt_idx = similarity.argmax().item()
        selected_prompt = base_prompts[best_prompt_idx]
        
        # Use the selected prompt to generate a detailed description with GPT-2
        prompt = f"Describe the image in detail: {selected_prompt}"
        input_ids = gpt_tokenizer.encode(prompt, return_tensors="pt")
        output_ids = gpt_model.generate(
            input_ids, 
            max_length=150, 
            num_return_sequences=1, 
            do_sample=True, 
            temperature=0.7,
            pad_token_id=gpt_tokenizer.eos_token_id
        )
        detailed_description = gpt_tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return detailed_description

    except Exception as e:
        return f"Error processing image: {str(e)}"

# def multimodal_reasoning(t="", image_path=None):
#     reasoning = t  # Default text
#     if image_path:
#         try:
#             # Load and preprocess the image
#             image = Image.open(image_path).convert("RGB")
#             inputs = clip_processor(images=image, return_tensors="pt")

#             # Extract image features
#             with torch.no_grad():
#                 image_features = clip_model.get_image_features(**inputs)

#             # Normalize the image features
#             image_features /= image_features.norm(dim=-1, keepdim=True)

#             # Define candidate textual descriptions
#             candidate_texts = [
#                 "A dog playing in the park",
#                 "A cat sleeping on a sofa",
#                 "A beautiful sunset over the ocean",
#                 "A person riding a bicycle",
#                 "A plate of delicious food",
#                 "A city skyline at night",
#                 "A book on a wooden table"
#             ]

#             # Convert text descriptions to CLIP embeddings
#             text_inputs = clip_processor(text=candidate_texts, return_tensors="pt", padding=True)
#             with torch.no_grad():
#                 text_features = clip_model.get_text_features(**text_inputs)
            
#             # Normalize the text features
#             text_features /= text_features.norm(dim=-1, keepdim=True)

#             # Compute similarity between image and text
#             similarity = (image_features @ text_features.T).squeeze(0)
#             best_match_idx = similarity.argmax().item()
#             reasoning = candidate_texts[best_match_idx]

#         except Exception as e:
#             reasoning = f"Error processing image: {str(e)}"

#     return reasoning

# def multimodal_reasoning(text, image_path=None):
#     reasoning = ""  # Default reasoning text
#     if image_path:
#         image = clip_processor(images=image_path, return_tensors="pt")
#         with torch.no_grad():
#             image_features = clip_model.get_image_features(**image)
#         reasoning = f"Image features extracted: {image_features.shape}"
#     return reasoning

# def multimodal_reasoning(image_path=None):
#     reasoning = ""  # Default reasoning text
#     if image_path:
#         try:
#             # Load image using PIL
#             image = Image.open(image_path).convert("RGB")

#             # Process image using CLIP's processor
#             inputs = clip_processor(images=image, return_tensors="pt")
#             # Extract image features
#             with torch.no_grad():
#                 image_features = clip_model.get_image_features(**inputs)
#             reasoning = f"Image features extracted: {image_features.shape}"
#         except Exception as e:
#             reasoning = f"Error processing image: {str(e)}"
#     return reasoning

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def reduce_bias(text, bias_level, image_path=None, model="gpt-3.5-turbo"):
    multimodal_context = multimodal_reasoning(image_path)
    prompt = f"""
    The following text may have bias based on the given bias level ({bias_level}). 
    Please rewrite it in a more neutral and objective manner while keeping the meaning intact:
    
    Original Text:
    "{text}"
    
    Additional Context:
    {multimodal_context}
    
    Neutral Rewrite:
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an AI that neutralizes bias in text with advanced multimodal reasoning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        # return response.choices[0].message.content.strip()
        return response.choices[0].message.content.strip(), multimodal_context
    except Exception as e:
        return str(e)


def multicon_GPT_ana(text, bias_level, image_path=None):
    multimodal_context = multimodal_reasoning(image_path)
    prompt = f"""
    The following text may have bias based on the given bias level ({bias_level}). 
    Please explain why the text is biased, in markdown, and also analyze how to correctly interpret it:
    
    Original Text:
    "{text}"
    
    Additional Context:
    {multimodal_context}
    
    Neutral Rewrite:
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an AI that neutralizes bias in text with advanced multimodal reasoning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        # return response.choices[0].message.content.strip()
        return response.choices[0].message.content.strip(), multimodal_context
    except Exception as e:
        return str(e)