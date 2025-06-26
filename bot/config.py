import os

class Config:
    # Bot token
    BOT_TOKEN = os.getenv("DISCORD_TOKEN", "MTM4NzE4NzUzNDE4MTY5NTUxOQ.GadTe-.lsq13H7nsI6D6q-Xyuk9NgiDxiC2PdzZ_nnpko")
    
    # Channel IDs
    AUTOMOD_LOG_CHANNEL = 1357714336356761662
    MODERATION_LOG_CHANNEL = 1353388676981456917
    ANNOUNCEMENT_CHANNEL = 1353388424295350283
    DEVLOG_CHANNEL = 1353388489915502737
    APPLICATION_LOG_CHANNEL = 1357714351280361472
    WELCOME_CHANNEL_ID = 1353409299636031610
    QOTD_CHAT_REVIVE_CHANNEL = 1353301751050014824
    ADMIN_LOG_CHANNEL = 1387524238117830776
    
    # Roblox Integration
    ROBLOX_GROUP_ID = 35828136
    ROBLOX_MAP_ID = 80340506584377
    ROVER_API_BASE = "https://registry.rover.link/api"
    
    # Management team roles
    MANAGEMENT_ROLES = {
        "Chairman": "Samu",
        "Vice Chairman": "Luca", 
        "President": "Fra",
        "Vice President": "Rev"
    }
    
    # Staff role IDs (to be configured by server admin)
    STAFF_ROLES = []  # Add actual role IDs here
    SECURITY_ROLES = []  # Add actual role IDs here
    
    # Roblox game link
    ROBLOX_GAME_LINK = "https://www.roblox.com/games/80340506584377/Monroe-Social-Club"
    
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

    
    # QOTD and Chat Revive messages
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
    
    # Colors for embeds
    COLORS = {
        "success": 0x00FF00,
        "error": 0xFF0000,
        "warning": 0xFFFF00,
        "info": 0x00CED1,
        "pink": 0xFF69B4,
        "purple": 0x9932CC
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
