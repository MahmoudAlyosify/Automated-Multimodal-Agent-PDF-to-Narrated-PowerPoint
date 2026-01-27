"""
Initialize LayoutLMv3 model - downloads from HuggingFace on first run
"""

import os
import sys

def init_layoutlmv3():
    """Download and initialize LayoutLMv3 model"""
    print("🤖 Initializing Microsoft LayoutLMv3...")
    print("   Model: microsoft/layoutlmv3-base")
    print("   Source: HuggingFace Hub")
    print()
    
    try:
        from transformers import AutoTokenizer, AutoModelForTokenClassification
        
        model_name = "microsoft/layoutlmv3-base"
        
        print("📥 Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            apply_ocr=True,
            trust_remote_code=True,
            cache_dir=os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
        )
        print("✓ Tokenizer loaded")
        
        print("📥 Downloading model (this may take a few minutes)...")
        model = AutoModelForTokenClassification.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir=os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
        )
        print("✓ Model loaded")
        
        print()
        print("✅ LayoutLMv3 initialization complete!")
        print("   Location: ~/.cache/huggingface/hub/")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error initializing LayoutLMv3: {str(e)}")
        print("   The app will use rule-based analysis as fallback")
        print()
        return False

if __name__ == "__main__":
    init_layoutlmv3()
