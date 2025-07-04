import discord
from discord.ext import commands
import re
from bot.config import Config
from better_profanity import profanity
from langdetect import detect, DetectorFactory, LangDetectException

# Set seed for consistent language detection
DetectorFactory.seed = 0

class AutomodCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Initialize profanity filter
        profanity.load_censor_words()

        # Smart moderation patterns
        self.spam_patterns = {
            'excessive_caps': r'[A-Z]{10,}',
            'excessive_punctuation': r'[!?]{5,}',
            'repeated_chars': r'(.)\1{5,}',
            'mass_mentions': r'<@[!&]?\d+>',
            'suspicious_links': r'(discord\.gg|bit\.ly|tinyurl|t\.co)\/\w+',
            'zalgo_text': r'[\u0300-\u036f\u1ab0-\u1aff\u1dc0-\u1dff\u20d0-\u20ff\ufe20-\ufe2f]',
            'excessive_emojis': r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]{10,}'
        }

        # Context-aware detection
        self.context_keywords = {
            'trading': ['trade', 'selling', 'buying', 'robux', 'limiteds', 'cheap', 'free robux'],
            'scam': ['free', 'giveaway', 'winner', 'click here', 'dm me', 'trust trade'],
            'advertising': ['join my', 'check out', 'subscribe', 'follow me', 'my channel', 'my server'],
            'begging': ['please give', 'can i have', 'donate', 'gift me', 'spare robux']
        }

        # Extended bad words list including multiple languages and AI detection
        self.bad_words = [
            # English profanity
            'fuck', 'fucking', 'fucked', 'fucker', 'shit', 'shitting', 'bitch', 'bitches', 
            'damn', 'damned', 'hell', 'ass', 'asses', 'asshole', 'piss', 'crap', 'crappy',
            'bastard', 'slut', 'sluts', 'whore', 'whores', 'retard', 'retarded', 'faggot', 
            'nigger', 'nigga', 'cunt', 'cunts', 'pussy', 'cock', 'dick', 'penis',
            # AI Detection patterns
            'chatgpt', 'openai', 'claude', 'bard', 'gemini', 'copilot', 'midjourney', 'stable diffusion',
            'dall-e', 'gpt-4', 'gpt-3', 'artificial intelligence', 'machine learning', 'neural network',
            'deep learning', 'transformer', 'language model', 'llm', 'ai assistant', 'bot response',
            'generated content', 'synthetic text', 'automated response', 'algorithm', 'data training',
            'prompt injection', 'jailbreak', 'system prompt', 'ignore previous', 'act as if',
            'pretend you are', 'roleplay as', 'simulate', 'emulate', 'mimic behavior',
            'as an ai', 'i am an ai', "i'm an ai", 'i cannot', "i'm not able", "i'm designed to",
            'my purpose is', 'i was created', 'my training', 'safety guidelines', 'content policy',
            'i shouldn\'t', 'that would be inappropriate', "i'm programmed", 'my developers', 'my creators',
            # Spanish profanity
            'puta', 'putas', 'mierda', 'coño', 'joder', 'cabron', 'cabrón', 'pendejo', 
            'idiota', 'estupido', 'estúpido', 'maricon', 'maricón', 'hijo de puta', 
            'chinga', 'pinche', 'verga', 'carajo',
            # Italian profanity
            'merda', 'cazzo', 'stronzo', 'puttana', 'figa', 'troia', 'bastardo',
            'idiota', 'coglione', 'porco dio', 'madonna', 'fanculo', 'vaffanculo',
            # French profanity
            'merde', 'putain', 'salope', 'con', 'connard', 'enculé', 'fils de pute',
            'bordel', 'chier', 'pute', 'bite', 'couille', 'connasse',
            # German profanity
            'scheiße', 'scheisse', 'verdammt', 'arschloch', 'hurensohn', 'fotze', 
            'schwuchtel', 'mistkerl', 'blödmann', 'scheißer', 'wichser',
            # Portuguese profanity  
            'merda', 'porra', 'caralho', 'puta', 'filho da puta', 'buceta',
            'cu', 'cuzão', 'desgraça', 'otário', 'cacete',
            # Russian profanity (transliterated)
            'blyad', 'blyat', 'suka', 'pizdec', 'hui', 'govno', 'mudak', 'debil',
            'urod', 'gavno', 'zasranec', 'chmo', 'dolbaeb',
            # Slurs and hate speech
            'tranny', 'dyke', 'kike', 'spic', 'chink', 'gook', 'towelhead',
            'raghead', 'wetback', 'beaner', 'cracker', 'honkey', 'fag'
        ]

        # Add custom words to profanity filter
        profanity.add_censor_words(self.bad_words)

    def contains_profanity(self, text):
        """Check if text contains profanity using multiple methods"""
        text_lower = text.lower()

        # Method 1: Direct word matching
        for word in self.bad_words:
            if word in text_lower:
                return True, word

        # Method 2: Better-profanity library check
        if profanity.contains_profanity(text):
            # Find the specific profane word
            words = text.split()
            for word in words:
                if profanity.contains_profanity(word):
                    return True, word.lower()

        # Method 3: Pattern matching for variations (with numbers, symbols)
        for word in self.bad_words:
            # Create pattern that allows character substitution
            pattern = word
            pattern = pattern.replace('a', '[a@4]')
            pattern = pattern.replace('e', '[e3]')
            pattern = pattern.replace('i', '[i1!]')
            pattern = pattern.replace('o', '[o0]')
            pattern = pattern.replace('s', '[s5$]')
            pattern = pattern.replace('t', '[t7]')

            if re.search(pattern, text_lower):
                return True, word

        return False, None

    def detect_spam_patterns(self, text):
        """Detect spam patterns in text"""
        detected_patterns = []

        for pattern_name, pattern in self.spam_patterns.items():
            if re.search(pattern, text):
                detected_patterns.append(pattern_name)

        return detected_patterns

    def detect_context_violations(self, text):
        """Detect context-based violations"""
        text_lower = text.lower()
        detected_contexts = []

        for context, keywords in self.context_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches >= 2:  # Require at least 2 matching keywords
                detected_contexts.append(context)

        return detected_contexts

    def calculate_message_score(self, message):
        """Calculate a risk score for the message"""
        score = 0
        factors = []

        # Length factors
        if len(message.content) > 1000:
            score += 2
            factors.append("very_long_message")

        # Mention factors
        mention_count = len(message.mentions)
        if mention_count > 5:
            score += 3
            factors.append("excessive_mentions")
        elif mention_count > 2:
            score += 1
            factors.append("multiple_mentions")

        # Caps ratio
        if message.content:
            caps_ratio = sum(1 for c in message.content if c.isupper()) / len(message.content)
            if caps_ratio > 0.7:
                score += 2
                factors.append("excessive_caps")

        # Spam patterns
        spam_patterns = self.detect_spam_patterns(message.content)
        score += len(spam_patterns)
        factors.extend(spam_patterns)

        # Context violations
        context_violations = self.detect_context_violations(message.content)
        score += len(context_violations) * 2
        factors.extend(context_violations)

        return score, factors

    def detect_language(self, text):
        """Detect the language of the text"""
        try:
            return detect(text)
        except (LangDetectException, Exception):
            return "unknown"

    def contains_profanity(self, text):
        """Check if text contains profanity"""
        try:
            # Check using better-profanity
            if profanity.contains_profanity(text):
                # Find the specific word
                words = text.split()
                for word in words:
                    if profanity.contains_profanity(word):
                        return True, word
                return True, "detected"
            return False, None
        except Exception as e:
            print(f"❌ Error checking profanity: {e}")
            return False, None

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages and DMs
        if message.author.bot or not message.guild:
            return

        # Don't ignore any user messages - check all content

        # Check for profanity
        contains_bad_word, detected_word = self.contains_profanity(message.content)

        if contains_bad_word:
            # Delete the message
            try:
                await message.delete()
            except discord.NotFound:
                pass  # Message already deleted
            except discord.Forbidden:
                pass  # No permission to delete

            # Get automod log channel
            log_channel = self.bot.get_channel(Config.AUTOMOD_LOG_CHANNEL)
            if not log_channel:
                return

            # Detect language
            detected_language = self.detect_language(message.content)

            # Create detailed log embed
            embed = discord.Embed(
                title="🚫 AutoMod Detection",
                description="Inappropriate content detected and removed",
                color=Config.COLORS["error"]
            )

            # User information
            embed.add_field(
                name="👤 User Information",
                value=f"**User:** {message.author.mention}\n**Username:** {message.author.name}#{message.author.discriminator}\n**User ID:** {message.author.id}",
                inline=False
            )

            # Message information
            embed.add_field(
                name="📝 Message Details",
                value=f"**Channel:** {message.channel.mention}\n**Message ID:** {message.id}\n**Timestamp:** <t:{int(message.created_at.timestamp())}:F>",
                inline=False
            )

            # Content information
            embed.add_field(
                name="🔍 Detection Details",
                value=f"**Detected Word:** `{detected_word}`\n**Language:** {detected_language.upper()}\n**Full Message:** `{message.content[:500]}{'...' if len(message.content) > 500 else ''}`",
                inline=False
            )

            # Additional information
            embed.add_field(
                name="📊 Additional Info",
                value=f"**Message Length:** {len(message.content)} characters\n**Word Count:** {len(message.content.split())} words\n**Channel ID:** {message.channel.id}",
                inline=False
            )

            # Set user avatar as thumbnail
            embed.set_thumbnail(url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)

            # Footer with bot info
            embed.set_footer(
                text="Monroe Social Club - AutoMod System",
                icon_url=self.bot.user.avatar.url
            )
            embed.timestamp = discord.utils.utcnow()

            # Send log embed
            await log_channel.send(embed=embed)

            # Send public warning message in the same channel
            warning_messages = [
                "🏖️ Keep it family friendly!",
                "🌴 Watch your language!",
                "☀️ Let's keep our beach vibes positive!",
                "🌊 Please respect our community rules!",
                "🕶️ That language doesn't match our 80s beach vibe!"
            ]

            import random
            warning_msg = random.choice(warning_messages)

            try:
                warning_embed = discord.Embed(
                    description=f"{message.author.mention} {warning_msg}",
                    color=Config.COLORS["warning"]
                )
                await message.channel.send(embed=warning_embed, delete_after=10)
            except discord.Forbidden:
                pass

            # Also send DM
            try:
                dm_embed = discord.Embed(
                    title="⚠️ Message Removed",
                    description="Your message was removed for containing inappropriate content.",
                    color=Config.COLORS["warning"]
                )
                dm_embed.add_field(
                    name="📝 Reason",
                    value="Inappropriate language detected",
                    inline=False
                )
                dm_embed.add_field(
                    name="🌴 Monroe Social Club Rules",
                    value="Please keep our beach club family-friendly and respectful!",
                    inline=False
                )
                dm_embed.set_footer(text="This is an automated message")

                await message.author.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled

async def setup(bot):
    await bot.add_cog(AutomodCog(bot))

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Check edited messages for profanity too"""
        # Only check if content actually changed
        if before.content != after.content:
            await self.on_message(after)

class AutoModerationSystem:
    async def on_message(self, message):
        """Centralized message monitoring"""
        # Implement sophisticated moderation logic here
        pass

class AutoModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.automod = AutoModerationSystem()
        print(f"🛡️ AutoModerationCog initialized")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Monitor messages for inappropriate content"""
        # Delegate to the AutoModerationSystem
        await self.automod.on_message(message)

async def setup(bot):
    await bot.add_cog(AutoModerationCog(bot))