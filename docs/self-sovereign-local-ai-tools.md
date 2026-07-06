# Self-Sovereign & Local-Only AI Tools

**Self-sovereign and local-only AI** refers to running large language models (LLMs) and AI applications entirely on your own computer or local network — with **zero data leaving your machine**.

Unlike cloud-based services (ChatGPT, Claude, Gemini, etc.), these tools:
- Keep all your documents, conversations, and knowledge completely private
- Work fully offline (no internet required after initial model download)
- Give you full control over which models you use and how they behave
- Avoid vendor lock-in, recurring subscription costs, and data privacy concerns
- Are ideal for sensitive or proprietary work such as scientific research, personal knowledge management, and internal organizational knowledge bases

This approach is especially powerful for researchers and knowledge workers who want to:
- Chat with their own documents and datasets
- Maintain long-term, version-controlled knowledge collections (such as OKF bundles)
- Experiment with different open models without technical complexity
- Share curated knowledge with collaborators who may not be deeply technical

Below are three excellent, beginner-friendly options that make local AI accessible without requiring programming or server administration skills.

## AnythingLLM

**AnythingLLM** is an all-in-one desktop application designed for chatting with your documents and building private knowledge workspaces. It is one of the most user-friendly options available for non-technical users who want powerful local RAG (Retrieval-Augmented Generation) capabilities.

It excels at turning folders of documents — including Markdown-based collections like OKF — into searchable, chat-able knowledge bases. You can drag and drop an entire folder, and it handles indexing, embedding, and conversation memory automatically.

**Key strengths for researchers:**
- Excellent folder-based document chat and RAG
- Clean, modern interface similar to ChatGPT
- Supports local models via Ollama or LM Studio backends
- Built-in agent features and multi-user workspaces (optional)
- Fully offline after setup

### Getting Started with an OKF Collection (Quick Steps)
1. Download and install AnythingLLM from the official site.
2. Launch the app and create a new Workspace.
3. Drag your entire OKF bundle folder into the workspace (or use the “Add Documents” button and select the folder).
4. Choose a local embedding model (default works well for most OKF collections).
5. Wait for indexing to complete (it processes the Markdown files and frontmatter automatically).
6. Start chatting! Example prompts:
   - “Summarize the δ¹³C profile from Station 1”
   - “What water masses are discussed in the GEOTRACES concepts?”
   - “Compare carbon cycling insights across the first five stations”

### Recommended Settings for OKF Collections
- **Embedding Model**: `nomic-embed-text` or `mxbai-embed-large` (good balance of quality and speed for technical Markdown)
- **Chunk Size**: 800–1200 tokens (OKF concepts are often self-contained, so larger chunks work well)
- **Chunk Overlap**: 100–200 tokens
- **Retrieval Mode**: Hybrid (semantic + keyword) if available — helps with specific concept names and tags
- Enable “Agentic” mode for more complex multi-step questions about your data

**Links:**
- Official Website: [https://anythingllm.com/](https://anythingllm.com/)
- GitHub Repository: [https://github.com/Mintplex-Labs/anything-llm](https://github.com/Mintplex-Labs/anything-llm)
- Desktop Download: [https://anythingllm.com/download](https://anythingllm.com/download)
- Documentation: [https://docs.anythingllm.com](https://docs.anythingllm.com)

## LM Studio

**LM Studio** is a polished desktop application for discovering, downloading, and running local LLMs with a graphical interface. It includes built-in tools for chatting with documents and experimenting with models.

It is particularly popular among users who want a simple way to browse Hugging Face models, quantize them, and run them locally with GPU acceleration where available. The document chat feature allows you to load folders of files (including Markdown) and have conversations grounded in that content.

**Key strengths for researchers:**
- Beautiful model browser and downloader
- Easy GPU/CPU configuration
- Built-in document chat / RAG
- OpenAI-compatible local server mode (useful for connecting other tools)
- Cross-platform (Windows, macOS, Linux)

### Getting Started with an OKF Collection (Quick Steps)
1. Download and install LM Studio from [lmstudio.ai](https://lmstudio.ai/).
2. Open LM Studio and go to the **My Models** tab to download a chat model (e.g., Gemma 2, Llama 3.2, or Qwen2.5).
3. Switch to the **Chat** tab (or **Documents** / **Chat with Docs** section depending on version).
4. Add your OKF folder (look for “Add Files/Folder” or the documents panel).
5. Select the model you want to use.
6. Start asking questions. The interface will ground answers in your OKF Markdown files.

### Recommended Settings for OKF Collections
- Use a reasonably capable model (7B+ parameters recommended for technical content)
- In document settings, enable **recursive folder scanning** if available
- Set context length high enough to include relevant concept frontmatter (e.g., 8k–32k tokens)
- Experiment with temperature 0.3–0.7 for more factual answers about data

**Links:**
- Official Website: [https://lmstudio.ai/](https://lmstudio.ai/)
- Download / Installers: Available directly from the website above

## Ollama + Open WebUI

This combination pairs **Ollama** (a lightweight, powerful tool for running and managing local LLMs) with **Open WebUI** (a beautiful, self-hosted web interface that feels like ChatGPT).

**Ollama** provides the underlying engine for running models efficiently on your hardware. **Open WebUI** adds a modern, feature-rich chat interface on top, with strong support for document collections, RAG, and multi-user setups. The result is a complete local AI environment that many people find more powerful and customizable than single desktop apps.

**Key strengths for researchers:**
- Extremely efficient model running (Ollama)
- Highly customizable and extensible interface (Open WebUI)
- Excellent RAG and document collection support
- Can be run as a simple desktop app or self-hosted service
- Large, active community and frequent updates
- Works very well with structured Markdown collections (such as OKF)

### Getting Started with an OKF Collection (Quick Steps)
1. Install Ollama from [ollama.com](https://ollama.com/).
2. Pull a model: `ollama pull gemma3:12b` (or your preferred model).
3. Install Open WebUI (easiest via the official desktop app or Docker — see docs).
4. In Open WebUI, create a new **Collection** (or Workspace).
5. Upload or point to your OKF folder (it supports recursive Markdown ingestion and respects links between concepts).
6. Start chatting in a new conversation that references the collection.

### Recommended Settings for OKF Collections
- Use a strong embedding model in Open WebUI settings (e.g., `nomic-embed-text` or `snowflake-arctic-embed`)
- Enable **Hybrid Search** (semantic + keyword) for better results on technical terms and station/concept names
- Set chunk size around 1000 tokens with modest overlap
- Turn on **RAG** and **Web Search** toggles only if needed (keep it local-first)

**Links:**
- Ollama Website: [https://ollama.com/](https://ollama.com/)
- Ollama GitHub: [https://github.com/ollama/ollama](https://github.com/ollama/ollama)
- Open WebUI Website: [https://openwebui.com/](https://openwebui.com/)
- Open WebUI GitHub: [https://github.com/open-webui/open-webui](https://github.com/open-webui/open-webui)
- Open WebUI Documentation: [https://docs.openwebui.com](https://docs.openwebui.com)

---

## Comparison Table

| Feature                        | AnythingLLM                  | LM Studio                     | Ollama + Open WebUI              |
|--------------------------------|------------------------------|-------------------------------|----------------------------------|
| **Ease of use for beginners**  | Excellent (drag & drop)     | Very Good                     | Good (slightly more setup)      |
| **Document / OKF folder support** | Outstanding                | Good                          | Excellent                       |
| **Model discovery & download** | Good                        | Excellent                     | Good (via Ollama)               |
| **Customization & power**      | Very Good                   | Good                          | Excellent                       |
| **Multi-user / team features** | Built-in workspaces         | Limited                       | Strong (users, permissions)     |
| **Offline capability**         | Full                        | Full                          | Full                            |
| **Best for**                   | Non-technical researchers sharing OKF collections | Individuals experimenting with many models | Teams or users wanting maximum control & features |
| **Learning curve**             | Lowest                      | Low                           | Medium                          |

---

## Choosing the Right Tool – Quick Decision Guide

**Choose AnythingLLM if:**
- Your primary goal is letting non-technical researchers or collaborators quickly chat with an OKF collection or folder of documents.
- You want the simplest possible experience with excellent out-of-the-box RAG.
- You like a clean ChatGPT-like interface with minimal configuration.

**Choose LM Studio if:**
- You (or your team) want an easy way to try many different models and experiment.
- You value a beautiful graphical model browser and one-click downloads.
- You occasionally want to run the local model as an OpenAI-compatible server for other tools.

**Choose Ollama + Open WebUI if:**
- You want the most powerful and customizable local setup.
- You anticipate team use, more advanced RAG needs, or long-term maintenance of knowledge collections.
- You like having a web-based interface that can run on a small server or desktop and supports multiple users.

**General recommendation for sharing OKF collections with researchers:**
Start with **AnythingLLM** — it has the lowest barrier for non-technical users while delivering excellent results with Markdown-based knowledge like OKF. Many people later add LM Studio or Open WebUI as they become more comfortable.

All three options fully support the self-sovereign, local-only philosophy: your OKF data, conversations, and models stay entirely under your control. 

Would you like me to add installation one-liners, example prompts tailored to ocean/GEOTRACES data, or export this document as a nicely formatted PDF?