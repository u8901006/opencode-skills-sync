---
name: llama-index
description: Use when working with LlamaIndex, llama-index, llama_index, RAG pipelines, document ingestion, vector indexes, retrieval, query engines, chat engines, or agent workflows in Python.
---

# LlamaIndex

## Overview

Use this skill for Python work involving LlamaIndex. On this Windows machine, the verified shared install is `llama-index 0.14.22` under Python 3.12.

Core principle: target the known interpreter explicitly and verify current APIs before writing code.

## Environment

Use Python 3.12 explicitly:

```powershell
py -3.12 -m pip show llama-index
py -3.12 -c "import importlib.metadata as m; from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader; print(m.version('llama-index'))"
```

Do not rely on bare `python` or `pip` here. `python` may point to a Hermes venv, while `pip` may target a different interpreter.

Known verified location:

```text
C:\Users\u8901\AppData\Local\Programs\Python\Python312\Lib\site-packages
```

## Before Coding

Fetch current docs before writing or changing LlamaIndex code:

```powershell
chub get llama-index/package --lang py
```

If `chub` is unavailable, use the official docs at `https://developers.llamaindex.ai/python/framework/`.

## Correct Imports

Install package name: `llama-index`.

Import package name: `llama_index`.

Current baseline imports:

```python
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
```

Use `Settings`, not old `ServiceContext` examples unless maintaining legacy code.

Avoid outdated examples using `GPTVectorStoreIndex`, `LLMPredictor`, or implicit model defaults.

## Common Workflows

OpenAI-backed starter:

```python
import os

from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

Settings.llm = OpenAI(model=os.environ["OPENAI_MODEL"])
Settings.embed_model = OpenAIEmbedding(
    model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
)

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
response = index.as_query_engine(similarity_top_k=3).query("Summarize these files.")
print(str(response))
```

Persist and reload:

```python
from llama_index.core import StorageContext, load_index_from_storage

index.storage_context.persist(persist_dir="storage")

storage_context = StorageContext.from_defaults(persist_dir="storage")
restored_index = load_index_from_storage(storage_context)
```

## Package Split

The starter package does not include every integration. Add explicit packages when needed:

```powershell
py -3.12 -m pip install llama-index-llms-ollama llama-index-embeddings-huggingface
py -3.12 -m pip install chromadb llama-index-vector-stores-chroma
```

Use `pathlib.Path` for paths in scripts so code works cleanly on Windows.

## Do Not Use

- Do not use `llamaindex-cli`; it is deprecated and was removed locally because it failed against current `llama-index-core`.
- Do not use `llama_index.__version__`; use `importlib.metadata.version('llama-index')`.
- Do not assume OpenAI keys or models are configured. Check or set `OPENAI_API_KEY`, `OPENAI_MODEL`, and embedding model settings explicitly.

## Verification

After installing or changing dependencies, run:

```powershell
py -3.12 -c "import importlib.metadata as m; from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader; print('llama-index', m.version('llama-index')); print('core imports ok')"
```
