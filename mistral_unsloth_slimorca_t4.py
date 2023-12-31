# -*- coding: utf-8 -*-
"""Mistral_Unsloth_slimorca_T4

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15pyLgRN97B_jA56HS0esx56knA9I5tuv
"""

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# import torch
# major_version, minor_version = torch.cuda.get_device_capability()
# if major_version >= 8:
#     # A100, RTX 3060+ support
#     !pip install "unsloth[colab_ampere] @ git+https://github.com/unslothai/unsloth.git"
# else:
#     # Tesla T4, V100 support
#     !pip install "unsloth[colab] @ git+https://github.com/unslothai/unsloth.git"
# pass

model_name = "mistralai/Mistral-7B-v0.1"
max_seq_length = 2048
learning_rate = 2e-4
weight_decay = 0.01
max_steps = 60
warmup_steps = 10
batch_size = 2
gradient_accumulation_steps = 4
lr_scheduler_type = "linear"
optimizer = "adamw_8bit"
use_gradient_checkpointing = True
random_state = 3407

from unsloth import FastMistralModel
import torch
max_seq_length = 2048
dtype = None # None for auto detection. Float16 for Tesla T4, V100, Bfloat16 for Ampere+
load_in_4bit = True # Use 4bit quantization to reduce memory usage. Can be False.
HAS_BFLOAT16 = torch.cuda.is_bf16_supported()

model, tokenizer = FastMistralModel.from_pretrained(
    model_name = model_name,
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
    # token = "hf_...", # use one if using gated models like meta-llama/Llama-2-7b-hf
)

model = FastMistralModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0, # Currently only supports dropout = 0
    bias = "none",    # Currently only supports bias = "none"
    use_gradient_checkpointing = True,
    random_state = 3407,
    max_seq_length = max_seq_length,
)

#@title Slim Orca data prep
from datasets import load_dataset
dataset = load_dataset('json', data_files='output.json', split = "train")
def formatting_prompts_func(examples):
    convos = examples["conversations"]
    texts = []
    mapper = {"system" : "SYSTEM:", "human" : "USER:", "gpt" : "ASSISTANT:"}
    end_mapper = {"system" : "\n\n", "human" : "\n", "gpt" : "</s>\n"}
    for convo in convos:
        text = "".join(f"{mapper[(turn := x['from'])]} {x['value']}{end_mapper[turn]}" for x in convo)
        texts.append(text)
    return { "text" : texts, }
pass
dataset = dataset.map(formatting_prompts_func, batched = True,)

from trl import SFTTrainer
from transformers import TrainingArguments
from transformers.utils import logging
logging.set_verbosity_info()

trainer = SFTTrainer(
    model = model,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    tokenizer = tokenizer,
    args = TrainingArguments(
        per_device_train_batch_size = batch_size,
        gradient_accumulation_steps = gradient_accumulation_steps,
        warmup_steps = warmup_steps,
        max_steps = max_steps,
        learning_rate = learning_rate,
        fp16 = not HAS_BFLOAT16,
        bf16 = HAS_BFLOAT16,
        logging_steps = 1,
        output_dir = "outputs",
        optim = optimizer,
        weight_decay = weight_decay,
        lr_scheduler_type = lr_scheduler_type,
        seed = random_state,
    ),
)

gpu_stats = torch.cuda.get_device_properties(0)
start_gpu_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
max_memory = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
print(f"GPU = {gpu_stats.name}. Max memory = {max_memory} GB.")
print(f"{start_gpu_memory} GB of memory reserved.")

trainer_stats = trainer.train()

print(f"{trainer_stats.metrics['train_runtime']} seconds used for training.")
print(f"{round(trainer_stats.metrics['train_runtime']/60, 2)} minutes used for training.")

# Save the trained model
model_save_path = "outputs"
model.save_pretrained(model_save_path)

print(f"Model saved to {model_save_path}")