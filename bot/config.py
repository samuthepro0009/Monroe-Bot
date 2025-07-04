import os
import discord

class Config:
    # =============================================================================
    # BOT CORE CONFIGURATION
    # =============================================================================
    
    # Discord Bot Token (stored as environment variable for security)
    BOT_TOKEN = os.getenv("DISCORD_TOKEN")
    
    # Bot activity and status settings
    BOT_STATUS = discord.Status.online
    BOT_ACTIVITY_TYPE = discord.ActivityType.watching
    BOT_ACTIVITY_NAME = "Monroe Social Club 🌴"
    
    # Bot command prefix (for legacy commands if needed)
    BOT_PREFIX = "!"
    
    # =============================================================================
    # SERVER & CHANNEL CONFIGURATION
    # =============================================================================
    
    # Channel IDs
    MODERATION_LOG_CHANNEL = 1353388424295350283  # Replace with actual channel ID
    AUTOMOD_LOG_CHANNEL = 1353388424295350283     # Replace with actual channel ID
    ANNOUNCEMENT_CHANNEL = 1353388424295350283    # Replace with actual channel ID
    APPLICATION_LOG_CHANNEL = 1353388424295350283  # Replace with actual channel ID
    DEVLOG_CHANNEL = 1353388424295350283          # Replace with actual channel ID
    
    # Public Channels
    ANNOUNCEMENT_CHANNEL = 1353388424295350283
    DEVLOG_CHANNEL = 1353388489915502737
    WELCOME_CHANNEL_ID = 1353409299636031610
    QOTD_CHAT_REVIVE_CHANNEL = 1353301751050014824
    
    # Broadcast channels for dashboard announcements
    BROADCAST_CHANNELS = [1353388424295350283, 1353388489915502737]
    
    # =============================================================================
    # STAFF & ROLE CONFIGURATION
    # =============================================================================
    
    # Management team configuration
    MANAGEMENT_ROLES = {
        "Chairman": "Samu",
        "Vice Chairman": "Luca", 
        "President": "Fra",
        "Vice President": "Rev"
    }
    
    # Role IDs
    STAFF_ROLES = [
        1353388424295350283,  # Replace with actual staff role IDs
        1353388424295350284,
    ]
    SECURITY_ROLES = []  # Add actual security role IDs here
    ADMIN_ROLES = []  # Add actual admin role IDs here
    
    # =============================================================================
    # ROBLOX INTEGRATION CONFIGURATION
    # =============================================================================
    
    # Roblox Group and Game Settings
    ROBLOX_GROUP_ID = 35828136
    ROBLOX_MAP_ID = 80340506584377
    ROBLOX_GAME_LINK = "https://www.roblox.com/games/your-game-id"
    ROVER_API_BASE = "https://registry.rover.link/api"
    
    # =============================================================================
    # MODERATION CONFIGURATION
    # =============================================================================
    
    # Auto-moderation settings
    AUTOMOD_ENABLED = True
    SPAM_DETECTION_ENABLED = True
    CAPS_DETECTION_ENABLED = True
    LINK_DETECTION_ENABLED = True
    
    # Spam detection thresholds
    SPAM_MESSAGE_COUNT = 5
    SPAM_TIME_WINDOW = 10  # seconds
    SPAM_PUNISHMENT_DURATION = 300  # 5 minutes timeout
    
    # Caps detection settings
    CAPS_THRESHOLD = 0.7  # 70% caps
    CAPS_MIN_LENGTH = 10  # minimum message length to check
    
    # Suspicious activity detection
    SUSPICIOUS_ACTIVITY_ENABLED = True
    RAID_DETECTION_THRESHOLD = 5  # users joining within time window
    RAID_DETECTION_TIME_WINDOW = 30  # seconds
    
    # Server Rules
    SERVER_RULES = {
        "1.1": "No Spamming - Avoid sending repetitive messages or excessive content",
        "1.2": "No Inappropriate Content - Keep all content family-friendly and appropriate",
        "1.3": "No Harassment - Treat all members with respect and kindness",
        "1.4": "No Self-Promotion - Avoid advertising other servers or content without permission",
        "1.5": "Use Appropriate Channels - Post content in the correct channels",
        "2.1": "No NSFW Content - Absolutely no adult content allowed",
        "2.2": "No Hate Speech - Zero tolerance for discriminatory language",
        "2.3": "No Doxxing - Never share personal information of others",
        "2.4": "No Impersonation - Don't pretend to be someone else",
        "2.5": "No Bypassing Moderation - Don't attempt to circumvent bans or mutes",
        "3.1": "No Raiding - Organizing attacks on other servers is prohibited",
        "3.2": "No Malicious Links - Don't share harmful or dangerous links",
        "3.3": "No Bot Abuse - Don't spam bot commands or attempt to break the bot",
        "3.4": "No Alt Accounts - Using alternate accounts to bypass punishments is forbidden",
        "3.5": "Follow Discord ToS - All Discord Terms of Service apply"
    }
    
    # =============================================================================
    # CONTENT & ENGAGEMENT CONFIGURATION
    # =============================================================================
    
    # Question of the Day (QOTD) system
    QOTD_ENABLED = True
    QOTD_QUESTIONS = [
        "What's your favorite 80s movie and why?",
        "If you could have dinner with any celebrity from the 80s, who would it be?",
        "What's your go-to karaoke song from the 80s?",
        "Describe your dream 80s beach party!",
        "What's the most iconic 80s fashion trend in your opinion?",
        "If you could time travel to the 80s, what would you do first?",
        "What's your favorite 80s song to dance to?",
        "Which 80s TV show would you want to be in?",
        "What's the best 80s snack or drink?",
        "If you owned a beach club in the 80s, what would you name it?",
        "What's your favorite 80s video game?",
        "Which 80s hairstyle would you rock?",
        "What's the most memorable 80s commercial you remember?",
        "If you could bring back one 80s trend, what would it be?",
        "What's your favorite 80s cartoon character?"
    ]
    
    # Chat revival messages
    CHAT_REVIVE_ENABLED = True
    CHAT_REVIVE_MESSAGES = [
        "🌊 The waves are calling! Anyone up for some beach vibes?",
        "🎵 What's everyone listening to today? Drop your current song!",
        "🏖️ Beach day activities - what's your favorite?",
        "🕶️ Sunglasses check! Show us your coolest pair!",
        "🌴 Palm trees swaying, good vibes flowing... how's everyone doing?",
        "🎮 Who's ready for some Roblox fun at Monroe Social Club?",
        "💫 Sending good vibes to everyone! What's making you smile today?",
        "🌺 Tropical paradise mood! Share something that makes you happy!",
        "🎨 Creative minds unite! What's your latest hobby or interest?",
        "🎪 Weekend vibes (even if it's not weekend)! What are your plans?",
        "🌈 Color your day bright! What's your favorite color combo?",
        "🎭 If you could have any superpower, what would it be?",
        "🎸 Music therapy time! What song describes your mood right now?",
        "🎯 Goal setting! What's one thing you want to accomplish this week?",
        "🎊 Celebration time! What's something you're proud of lately?"
    ]
    
    # =============================================================================
    # ANNOUNCEMENT TEMPLATES CONFIGURATION
    # =============================================================================
    
    # Available announcement templates
    ANNOUNCEMENT_TEMPLATES = {
        "event": {
            "title": "🎉 Upcoming Event",
            "color": 0xFF69B4,  # Hot pink
            "emoji": "🎉"
        },
        "update": {
            "title": "📢 Important Update",
            "color": 0x00CED1,  # Dark turquoise
            "emoji": "📢"
        },
        "maintenance": {
            "title": "🔧 Maintenance Notice",
            "color": 0xFFFF00,  # Yellow
            "emoji": "🔧"
        },
        "celebration": {
            "title": "🎊 Celebration Time",
            "color": 0x9932CC,  # Dark orchid
            "emoji": "🎊"
        },
        "welcome": {
            "title": "🌴 Welcome Notice",
            "color": 0x00FF00,  # Lime green
            "emoji": "🌴"
        },
        "rules": {
            "title": "📋 Rules Reminder",
            "color": 0xFF4500,  # Orange red
            "emoji": "📋"
        },
        "partnership": {
            "title": "🤝 Partnership Announcement",
            "color": 0x4169E1,  # Royal blue
            "emoji": "🤝"
        },
        "giveaway": {
            "title": "🎁 Giveaway Alert",
            "color": 0xFFD700,  # Gold
            "emoji": "🎁"
        }
    }
    
    # =============================================================================
    # ASCII ART CONFIGURATION
    # =============================================================================
    
    # ASCII Art collection for commands
    ASCII_ART = {
        "waves": """
🌊 ～～～～～～～～～～～～～ 🌊
   ～～～～～～～～～～～～
🌊 ～～～～～～～～～～～～～ 🌊
        """,
        "palm": """
        🌴
       /|\\
      / | \\
        |
        |
    ________
        """,
        "sunset": """
    🌅 ～～～～～～～～～ 🌅
       \\  |  /
        \\ | /
         \\|/
    ～～～～～～～～～～～～～
        """,
        "beach": """
🏖️ ～～～～～～～～～～～～～ 🏖️
    🌴     ☀️     🌴
       ～～～～～～～
    🏄‍♂️ ～～～～～～～ 🏄‍♀️
        """,
        "party": """
🎉 ～～～ PARTY TIME ～～～ 🎉
    🕺 💃 🕺 💃 🕺 💃
    🎵 ♪ ♫ ♪ ♫ ♪ ♫ 🎵
🎊 ～～～～～～～～～～～～～ 🎊
        """,
        "retro": """
📼 ～～～ 80s VIBES ～～～ 📼
    🕶️ 📻 🎮 💿 📞
    ▓▒░ NEON LIGHTS ░▒▓
🌃 ～～～～～～～～～～～～～ 🌃
        """,
        "welcome": """
🌴 ～～ WELCOME TO ～～ 🌴
   MONROE SOCIAL CLUB
    🏖️ ～～～～～～～ 🏖️
      80s Beach Paradise
🌊 ～～～～～～～～～～～～～ 🌊
        """,
        "logo": """
███╗   ███╗███████╗ ██████╗
████╗ ████║██╔════╝██╔════╝
██╔████╔██║███████╗██║     
██║╚██╔╝██║╚════██║██║     
██║ ╚═╝ ██║███████║╚██████╗
╚═╝     ╚═╝╚══════╝ ╚═════╝
    Monroe Social Club
        """
    }
    
    # =============================================================================
    # ACTIVITY LEADERBOARD CONFIGURATION
    # =============================================================================
    
    # Activity tracking settings
    LEADERBOARD_ENABLED = True
    LEADERBOARD_RESET_WEEKLY = True
    LEADERBOARD_MAX_ENTRIES = 10
    
    # Point values for different activities
    ACTIVITY_POINTS = {
        "message": 1,
        "reaction_given": 1,
        "reaction_received": 2,
        "voice_minute": 2,
        "command_used": 1,
        "thread_created": 5,
        "event_participation": 10
    }
    
    # =============================================================================
    # API & WEB SERVER CONFIGURATION
    # =============================================================================
    
    # Web server settings
    API_ENABLED = True
    API_PORT = int(os.getenv('PORT', 8000))
    API_HOST = "0.0.0.0"
    
    # Dashboard authentication
    DASHBOARD_SECRET_KEY = os.getenv("DASHBOARD_SECRET", "monroe-secret-key-2024")
    
    # Health check settings
    HEALTH_CHECK_ENABLED = True
    HEALTH_CHECK_PATH = "/health"
    
    # =============================================================================
    # VISUAL & THEME CONFIGURATION
    # =============================================================================
    
    # Colors
    COLORS = {
        "success": 0x00ff00,
        "error": 0xff0000,
        "warning": 0xffa500,
        "info": 0x00bfff,
        "purple": 0x7c3aed,
        "pink": 0xff69b4
    }
    
    # Admin logging colors by action type
    LOG_COLORS = {
        "member_join": 0x00FF00,      # Green - positive action
        "member_leave": 0xFF8C00,     # Orange - neutral/warning
        "member_ban": 0xFF0000,       # Red - negative action
        "member_kick": 0xFF4500,      # Red-orange - negative action
        "message_delete": 0xFFFF00,   # Yellow - attention needed
        "command_used": 0x00CED1,     # Cyan - informational
        "thread_create": 0x9932CC,    # Purple - thread actions
        "thread_delete": 0x8B0000,    # Dark red - thread deletion
        "voice_join": 0x32CD32,       # Lime green - voice activity
        "voice_leave": 0xFFA500,      # Orange - voice activity
        "role_update": 0x4169E1,      # Royal blue - role changes
        "nickname_change": 0xDDA0DD,  # Plum - profile changes
        "message_edit": 0xFFD700      # Gold - message modifications
    }
    
    # =============================================================================
    # HOSTING & DEPLOYMENT CONFIGURATION
    # =============================================================================
    
    # Hosting platform information
    HOSTING_PLATFORM = "Replit"
    HOSTING_URL = "https://replit.com"
    BOT_VERSION = "2.0.0"
    BOT_UPTIME_24_7 = True
    
    # =============================================================================
    # DEBUG & DEVELOPMENT CONFIGURATION
    # =============================================================================
    
    # Debug settings
    DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"
    VERBOSE_LOGGING = os.getenv("VERBOSE_LOGGING", "False").lower() == "true"
    
    # Development features
    DEV_GUILD_ID = None  # Set to guild ID for faster command sync during development
    
    # =============================================================================
    # SAFETY & SECURITY CONFIGURATION
    # =============================================================================
    
    # Rate limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_COMMANDS_PER_MINUTE = 30
    
    # Content filtering
    CONTENT_FILTER_ENABLED = True
    NSFW_DETECTION_ENABLED = True
    
    # Backup and recovery
    AUTO_BACKUP_ENABLED = False  # Set to True if you want automatic backups
    BACKUP_FREQUENCY_HOURS = 24
    
    # =============================================================================
    # FEATURE FLAGS
    # =============================================================================
    
    # Enable/disable major features
    FEATURES = {
        "moderation": True,
        "automod": True,
        "suspicious_activity": True,
        "announcement_templates": True,
        "ascii_art": True,
        "activity_leaderboard": True,
        "admin_logging": True,
        "roblox_integration": True,
        "qotd_system": True,
        "utils_commands": True,
        "rich_presence": True,
        "web_api": True,
        "dashboard_integration": True
    }