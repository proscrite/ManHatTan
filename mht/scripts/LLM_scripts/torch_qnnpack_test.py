import torch

import os
from transformers import AutoTokenizer, AutoModelForCausalLM

# ————————————————————————————————
# 0. Tame parallelism on macOS
# ————————————————————————————————
os.environ["TOKENIZERS_PARALLELISM"] = "false"
torch.set_num_threads(1)

# ————————————————————————————————
# 1. LOAD MODEL & TOKENIZER ONCE
# ————————————————————————————————
MODEL = "Norod78/hebrew-gpt_neo-small"
tokenizer = AutoTokenizer.from_pretrained(MODEL, use_fast=False)

# Load full‐precision model
model_fp = AutoModelForCausalLM.from_pretrained(MODEL)
# Try setting the quantization engine to qnnpack
torch.backends.quantized.engine = "qnnpack"
print("Quantization engine:", torch.backends.quantized.engine)

quantized_model = torch.quantization.quantize_dynamic(
    model_fp,
    {torch.nn.Linear},
    dtype=torch.qint8,
)