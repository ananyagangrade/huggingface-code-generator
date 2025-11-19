# generator/models.py
import os

DEFAULT_MODEL = os.getenv("CODEGEN_MODEL", "Salesforce/codegen-350M-multi")

class CodeGenModel:
    def __init__(self, model_name: str = DEFAULT_MODEL, device: str = None):
        self.model_name = model_name
        self.device = device or ("cuda" if self._cuda_available() else "cpu")
        self.tokenizer = None
        self.model = None

        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch  # noqa: F401
        except Exception as e:
            raise ImportError(
                "transformers/torch not available. Install with: 'pip install transformers torch sentencepiece huggingface_hub'\n"
                f"Original error: {e}"
            ) from e

        try:
            print(f"[models] Loading tokenizer for model: {model_name} ... (device={self.device})")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
            print("[models] Tokenizer loaded. Loading model (this may take some time)...")
            if self.device == "cuda":
                self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
            else:
                self.model = AutoModelForCausalLM.from_pretrained(model_name)
            print("[models] Model loaded successfully.")
        except Exception as e:
            msg = (
                "[models] Failed to load model from Hugging Face. "
                "This can happen if the model is gated (requires HF access), "
                "if you are offline, or if the model name is incorrect.\n"
                f"Attempted model: {model_name}\n"
                f"Original error: {e}"
            )
            raise OSError(msg) from e

    def _cuda_available(self):
        try:
            import torch
            return torch.cuda.is_available()
        except Exception:
            return False

    def generate(self, prompt: str, max_new_tokens: int = 256, temperature: float = 0.2, top_p: float = 0.95):
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded")

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        import torch as _torch
        with _torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
