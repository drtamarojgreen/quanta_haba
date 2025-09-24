# Integrating the TISSLM Model via Python

This document provides instructions on how to integrate the TISSLM model directly into your Python application by using its core modules. This approach allows for fine-grained control and avoids the overhead of a network API.

## Prerequisites

Before you can use the model, you need two essential artifacts:

1.  **A Trained Tokenizer:** The model requires a tokenizer to be trained on your corpus. You can train one by running the `train_bpe.py` script.
2.  **A Model Checkpoint:** You need a trained model checkpoint file (`.npz`). You can train a model and generate a checkpoint by running the `run_training.py` script.

Please ensure you have the paths to both the tokenizer directory and the checkpoint file ready.

## Generating Text: A Code Example

The primary way to generate text is by using the `generate_text` function. The following example demonstrates the end-to-end process of loading the model and generating a response to a prompt.

```python
import numpy as np
from quanta_tissu.tisslm.core.model import QuantaTissu
from quanta_tissu.tisslm.core.tokenizer import Tokenizer
from quanta_tissu.tisslm.core.generate_text import generate_text
from quanta_tissu.tisslm.config import model_config

# --- 1. Define Paths ---
# Update these paths to point to your trained artifacts.
TOKENIZER_PATH = "/path/to/your/tokenizer"
CHECKPOINT_PATH = "/path/to/your/model_checkpoint.npz"

# --- 2. Initialize Tokenizer and Model ---
try:
    # Load the trained tokenizer
    tokenizer = Tokenizer(tokenizer_path=TOKENIZER_PATH)
except FileNotFoundError:
    print(f"Error: Tokenizer not found at '{TOKENIZER_PATH}'")
    # Instructions for the user could be added here.
    exit()

# Update the model configuration with the tokenizer's vocabulary size
model_config["vocab_size"] = tokenizer.get_vocab_size()

# Instantiate the model
model = QuantaTissu(model_config)

# --- 3. Load Model Weights ---
try:
    # Load the trained weights from the checkpoint file
    model.load_weights(CHECKPOINT_PATH)
except FileNotFoundError:
    print(f"Error: Checkpoint not found at '{CHECKPOINT_PATH}'")
    # Instructions for the user could be added here.
    exit()

# --- 4. Generate Text ---
prompt = "This is the start of a beautiful story"
generated_output = generate_text(
    model=model,
    tokenizer=tokenizer,
    prompt=prompt,
    length=50,  # Number of new tokens to generate
    method="nucleus",
    temperature=0.8,
    top_k=20,
    top_p=0.9,
    repetition_penalty=1.0
)

print("--- Prompt ---")
print(prompt)
print("
--- Generated Response ---")
print(generated_output)

```

### Explanation

1.  **Import necessary components:** We import the `QuantaTissu` model, the `Tokenizer`, the `generate_text` function, and the base `model_config`.
2.  **Initialize Components:** We first create an instance of the `Tokenizer`. We then update the global `model_config` with the actual vocabulary size from our tokenizer before creating an instance of the `QuantaTissu` model.
3.  **Load Weights:** We call the `load_weights()` method on the model instance to load the trained parameters from our checkpoint file.
4.  **Generate:** We call the `generate_text()` function, passing it the initialized model and tokenizer, our text prompt, and various parameters to control the generation process.

This process gives you direct access to the model's generation capabilities within your Python code.