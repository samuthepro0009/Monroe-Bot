# Monroe Social Club Discord Bot

## Overview

This is a Discord bot designed for the Monroe Social Club, a retro 80s beach-themed community with Roblox integration. The bot provides comprehensive moderation tools, automatic content filtering, member applications system, and seamless Roblox group integration. The bot is built with Python using the discord.py library and features a modular architecture with separate cogs for different functionalities.

## System Architecture

The bot follows a modular cog-based architecture using discord.py's extension system:

- **Main Entry Point** (`main.py`): Bot initialization, event handling, and cog loading
- **Configuration Management** (`bot/config.py`): Centralized configuration including tokens, channel IDs, and role mappings
- **Modular Cogs**: Separate modules for different bot functionalities
- **Utility Systems**: Shared embed creation and helper functions

## Key Components

### Core Bot Features
- **Event Handling**: Member join events with custom welcome messages
- **Slash Command Support**: Modern Discord slash commands with automatic syncing
- **Intent Management**: Proper Discord intents for message content, members, and guild access

### Moderation System (`bot/moderation.py`)
- Comprehensive moderation commands (warn, kick, ban)
- Permission-based access control for staff members
- Standardized moderation logging with rich embeds
- Image attachment support for moderation actions

### Automoderation (`bot/automod.py`)
- Multi-language profanity detection using better-profanity library
- Language detection with langdetect
- Comprehensive bad words list covering multiple languages
- Automatic content filtering and logging

### Roblox Integration (`bot/roblox_integration.py`)
- Rover API integration for Discord-to-Roblox account linking
- Roblox user profile fetching and display
- Avatar headshot integration
- Group information display

### Applications System (`bot/applications.py`)
- Modal-based application forms for Staff and Security roles
- Multi-question application process including age, experience, timezone, availability, and motivation
- Structured application data collection

### Utility Functions (`bot/utils.py`)
- Comprehensive help command system
- Standardized embed creation
- Common utility functions for bot operations

### Embed System (`bot/embeds.py`)
- Standardized embed creation for moderation actions
- Welcome message embeds with 80s beach theme
- Consistent branding and formatting across all bot messages

## Data Flow

1. **Message Processing**: Discord messages are processed through automod filters before being displayed
2. **Command Execution**: Slash commands are processed with permission checks and logged appropriately
3. **Moderation Actions**: Staff actions are logged to dedicated channels with rich embed formatting
4. **Roblox Integration**: Discord user data is cross-referenced with Roblox accounts via Rover API
5. **Application Processing**: User applications are collected via modals and processed for staff review

## External Dependencies

### Python Packages
- **discord.py**: Primary Discord bot framework
- **aiohttp**: Async HTTP client for API requests
- **better-profanity**: Advanced profanity filtering
- **langdetect**: Language detection for multi-language content moderation

### External APIs
- **Rover API**: Discord-to-Roblox account linking service
- **Roblox API**: User information and avatar fetching
- **Discord API**: All bot interactions and messaging

### Configuration Requirements
- **Discord Bot Token**: Required for bot authentication
- **Channel IDs**: Specific channels for logging, announcements, and applications
- **Role IDs**: Staff and security role configuration
- **Roblox Group ID**: Group integration configuration

## Deployment Strategy

The bot is designed for deployment on Replit with the following characteristics:

- **Python 3.11 Runtime**: Specified in .replit configuration
- **Automatic Dependency Installation**: Dependencies installed via pip during startup
- **Environment Variables**: Bot token and sensitive data stored as environment variables
- **Persistent Operation**: Designed to run continuously with proper error handling
- **Modular Loading**: Cogs can be loaded/unloaded dynamically for maintenance

### Deployment Configuration
- Uses Replit's workflow system for automated startup
- Parallel workflow execution for optimal performance
- Automatic dependency resolution with pyproject.toml and uv.lock

## Changelog

- June 26, 2025: Major bot enhancement and hosting compatibility update
  - Translated admin logging system to English for international management team
  - Enhanced automod with AI detection capabilities (ChatGPT, Claude, Bard patterns, prompt injection attempts)
  - Added Render hosting service compatibility with health check endpoints and PORT environment variable support
  - Implemented UptimeRobot monitoring compatibility with /health endpoint
  - Created custom embed system for management with modal-based creation (title, description, fields, colors, author, images, footer)
  - Fixed rich presence Roblox integration with proper universe ID resolution and clickable game links
  - Added requirements.txt and render.yaml for seamless Render deployment
  - Enhanced Roblox game integration with visit counters and improved presence display
  - Extended profanity detection with AI-generated content patterns and suspicious AI behavior detection
  - Comprehensive bot with 24 slash commands including new custom embed creation for management only

## User Preferences

Preferred communication style: Simple, everyday language.