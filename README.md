## Installation

```bash
python -m venv grok_env
grok_env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Add Grok API Key

```bash
cp .env.example .env

# Edit .env with your xAI API key
# Add: XAI_API_KEY=your_actual_xai_api_key_here
```

## Claude Desktop Setup
add to ```claude_desktop_config.json```
```bash
{
  "mcpServers": {
    "plant-detector": {
      "command": "C:\\path\\to\\grok_env\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\grok-mcp-plant-detection\\mcp_fast_grok_real.py"]
    }
  }
}
```

## Testing MCP file on local
add images to the images_test folder
```bash
python test_direct.py
```
