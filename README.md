# AI Browser Agent - Intelligent Browser Automation Assistant

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/Playwright-✅-green.svg)](https://playwright.dev/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-orange.svg)](https://openai.com/)

An autonomous AI agent capable of performing complex tasks in the browser: from searching and ordering products to navigating websites. Simply describe what needs to be done - the agent will plan and execute all actions independently.

## Features

- Intelligent planning - breaks down complex tasks into a sequence of steps
- Browser automation - full control via Playwright
- Contextual understanding - remembers action history and current state
- E-commerce automation - product search, cart management, order placement
- Smart element detection - uses Accessibility Tree for precise interaction

## Example Tasks

- "Order tomatoes from Samokat"
- "Find laptops on Ozon and add the cheapest one to cart"
- "Book a table at a restaurant on the website"
- "Compare flight prices"

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/nk-knvlv/ai_agent.git
cd ai_agent/src
```

### 2. It is recommended to use a local model with 14B parameters or more.

```bash
# Install Ollama (visit https://ollama.ai for other platforms)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the recommended model
ollama pull qwen2.5:14b
```
### 3. Setup Python Environment

```bash
python -m venv .venv

.\.venv\Scripts\activate

pip install -r requirements.txt
```

### 4. Create a .env file in the project root:

```bash

# Ollama Configuration
OLLAMA_MODEL=qwen2.5:14b
OLLAMA_HOST=http://localhost:11434

# Optional: For OpenAI or other providers
# OPENAI_API_KEY=your_key_here
```

### 5. Run

```bash
python -m ai_browser_agent
```
