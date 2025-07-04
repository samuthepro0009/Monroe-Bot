
# =============================================================================
# MONROE SOCIAL CLUB BOT - UNIFIED CONFIGURATION
# =============================================================================
# This file contains ALL configuration options for the Monroe Social Club bot.
# Sections are clearly marked for easy navigation and maintenance.
# =============================================================================

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
    
    # Logging Channels
    AUTOMOD_LOG_CHANNEL = 1357714336356761662
    MODERATION_LOG_CHANNEL = 1353388676981456917
    ADMIN_LOG_CHANNEL = 1387524238117830776
    APPLICATION_LOG_CHANNEL = 1357714351280361472
    
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
    
    # Staff role IDs (configure these with actual role IDs)
    STAFF_ROLES = []  # Add actual staff role IDs here
    SECURITY_ROLES = []  # Add actual security role IDs here
    ADMIN_ROLES = []  # Add actual admin role IDs here
    
    # =============================================================================
    # ROBLOX INTEGRATION CONFIGURATION
    # =============================================================================
    
    # Roblox Group and Game Settings
    ROBLOX_GROUP_ID = 35828136
    ROBLOX_MAP_ID = 80340506584377
    ROBLOX_GAME_LINK = "https://www.roblox.com/games/80340506584377/Monroe-Social-Club"
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
    
    # Server rules with severity levels
    SERVER_RULES = {
        # Gravità 1 – Chat
        "1.1.1": "Caps Abuse – Excessive use of ALL CAPS in messages",
        "1.1.2": "Spoilers – Posting spoilers without proper tags or warnings",
        "1.1.3": "Emoji/Sticker Abuse – Overusing or misusing custom emojis/stickers",
        "1.1.4": "Language Violation – Using a language not permitted in public chats",
        "1.1.5": "Ghost Pings – Mentioning users then deleting the message to annoy",
        "1.1.6": "Backseat Moderation – Trying to enforce rules without being staff",
        "1.1.7": "Inappropriate Nicknames – Offensive or misleading nicknames",

        # Gravità 1 – Voice
        "1.2.1": "Mic Spam – Background noise or minor disruption in voice chats",
        "1.2.2": "Unnecessary Soundboard Use – Mild misuse of audio tools",

        # Gravità 1 – Gioco
        "1.3.1": "Minor Fail RP – Small unrealistic or off-character actions",
        "1.3.2": "Breaking Character – Light disruptions of RP immersion",

        # Gravità 2 – Chat
        "2.1.1": "Spam – Repetitive messages, emojis, or bot commands",
        "2.1.2": "Flaming – Hostile arguments or provoking others",
        "2.1.3": "Toxic Behavior – Negative or aggressive conduct in chat",
        "2.1.4": "Malicious Links – Sharing misleading or unsafe URLs",
        "2.1.5": "Advertising – Promoting external content without permission",
        "2.1.6": "Fake Reports – Submitting false claims to staff",
        "2.1.7": "Impersonation – Pretending to be others, especially staff",
        "2.1.8": "Inappropriate Jokes – Sensitive jokes about trauma, suicide, etc.",

        # Gravità 2 – Voice
        "2.2.1": "Loud Noises – Shouting, static, or other disruptions in VC",
        "2.2.2": "Soundboard Misuse – Inappropriate or repeated use of audio clips",
        "2.2.3": "Camera Misuse – Using a webcam inappropriately",

        # Gravità 2 – Gioco
        "2.3.1": "Fail RP – Unrealistic or trollish behavior in RP",
        "2.3.2": "Metagaming – Using OOC info to gain IC advantage",
        "2.3.3": "Powergaming – Forcing actions onto others in RP",
        "2.3.4": "ERP – Erotic or suggestive roleplay (zero tolerance)",
        "2.3.5": "Application Abuse – Joke or troll answers in applications",
        "2.3.6": "Late Event Entry – Joining RP or applications after deadline",
        "2.3.7": "Unfair Advantage – Exploiting bugs, glitches or favoritism",

        # Gravità 3 – Chat
        "3.1.1": "Slurring – Use of hateful or racist slurs",
        "3.1.2": "Harassment – Targeting or bullying individuals repeatedly",
        "3.1.3": "Discrimination – Hate based on race, gender, religion, etc.",
        "3.1.4": "NSFW Content – Posting pornographic or disturbing content",
        "3.1.5": "Security Threats – Discussing or engaging in hacking/exploiting",
        "3.1.6": "Ban Evasion – Using alts/VPNs to bypass punishments",
        "3.1.7": "Leaking Internal Info – Sharing private staff/server data",
        "3.1.8": "Staff Disrespect – Openly ignoring or attacking staff decisions",
        "3.1.9": "Incitement – Promoting hate, violence, or illegal actions",
        "3.1.10": "Doxxing – Sharing personal/private information without consent",

        # Gravità 3 – Voice
        "3.2.1": "Major VC Disruption – Coordinated trolling or aggressive behavior in VC",
        "3.2.2": "Screen Sharing NSFW – Sharing graphic or rule-breaking content in VC",
        "3.2.3": "Raiding VC – Organized disruption via multiple users in VC",

        # Gravità 3 – Gioco
        "3.3.1": "Major Fail RP – Extremely unrealistic or immersion-breaking actions",
        "3.3.2": "Griefing Events – Disrupting serious RP or events intentionally",
        "3.3.3": "Alt Abuse – Using alternate accounts in RP/games to gain advantage",
        "3.3.4": "ERP (Severe) – Explicit RP scenes or repeat offenses",
        "3.3.5": "Raiding – Coordinated trolling inside game servers"
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
    
    # Color scheme for embeds
    COLORS = {
        "success": 0x00FF00,      # Bright green
        "error": 0xFF0000,        # Bright red
        "warning": 0xFFFF00,      # Bright yellow
        "info": 0x00CED1,         # Dark turquoise
        "pink": 0xFF69B4,         # Hot pink
        "purple": 0x9932CC,       # Dark orchid
        "blue": 0x4169E1,         # Royal blue
        "orange": 0xFF4500,       # Orange red
        "gold": 0xFFD700,         # Gold
        "lime": 0x00FF00,         # Lime green
        "cyan": 0x00FFFF,         # Cyan
        "magenta": 0xFF00FF       # Magenta
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
