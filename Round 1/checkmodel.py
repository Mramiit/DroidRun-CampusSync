import os
from google import genai

# Setup your key
os.environ["GEMINI_API_KEY"] = "YOUR_ACTUAL_KEY_HERE"

def list_my_models():
    try:
        client = genai.Client(api_key=os.environ["API_KEY"])
        print("🔍 Asking Google for available models...")
        
        # List all models
        models = list(client.models.list())
        
        print(f"\n✅ Found {len(models)} models. Here are the 'Flash' and 'Pro' ones:")
        print("-" * 50)
        
        valid_models = []
        for m in models:
            # We filter for models that support 'generateContent'
            if "generateContent" in m.supported_generation_methods:
                print(f"👉 {m.name}")
                valid_models.append(m.name)
                
        print("-" * 50)
        print("💡 TIP: Copy one of the names above EXACTLY (e.g., 'models/gemini-1.5-flash')")
        
    except Exception as e:
        print(f"❌ Error listing models: {e}")

if __name__ == "__main__":
    list_my_models()
