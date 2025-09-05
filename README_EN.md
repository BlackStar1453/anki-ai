# Chat with Card

> AI-powered chat tool for Anki with card generation capabilities and multi-language support

[![Build Status](https://github.com/your-username/chat-with-card/workflows/Build%20and%20Release%20Chat%20with%20Card/badge.svg)](https://github.com/your-username/chat-with-card/actions)
[![AnkiWeb](https://img.shields.io/badge/AnkiWeb-Available-blue)](https://ankiweb.net/shared/addons/)
[![Version](https://img.shields.io/badge/version-2.0.0-green)](https://github.com/your-username/chat-with-card/releases)

## ✨ Features

- 🤖 **AI Chat Integration**: Chat with AI about your Anki cards
- 📝 **Card Generation**: Create cards directly from conversations
- 🌍 **Multi-language Support**: English, 简体中文, 繁體中文, 日本語
- ✨ **Markdown Support**: Rich text formatting in both chat and cards
- 🎨 **Modern UI**: Clean, minimalist design optimized for Anki
- 📦 **Self-contained**: No additional installations required

## 🚀 Quick Start

### Installation

1. Download the latest `.ankiaddon` file from [Releases](https://github.com/your-username/chat-with-card/releases)
2. In Anki: **Tools** > **Add-ons** > **Install from file**
3. Select the downloaded file
4. Restart Anki
5. Configure your AI API key in the settings

### Usage

1. Open any card in Anki
2. Click the **"Open Chat"** button
3. Start chatting with AI about your card
4. Create new cards directly from your conversations

## 🌍 Language Support

The addon automatically detects your system language and supports:

| Language | Code | Status |
|----------|------|--------|
| English | `en` | ✅ Full support |
| 简体中文 | `zh_CN` | ✅ Complete translation |
| 繁體中文 | `zh_TW` | ✅ Complete translation |
| 日本語 | `ja` | ✅ Complete translation |

You can manually change the language in **Settings** > **Language**.

## 🔧 Development

### Prerequisites

- Python 3.7+
- Anki 2.1.0+

### Setup

```bash
# Clone the repository
git clone https://github.com/your-username/chat-with-card.git
cd chat-with-card

# Install dependencies
make install-deps

# Build the addon
make build
```

### Available Commands

```bash
make help          # Show all available commands
make build         # Build the addon package
make test          # Run tests
make check         # Run release checks
make clean         # Clean build files
make release VERSION=2.0.0  # Complete release workflow
```

## 📦 Release Process

### Automated Release (Recommended)

```bash
# Complete automated release
make release VERSION=2.0.0

# Or use the release script directly
./scripts/release.sh 2.0.0
```

This will:
1. Update version numbers
2. Build the addon package
3. Run all checks
4. Create Git tag
5. Trigger GitHub Actions for automated release

### Manual Release

```bash
# Build only
python build_addon.py

# Check release
python check_release.py

# Create tag manually
git tag v2.0.0
git push origin v2.0.0
```

### GitHub Actions

The project includes automated CI/CD workflows:

- **Build and Release**: Triggered by version tags
- **AnkiWeb Upload Prep**: Manual trigger for AnkiWeb submission

See [GitHub Actions Setup](GITHUB_ACTIONS_SETUP.md) for detailed configuration.

## 📋 Project Structure

```
chat-with-card/
├── __init__.py              # Plugin entry point
├── manifest.json            # Anki addon manifest
├── config.json             # Default configuration
├── config.py               # Configuration management
├── ui/                     # User interface components
│   ├── chat_dialog.py      # Main chat interface
│   └── config_dialog.py    # Settings dialog
├── services/               # Core services
│   ├── ai_service_adapter.py  # AI service integration
│   └── card_service.py     # Card creation service
├── utils/                  # Utility functions
├── i18n/                   # Internationalization
│   ├── translator.py       # Translation system
│   └── locales/           # Translation files
├── vendor/                 # Bundled dependencies (auto-generated)
├── scripts/               # Build and release scripts
├── .github/workflows/     # GitHub Actions
└── dist/                  # Build output (auto-generated)
```

## 🔧 Configuration

The addon can be configured through:

1. **Settings Dialog**: Access via Tools menu or addon manager
2. **Config File**: Direct editing of `config.json`
3. **Environment Variables**: For advanced users

### API Keys

Supported AI providers:
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Google (Gemini)

Configure your API key in the settings dialog.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Submit a pull request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Update translations for UI changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Anki](https://apps.ankiweb.net/) - The amazing spaced repetition software
- [OpenAI](https://openai.com/) - AI API services
- [Mistune](https://github.com/lepture/mistune) - Markdown processing
- The Anki community for feedback and support

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/chat-with-card/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/chat-with-card/discussions)
- **AnkiWeb**: [Addon Page](https://ankiweb.net/shared/addons/)

---

Made with ❤️ for the Anki community

## 📖 Other Languages

- [中文文档](README.md) - Chinese documentation
