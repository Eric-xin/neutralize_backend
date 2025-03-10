from openai import OpenAI
import os
from dotenv import load_dotenv
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, CLIPProcessor, CLIPModel
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from PIL import Image

load_dotenv()

# Determine available device: cuda > mps > cpu
device = torch.device("cuda" if torch.cuda.is_available() 
                      else "mps" if torch.backends.mps.is_available() 
                      else "cpu")
print(f"Using device: {device.type.upper()} ({torch.cuda.get_device_name(device) if device.type == 'cuda' else 'N/A'})")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load bias analysis model and move to device
tokenizer = AutoTokenizer.from_pretrained("textattack/bert-base-uncased-yelp-polarity")
model = AutoModelForSequenceClassification.from_pretrained("textattack/bert-base-uncased-yelp-polarity")
model.to(device)

# Load CLIP model and processor, then move model to device
clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
clip_model.to(device)

# Load GPT-2 model and tokenizer for text generation, then move model to device
gpt_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
gpt_model = GPT2LMHeadModel.from_pretrained("gpt2")
gpt_model.to(device)

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def NLP_ana(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    # Move inputs to device
    inputs = {k: v.to(device) for k, v in inputs.items()}
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
        inputs = {k: v.to(device) for k, v in inputs.items()}
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
        text_inputs = {k: v.to(device) for k, v in text_inputs.items()}
        with torch.no_grad():
            text_features = clip_model.get_text_features(**text_inputs)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        
        similarity = (image_features @ text_features.T).squeeze(0)
        best_prompt_idx = similarity.argmax().item()
        selected_prompt = base_prompts[best_prompt_idx]
        
        # Use the selected prompt to generate a detailed description with GPT-2
        prompt = f"Describe the image in detail: {selected_prompt}"
        input_ids = gpt_tokenizer.encode(prompt, return_tensors="pt").to(device)
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
        return response.choices[0].message.content.strip(), multimodal_context
    except Exception as e:
        return str(e), multimodal_context

def multicon_GPT_ana(text, bias_level, image_path=None, model="gpt-3.5-turbo"):
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
        return response.choices[0].message.content.strip(), multimodal_context
    except Exception as e:
        return str(e), multimodal_context
