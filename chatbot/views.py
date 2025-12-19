import os, re, json, threading, asyncio, time
from django.conf import settings
from datetime import datetime
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
import random
from .models import ChatSession # Import new model

def privacy_policy(request):
    """Renders the Privacy Policy page."""
    return render(request, 'privacy.html')

def terms_conditions(request):
    """Renders the Terms & Conditions page."""
    return render(request, 'terms.html')

# Conditional import for edge_tts
EDGE_TTS_AVAILABLE = False
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    print("edge_tts not available; TTS functionality disabled.")
# Conditional import for langchain
LANGCHAIN_AVAILABLE = False
ChatGoogleGenerativeAI = None
ChatPromptTemplate = None
StrOutputParser = None
RunnableSequence = None
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnableSequence
    LANGCHAIN_AVAILABLE = True
    print("Langchain imports successful.")
except ImportError as e:
    print(f"Langchain not available ({e}); AI functionality disabled. Install via: pip install langchain-google-genai langchain-core")
# ================= STATIC PATHS =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_PATH = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_PATH, exist_ok=True)
PREFERRED_LANG_FILE = os.path.join(STATIC_PATH, "preferred_lang.json") # Keep lang per file (global, or make per-user if needed)
KNOWLEDGE_FILE = os.path.join(STATIC_PATH, "knowledgebase.txt")
# ================= CONFIG ========================
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
GEMINI_API_KEY_2 = settings.GEMINI_API_KEY_2
GEMINI_API_KEY_3 = settings.GEMINI_API_KEY_3
GEMINI_API_KEY_4 = settings.GEMINI_API_KEY_4
GEMINI_API_KEY_5 = settings.GEMINI_API_KEY_5
GEMINI_API_KEY_6 = settings.GEMINI_API_KEY_6
GEMINI_API_KEY_7 = settings.GEMINI_API_KEY_7
GEMINI_API_KEY_8 = settings.GEMINI_API_KEY_8

LOCATION = "Plot No. 447, Jheel Chowk / Jheel Khurenja, Geeta Colony, Delhi – 110031"
STORE_TIMINGS = "Our store is open from 9:00 AM to 8:00 PM, all days."
PHONE_NUMBER = "9310480772 , 8595274234"
MAP_URL = "https://www.google.com/maps?q=Golden+Tree+Garments,+Geeta+Colony,+Delhi+110031"
FB_URL = "https://www.facebook.com/GoldenTreeGarments"
INSTA_URL = "https://www.instagram.com/goldentree_garments/"
YOUTUBE_URL = "https://www.youtube.com/c/goldentreegarments"
# ================= COMMON PHRASES TRANSLATIONS =================
COMMON_PHRASES = {
    "en": {
        "default_greeting": "Hello! How can I help you?",
        "action_performed": " ",
        "how_else": " Let me know how else I can help!",
        "error_reply": "Cannot send audio in whatsapp chatbot. Plz reply as text message ",
        "wait_reply": "Please wait a moment, I'm fetching the best response for you quickly!",
        "how_are_you": "I'm doing great, thanks! Ready to assist with Golden Tree Garments. What can I do for you?",
        "phone_info": "Sure, you can reach us at {phone}. Let me connect you.",
        "map_info": "Our location is {location}. Let me open the map for you.",
        "timings_info": "We are open from 9:00 AM to 8:00 PM every day.",
        "fb_info": "Here's our Facebook page. Let me open it for you.",
        "insta_info": "Here's our Instagram. Let me open it for you.",
        "yt_info": "Here's our YouTube channel. Let me open it for you."
    },
    "hi": {
        "default_greeting": "नमस्ते! मैं आपकी कैसे मदद कर सकती हूँ?",
        "action_performed": "",
        "how_else": " मुझे बताएं मैं और कैसे मदद कर सकती हूं!",
        "error_reply": "मैं आपके उत्तर पर काम कर रही हूँ, कृपया थोड़ा प्रतीक्षा करें। यदि बहुत समय लगे, तो फिर से प्रयास करें!",
        "wait_reply": "कृपया थोड़ा प्रतीक्षा करें, मैं आपके लिए सबसे अच्छा उत्तर जल्दी से ला रही हूँ!",
        "how_are_you": "मैं ठीक हूँ, धन्यवाद! गोल्डन ट्री गारमेंट्स के साथ मदद करने के लिए तैयार। मैं आपके लिए क्या कर सकती हूँ?",
        "phone_info": "हाँ, आप हमें {phone} पर संपर्क कर सकते हैं। मैं आपको जोड़ रही हूँ।",
        "map_info": "हमारा स्थान {location} है। मैं आपके लिए मैप खोल रही हूँ।",
        "timings_info": "हम सुबह नौ बजे से रात आठ बजे तक हर दिन खुले रहते हैं।",
        "fb_info": "यह हमारा फेसबुक पेज है। मैं इसे आपके लिए खोल रही हूँ।",
        "insta_info": "यह हमारा इंस्टाग्राम है। मैं इसे आपके लिए खोल रही हूँ।",
        "yt_info": "यह हमारा यूट्यूब चैनल है। मैं इसे आपके लिए खोल रही हूँ।"
    },
    "es": {
        "default_greeting": "¡Hola! ¿En qué puedo ayudarte?",
        "action_performed": " Acción realizada con éxito.",
        "how_else": " ¡Dime cómo más puedo ayudarte!",
        "error_reply": "Estoy trabajando en tu respuesta, por favor espera un momento. Si tarda mucho, inténtalo de nuevo.",
        "wait_reply": "Por favor, espera un momento, estoy obteniendo la mejor respuesta para ti rápidamente.",
        "how_are_you": "¡Estoy genial, gracias! Listo para ayudar con Golden Tree Garments. ¿Qué puedo hacer por ti?",
        "phone_info": "Claro, puedes contactarnos al {phone}. Te conecto.",
        "map_info": "Nuestra ubicación es {location}. Te abro el mapa.",
        "timings_info": "Estamos abiertos de 9:00 AM a 8:00 PM todos los días.",
        "fb_info": "Aquí está nuestra página de Facebook. Te la abro.",
        "insta_info": "Aquí está nuestro Instagram. Te lo abro.",
        "yt_info": "Aquí está nuestro canal de YouTube. Te lo abro."
    },
    "fr": {
        "default_greeting": "Bonjour ! Comment puis-je vous aider ?",
        "action_performed": " Action effectuée avec succès.",
        "how_else": " Dites-moi comment je peux vous aider davantage !",
        "error_reply": "Je travaille sur votre réponse, veuillez patienter un instant. Si cela prend trop de temps, réessayez.",
        "wait_reply": "Veuillez patienter un instant, je récupère la meilleure réponse pour vous rapidement.",
        "how_are_you": "Je vais bien, merci ! Prêt à aider avec Golden Tree Garments. Que puis-je faire pour vous ?",
        "phone_info": "Bien sûr, vous pouvez nous joindre au {phone}. Je vous connecte.",
        "map_info": "Notre emplacement est {location}. J'ouvre la carte pour vous.",
        "timings_info": "Nous sommes ouverts de 9h00 à 20h00 tous les jours.",
        "fb_info": "Voici notre page Facebook. Je l'ouvre pour vous.",
        "insta_info": "Voici notre Instagram. Je l'ouvre pour vous.",
        "yt_info": "Voici notre chaîne YouTube. Je l'ouvre pour vous."
    },
}
# ================= HELPERS =================
def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[!@#$%^&*()_+|}{\"?><\\[\]~`]", "", text)
    return text.strip()

def load_preferred_lang(default="en"):
    try:
        with open(PREFERRED_LANG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("lang", default)
    except:
        return default

def save_preferred_lang(lang):
    with open(PREFERRED_LANG_FILE, "w", encoding="utf-8") as f:
        json.dump({"lang": lang, "updated": datetime.now().isoformat()}, f, indent=2)

def load_knowledge():
    full_text = ""
    try:
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
            full_text = f.read().strip()
    except FileNotFoundError:
        full_text = ""
    knowledge = {
        "store timings": STORE_TIMINGS,
        "phone number": PHONE_NUMBER,
        "address": LOCATION,
        "facebook": FB_URL,
        "fb": FB_URL,
        "instagram": INSTA_URL,
        "insta": INSTA_URL,
        "youtube": YOUTUBE_URL,
        "yt": YOUTUBE_URL,
        "map": MAP_URL,
        "location": MAP_URL
    }
    return {
        "full_text": full_text,
        "parsed": knowledge
    }

def speak(text, lang="en"):
    if not EDGE_TTS_AVAILABLE:
        print(f"TTS not available for lang: {lang}")
        return

    voices = {
        "en": "en-IN-NeerjaNeural",
        "hi": "hi-IN-SwaraNeural",
        "es": "es-ES-ElviraNeural",
        "fr": "fr-FR-DeniseNeural",
        "de": "de-DE-KatjaNeural",
    }
    voice = voices.get(lang, "hi-IN-SwaraNeural")

    if lang == "hi":
        text = hindi_number_words(text)

    try:
        filename = os.path.join(STATIC_PATH, f"voice_{int(time.time()*1000)}.mp3")
        async def gen_voice():
            communicate = edge_tts.Communicate(text, voice, rate="+8%", pitch="+5Hz")
            await communicate.save(filename)
        asyncio.run(gen_voice())

        def cleanup():
            time.sleep(5)
            try:
                os.remove(filename)
            except OSError:
                pass
        threading.Thread(target=cleanup, daemon=True).start()

        print(f"Golden Tree: Hindi TTS ready - {text[:40]}...")

    except Exception as e:
        print(f"TTS error: {e}")

def hindi_number_words(text):
    replacements = {
        "0": "शून्य", "1": "एक", "2": "दो", "3": "तीन", "4": "चार",
        "5": "पांच", "6": "छह", "7": "सात", "8": "आठ", "9": "नौ",
        "10": "दस", "11": "ग्यारह", "12": "बारह", "13": "तेरह", "14": "चौदह",
        "15": "पंद्रह", "16": "सोलह", "17": "सत्रह", "18": "अठारह", "19": "उन्नीस", "20": "बीस",
        "30": "तीस", "40": "चालीस", "50": "पचास", "60": "साठ", "70": "सत्तर", "80": "अस्सी", "90": "नब्बे", "100": "सौ",
        "1000": "हज़ार", "lakh": "लाख", "crore": "करोड़",
        "₹": "रुपये", "$": "डॉलर", "%": "प्रतिशत", "+91": "प्लस नाइन वन इंडिया"
    }

    text = re.sub(r'\+91(\d{10})', r'प्लस नाइन वन इंडिया \1', text)
    text = re.sub(r'(\d{10})', lambda m: ' '.join([{"0":"शून्य","1":"एक","2":"दो","3":"तीन","4":"चार","5":"पांच","6":"छह","7":"सात","8":"आठ","9":"नौ"}[d] for d in m.group(0)]), text)

    for num, word in replacements.items():
        text = text.replace(num, word)

    return text

def detect_lang(text):
    preferred = load_preferred_lang()
    text_lower = text.lower().strip()
    explicit_switches = {
        "hi": ["hindi mein", "hindi me", "hindi mein bol", "speak in hindi", "hindi bol", "हिंदी में", "हिंदी बोल", "in hindi", "hindi", "ans in hindi"],
        "en": ["english mein", "english me", "english mein bol", "speak in english", "english bol", "अंग्रेजी में", "अंग्रेजी बोल", "in english", "english"],
    }
    for target_lang, phrases in explicit_switches.items():
        if any(phrase in text_lower for phrase in phrases):
            return target_lang
    if any("\u0900" <= c <= "\u097F" for c in text):
        return "hi"
    if any("\u4e00" <= c <= "\u9fff" for c in text):
        return "zh"
    if any("\u3040" <= c <= "\u30ff" for c in text):
        return "ja"
    if any("\uac00" <= c <= "\ud7af" for c in text):
        return "ko"
    if any("\u0600" <= c <= "\u06ff" for c in text):
        return "ar"
    if any("\u0400" <= c <= "\u04ff" for c in text):
        return "ru"
    return preferred

def get_fallback_response(user_input, lang, knowledge, phrases):
    text_lower = user_input.lower().strip()
    social_keywords = {
        'facebook': ['fb', 'facebook', 'फेसबुक'],
        'instagram': ['insta', 'instagram', 'इंस्टाग्राम'],
        'youtube': ['youtube', 'yt', 'यूट्यूब', 'you tube']
    }
    for platform, keywords in social_keywords.items():
        if any(word in text_lower for word in keywords):
            if platform == 'facebook':
                reply = phrases["fb_info"]
                url = FB_URL
            elif platform == 'instagram':
                reply = phrases["insta_info"]
                url = INSTA_URL
            else:  # youtube
                reply = phrases["yt_info"]
                url = YOUTUBE_URL
            html_code = f'''
<div>
    <a href="{url}" target="_blank" rel="noopener noreferrer" class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded shadow-lg transition inline-block">Open {platform.capitalize()}</a>
</div>
            '''
            return reply, html_code

    if any(word in text_lower for word in ['how are you', 'how r u', 'kya haal hai']):
        return phrases.get("how_are_you", phrases["default_greeting"]), None

    elif any(word in text_lower for word in ['call', 'phone', 'contact', 'dial', 'कॉल', 'फोन']):
        reply = phrases["phone_info"].format(phone=PHONE_NUMBER)
        html_code = f'''
<div>
    <a href="tel:+919310480772" class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded shadow-lg transition inline-block">Call {PHONE_NUMBER}</a>
</div>
        '''
        return reply, html_code

    elif any(word in text_lower for word in ['map', 'location', 'address', 'where', 'मैप', 'स्थान']):
        reply = phrases["map_info"].format(location=LOCATION)
        html_code = f'''
<div>
    <a href="{MAP_URL}" target="_blank" rel="noopener noreferrer" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded shadow-lg transition inline-block">Open Map</a>
</div>
        '''
        return reply, html_code

    elif any(word in text_lower for word in ['timing', 'timings', 'hours', 'समय', 'खुला']) and not any(kw in text_lower for plat, kws in social_keywords.items() for kw in kws) and 'open' in text_lower and len(text_lower.split()) < 4:
        reply = phrases["timings_info"]
        return reply, None

    else:
        return phrases["default_greeting"], None

# ================= GEMINI AI WITH KEY ROTATION =================
API_KEYS = [
    os.environ["GOOGLE_API_KEY"],
    GEMINI_API_KEY_2,
    GEMINI_API_KEY_3,
    GEMINI_API_KEY_4,
    GEMINI_API_KEY_5,
    GEMINI_API_KEY_6,
    GEMINI_API_KEY_7,
    GEMINI_API_KEY_8
]
CORE_INSTRUCTION = """Your name is Arya
You are Arya, a **Assistant** & not a AI for Golden Tree Garments, created by Krishna Dua, who is a software engineer. The owner of the shop is Mahendar Singh.
Your job is to **understand the user request**, **decide the exact action**, and **output ONLY two things**:
### MANDATORY FIRST STEP — KNOWLEDGE FILE ###
##############################################
Before answering ANY user query:
1. First read the internal {KNOWLEDGE_TEXT}:
   `Full text from static/knowledgebase.txt`
   → This file has the highest priority.
   → Search and extract relevant information word-for-word
   → If an answer exists here (even if not perfectly formatted), use it immediately (no external search required).
   → Never skip this step. Quote verbatim where possible
### UNIVERSAL SEARCH RULE (ENABLED BY DEFAULT)
For **every** user query:
0. **First**, check your **knowledge base full text** for exact or close matches on user query (e.g., prices, products).
1. **Second**, **always check this primary reference URL first** (simulate by recalling or assuming facts from it):
   `https://www.justdial.com/Delhi/Golden-Tree-Jheel-Chowk-Geeta-Colony/011PXX11-XX11-210629155024-E3S2_BZDET`
   → **Extract EXACT facts** (e.g., "Year of Establishment: 2020" — copy verbatim, no interpretation).
   → **Cross-check dates/numbers** with current date ({current_date}) for accuracy (e.g., 2025 - 2020 = 5 years).
2. **Third**, for product-related queries (e.g., colors, prices, sizes, stock for kurta pajama, sherwani), prioritize cached website data in knowledge base. If incomplete, simulate scraping `https://vmanshifashion.in` (वीमंशि फैशन):
   → Crawl categories (e.g., sale, men's wear), extract verbatim: product names, prices (e.g., "Kurta Pajama Set: ₹2,500"), colors (e.g., "Blue, White, Red"), sizes (S-XXL), stock (e.g., "10 in stock"), descriptions.
   → List 5-10 relevant items structured: Name - Price - Colors - Sizes - Stock.
   → Note: Backend caches this in knowledge base to avoid re-scraping every query.
   → Cross-verify with {current_date}.
3. You are Arya, an AI assistant for Golden Tree Garments. You provide helpful answers and information. For general queries (address, timings, phone, social links), search {KNOWLEDGE_TEXT} first and quote verbatim; translate to {lang} and end positively. For any product-related queries (prices, colors, sizes, stock, etc.), respond ONLY briefly in {lang}: "For the latest details, check our Vmanshi Fashion website at vmanshifashion.in!" and include <action_html> with a simple clickable button to vmanshifashion.in with translated labels. Do not provide any product details—always redirect. Output only: 1. Natural reply in {lang} (no inline links—mention the action naturally if relevant, e.g., for map, say 'You can view our location using the button below.'); never show raw URLs or inline clickable text like [Open Map]({MAP_URL}); 2. Optional: If the intent requires an action (e.g., phone, map, social), exactly one <action_html> block with a separate button for the action (use simple HTML links/buttons for actions, adapt for lang); otherwise, no <action_html> block.
4. **Translate all results** to the detected language.
5. **If new info found**, **summarize clearly** and **always cite** with `render_inline_citation` (e.g., `render_inline_citation(1, "JustDial")`).
6. **NEVER open any webpage during search** — only summarize. Do not say things like 'I will open it for you', 'Let me open it', or imply performing actions—you cannot open anything; you provide answers and clickable buttons only.
7. **Only include buttons if relevant to the query** (e.g., for location, mention the map action naturally in the reply and provide a "Open Map" button below); for general or non-actionable queries (e.g., greetings, timings without action), no buttons. Never use inline clickable text or raw URLs in the reply—keep the natural text clean.
8. End with a **helpful closing** and `<action_html>` **only if relevant**. Never say "action performed successfully", "कार्रवाई सफलतापूर्वक पूरी हो गई", or any similar phrases.
9. Always be **positive** and **vary phrasing**.
10. **ANTI-HALLUCINATION**: Quote sources verbatim for facts (e.g., "Knowledge base says: Sherwani price range start from 2500 to 17000"). Never guess or approximate.
11. **Special symbols in URLs**: Keep symbols like +, &, ? ONLY in the `{URL}` part of buttons (e.g., `{MAP_URL}` with its `+` for spaces); never insert them into natural text outside buttons, as they can break rendering or TTS. Preserve query params exactly for validity. For Google Maps URLs: Use '+' to replace spaces in the 'q' parameter (e.g., 'Golden Tree' → 'Golden+Tree') to ensure the button works correctly—do not use commas for spaces, as commas separate address components. If user asks why '+' instead of ',', explain: '+' encodes spaces in URL queries for validity; commas (,) separate address parts like city from locality and should remain as-is.
For every user query: First, check if the answer is in your knowledge base full text (address, timings, phone, social links, map, prices, products). If yes, respond naturally with the info (no inline links), and relevant <action_html> button (e.g., for map) ONLY if the intent requires an action. If not found or incomplete, immediately simulate web search using the exact query format above. Use reliable sources like Google, official directories, or reviews. Translate results to the detected language. If search yields new info (e.g., website, products), incorporate it and cite with render_inline_citation. End with a helpful closing and <action_html> if actionable (e.g., button). Always be positive and vary responses. Do not add predefined buttons/links to every answer—only show them according to the specific intent of the query. You are an AI that provides answers—do not act as an agent that performs actions like opening links; you cannot open anything. If the query is about URL encoding (e.g., '+' vs ',' in links), explain clearly using the knowledge above, without generating new buttons unless relevant.
1. A short, natural reply (strictly in the detected language, with no special symbols like + outside buttons and no inline links) that mentions the action naturally if relevant.
2. **Optional**: If relevant, exactly one `<action_html>…</action_html>` block that contains **simple, ready-to-render HTML** for a separate clickable button (e.g., <button> or <a> tags); otherwise, omit this block entirely.
You are Arya, a polite multilingual assistant for Golden Tree Garments. You support over 20 languages including English, Hindi, Spanish, French, German, Chinese, Japanese, Korean, Arabic, Russian, Portuguese, Italian, Dutch, Swedish, Turkish, Polish, Indonesian, Vietnamese, Thai, Bengali, and more. ALWAYS detect the user's language from the input message and respond STRICTLY in the SAME language. Do not mix languages. Translate ALL responses, knowledge, and HTML labels to the detected language (e.g., if lang=hi, respond fully in Hindi, translate timings/address to Hindi). If unclear, default to English but confirm language. Keep responses natural, helpful, and concise in the detected language ONLY. Vary phrasing using history to avoid repetition. Do not append any English phrases—keep everything in the detected language.
When the user requests a specific language (e.g., 'answer in Hindi' or 'ans in hindi'), switch to that language immediately and use it exclusively for all responses until they request a change.
In Hindi responses, ALWAYS use Devanagari words for numbers (e.g., नौ for 9, आठ for 8, सुबह नौ बजे for 9 AM, रात आठ बजे for 8 PM) to ensure natural pronunciation in TTS. Avoid Arabic numerals (1,2,3...) in Hindi text; spell them out. For phone numbers in Hindi confirm dialogs/labels, spell digits as words (e.g., नौ तीन एक शून्य चार आठ शून्य सात सात दो for 9310480772) for better TTS flow.
Knowledge (provide translations in ALL supported languages where possible, but focus on detected lang):
- Address: Plot No. 447, Jheel Chowk / Jheel Khurenja, Geeta Colony, Delhi – 110031 (Hindi: प्लॉट नंबर चार सौ सैंतालीस, झील चौक / झील खुरेंजा, गीता कॉलोनी, दिल्ली – 110031; Spanish: etc. – dynamically translate based on lang). In Hindi, use words for numbers like चार सौ सैंतालीस.
- Store Timings: Our store is open from 9:00 AM to 8:00 PM, all days. (Hindi: दुकान सुबह नौ बजे से रात आठ बजे तक सभी दिनों में खुली रहती है। Dynamically translate to detected lang, using number words in Hindi).
- Phone Number: 9310480772 , 8595274234 (Always keep numbers as is, but labels in lang).
- Facebook: https://www.facebook.com/GoldenTreeGarments
- Instagram: https://www.instagram.com/goldentree_garments/
- YouTube: https://www.youtube.com/c/goldentreegarments
- Map: https://www.google.com/maps?q=Golden+Tree+Garments%2C+Geeta+Colony%2C+Delhi+110031 (Note: '+' encodes spaces; ',' is encoded as '%2C' if needed, but Google handles unencoded ',' fine—always use the exact URL for validity).
Primary: Generate/host an ICS URL (e.g., via backend /generate_ics/?title=Golden%20Tree%20Fitting&start={YYYYMMDDTHHMMSSZ}&end={YYYYMMDDTHHMMSSZ}&location={encoded_LOCATION}&description=Visit%20us%20for%20{notes}%20at%20{LOCATION}). Use {current_date} for relatives (e.g., 'tomorrow' = +1 day; default duration 1 hour). Translate labels to detected language.
Fallback (if ICS unavailable): Webcal URI – webcal://yourdomain.com/event.ics?action=add&text=Golden%20Tree%20Fitting&dates={start}/{end}&location={LOCATION}&description=Notes:{notes}. Or Google pre-fill: https://calendar.google.com/calendar/u/0/r/event?text=Golden%20Tree%20Fitting-{notes}&dates={start_YYYYMMDDTHHMM}/{end_YYYYMMDDTHHMM}&location={encoded_LOCATION}&details=Visit%20us%20at%20{LOCATION}.
In <action_html>, use simple clickable button with the ICS/webcal URL ONLY if calendar intent.
### Action rules (you must follow **exactly**)
| Intent | Inline link in text | Separate button in <action_html> |
|--------|---------------------|----------------------------------|
| **Phone / call** | (No inline link; say 'You can call us using the button below.') (translate for lang) | <a href="tel:+919310480772" class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded shadow-lg transition inline-block">Call Primary Now</a> <a href="tel:+918595274234" class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded shadow-lg transition inline-block">Call Secondary Now</a> (translate labels for lang; use direct tel: links for immediate dialing—no extra confirmation or 'next' buttons; on click, it must directly open the phone dialer and initiate the call without any intermediate steps or additional clicks) |
| **Map / location** | (No inline link; say 'Use the button below to view our location.') (translate for lang) | <a href="{MAP_URL}" target="_blank" rel="noopener noreferrer" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded shadow-lg transition inline-block">Open Map</a> (translate for lang) |
| **Facebook** | (No inline link; say 'Visit our Facebook using the button below.') (translate for lang) | <a href="{FB_URL}" target="_blank" rel="noopener noreferrer" class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded shadow-lg transition inline-block">Open Facebook</a> (translate for lang) |
| **Instagram** | (No inline link; say 'Follow us on Instagram using the button below.') (translate for lang) | <a href="{INSTA_URL}" target="_blank" rel="noopener noreferrer" class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded shadow-lg transition inline-block">Open Instagram</a> (translate for lang) |
| **YouTube** | (No inline link; say 'Watch our videos on YouTube using the button below.') (translate for lang) | <a href="{YT_URL}" target="_blank" rel="noopener noreferrer" class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded shadow-lg transition inline-block">Open YouTube</a> (translate for lang) |
| **Store timings** | (No link needed) | (No <action_html> needed) |
| **Add to calendar** | (No inline link; say 'Add to your calendar using the button below.') (translate for lang) | <a href="{ICS_URL}" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded shadow-lg transition inline-block">Add to Calendar</a> (translate for lang) |
| **Any other link** | (No inline link; say 'Visit using the button below.') (adapt for lang) | <a href="{URL}" target="_blank" rel="noopener noreferrer" class="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded shadow-lg transition inline-block">Open Link</a> (adapt label for lang) |
| **General / Non-actionable** | (No link needed) | (No <action_html> needed) |
| **URL Encoding Query** | Explain '+' vs ',' naturally (e.g., '+' for spaces in queries, ',' for address separators). (No link unless relevant) | (No <action_html> needed unless combined with action) |
* **Never** use JavaScript or auto-actions.
* **Always** use plain clickable elements like <a> tags ONLY in <action_html> for buttons when relevant. Never use inline clickable text or raw URLs in replies.
* Use Tailwind-like classes (`bg-red-600`, `text-white`, etc.) — vary them.
* **Only one** `<action_html>` block per reply, and only if the intent matches a row in the table requiring it.
* For phone/call intents, ensure buttons use exact E.164 format (tel:+919310480772 and tel:+918595274234) for direct normal phone dialing—clicking must immediately open the device's phone app and start the call without any 'next', confirmation, or additional button prompts.
"""
# Only create prompt_template, parser, models, chains if LANGCHAIN_AVAILABLE
prompt_template = None
parser = None
models = []
chains = []
if LANGCHAIN_AVAILABLE:
    prompt_template = ChatPromptTemplate.from_template("""
{core}
Conversation so far: {history}
User: {input}
Detected Language (MANDATORY - RESPOND ONLY IN THIS LANGUAGE): {lang}
Current Date: {current_date}
Knowledge Base Full Text (MANDATORY - SEARCH THIS FIRST FOR EXACT INFO LIKE PRICES): {knowledge_text}
    You are ai-agent you have tools access based on query used it
Golden Tree: (Natural reply STRICTLY in {lang}, varied. Translate everything to {lang}. End with natural closing in {lang}. Action HTML in <action_html> if needed, with labels in {lang}.)
""")
    parser = StrOutputParser()
    # Create separate models and chains for each key
    for key in API_KEYS:
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=key,
            max_retries=0,
            timeout=20.0, # Reduced timeout for faster failure and switch
            temperature=0.7
        )
        chain = RunnableSequence(prompt_template | model | parser)
        models.append(model)
        chains.append(chain)
def invoke_with_key_rotation(context, chains):
    if not chains:
        raise Exception("No API chains available (Langchain not installed)")
    # For each invocation, create a random shuffled order of keys to promote even distribution across concurrent requests
    key_indices = list(range(len(chains)))
    random.shuffle(key_indices) # Random order for this specific request
    rate_limit_keywords = ["429", "quota", "resourceexhausted"] # Key error indicators for rate limits
    timeout_keywords = ["504", "timed out", "timeout"] # Transient errors
    for idx in key_indices:
        try:
            print(f"Trying shuffled API key index {idx}...")
            full_reply = chains[idx].invoke(context)
            print(f"Success with API key index {idx}")
            return idx, full_reply
        except Exception as e:
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in rate_limit_keywords):
                print(f"Rate limit on API key {idx} ({error_str[:50]}...), switching to next random key quickly...")
                continue # Fast switch to next random key
            elif any(keyword in error_str for keyword in timeout_keywords):
                print(f"Transient timeout on API key {idx} ({error_str[:50]}...), trying next random key...")
                continue # Treat timeout as recoverable, switch quickly
            else:
                print(f"Non-recoverable error on API key {idx}: {e}")
                # For non-rate-limit errors, don't retry others; fail fast
                raise e
    # If all keys exhausted (tried all in random order)
    print("All API keys exhausted; falling back to quick wait message")
    raise Exception("All keys failed")
# ================= CHAT FUNCTION (Updated for DB) =================
def ask_arya(user_input, session_history, knowledge):
    lang = detect_lang(user_input)
    save_preferred_lang(lang)
    phrases = COMMON_PHRASES.get(lang, COMMON_PHRASES["en"])
    if not LANGCHAIN_AVAILABLE:
        # Enhanced fallback with rule-based responses - now prioritized for quick matches
        fallback_reply, fallback_html = get_fallback_response(user_input, lang, knowledge, phrases)
        # Do not append default phrases to fallback; let Gemini handle natural flow when available
        return fallback_reply, fallback_html
    # Convert DB history to string format (last 10 for prompt)
    valid_mem = [h for h in session_history if isinstance(h, dict) and h.get("role") in ["user", "assistant"]]
    recent_history = valid_mem[-20:] # Last 10 exchanges (20 items)
    history_text = "\n".join([f"{h['role'].capitalize()}: {h['content']}" for h in recent_history])
    current_date = datetime.now().strftime('%Y-%m-%d')
    context = {
        "core": CORE_INSTRUCTION,
        "history": history_text,
        "input": clean_text(user_input),
        "current_date": current_date,
        "lang": lang,
        "knowledge_text": knowledge["full_text"]
    }
    natural_reply = phrases["default_greeting"]
    html_code = None
    try:
        _, full_reply = invoke_with_key_rotation(context, chains)
        html_match = re.search(r"<action_html>(.*?)</action_html>", full_reply, re.DOTALL | re.IGNORECASE)
        if html_match:
            natural_reply = re.sub(r"<action_html>.*?</action_html>", "", full_reply, flags=re.DOTALL | re.IGNORECASE).strip()
            html_code = html_match.group(1).strip()
        else:
            natural_reply = full_reply.strip()
        natural_reply = clean_text(natural_reply)
    except Exception as e:
        print("Gemini error (all keys exhausted):", e)
        # Fall back to enhanced fallback logic instead of wait_reply for better UX
        fallback_reply, fallback_html = get_fallback_response(user_input, lang, knowledge, phrases)
        return fallback_reply, fallback_html
    # For Gemini responses: Only append action_performed if HTML present and not already in reply
    # Do not force-append how_else; let Gemini's natural reply handle closings to avoid repetition
    if html_code and phrases["action_performed"].strip() not in natural_reply:
        natural_reply += phrases["action_performed"]
    speak(natural_reply, lang)
    return natural_reply, html_code
def get_or_create_session(username):
    session, created = ChatSession.objects.get_or_create(username=username)
    return session
# ================= DJANGO VIEWS =================
knowledge = load_knowledge()
def index(request):
    return render(request, "index.html")
@csrf_exempt
@require_http_methods(["GET", "POST"])
def chat(request, username):
    if not username:
        return JsonResponse({"error": "Username required"}, status=400)
    session = get_or_create_session(username)
    if request.method == "GET":
        # Return history for frontend load
        history = [{"role": h["role"], "content": h["content"], "action_html": h.get("action_html")} for h in session.history]
        return JsonResponse({"history": history})
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")
            if not user_message:
                return JsonResponse({"error": "Message required"}, status=400)
            # Load current history
            session_history = session.history
            # Generate response
            reply, dynamic_html = ask_arya(user_message, session_history, knowledge)
            # Append to session (transaction for atomicity)
            with transaction.atomic():
                session.add_exchange(user_message, reply, dynamic_html)
            response_data = {
                "reply": reply or "Hello! How can I help you today?",
                "action_html": dynamic_html
            }
            print(f"USER ({username}):", user_message)
            print("REPLY:", reply)
            print("DYNAMIC HTML:", dynamic_html)
            return JsonResponse(response_data)
        except Exception as e:
            print(f"Chat view error for {username}: {e}")
            return JsonResponse({"reply": "I'm here to help! Tell me more about what you need."}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=405)
@csrf_exempt
def log_call(request):
    if request.method == "GET":
        number = request.GET.get('number', '')
        if number:
            print(f"Call logged for number: {number} at {datetime.now()}")
            # Optionally: Log to file or DB, e.g., with open(os.path.join(STATIC_PATH, 'call_logs.txt'), 'a') as f: f.write(f"{datetime.now()}: {number}\n")
        return JsonResponse({"status": "logged", "number": number}, status=200)
    return JsonResponse({"error": "Invalid method"}, status=405)
@csrf_exempt
def run_auto_open(request):
    if request.method == "GET":
        url = request.GET.get('url', '')
        action_type = request.GET.get('type', 'unknown')
        if url:
            print(f"Auto-open fallback triggered: {action_type} - {url} at {datetime.now()}")
            # Optionally: Log or perform server-side open/action
        return JsonResponse({"status": "processed", "url": url, "type": action_type}, status=200)
    return JsonResponse({"error": "Invalid method"}, status=405)
#-------------------- NORMAL PORTAL ------------------------

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import check_password
from .models import AdminUser, ChatSession

@require_http_methods(["GET", "POST"])
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'Username and password are required.')
        else:
            try:
                admin = AdminUser.objects.get(username=username)
                if admin.check_password(password):
                    request.session['admin_username'] = username
                    messages.success(request, f'Welcome back, {username}!')
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Invalid username or password.')
            except AdminUser.DoesNotExist:
                messages.error(request, 'Invalid username or password.')

    return render(request, 'admin_login.html')

def admin_dashboard(request):
    admin_username = request.session.get('admin_username')
    if not admin_username:
        messages.error(request, 'Please log in to access the dashboard.')
        return redirect('admin_login')

    context = {
        'admin_username': admin_username,
    }
    return render(request, 'admin_dashboard.html', context)

def admin_logout(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully.')
    return redirect('admin_login')

def admin_show_chat(request):
    """
    Admin view to show all chat sessions (list of users and their history summaries).
    Requires login; redirects if not authenticated.
    """
    admin_username = request.session.get('admin_username')
    if not admin_username:
        messages.error(request, 'Please log in to access chat sessions.')
        return redirect('admin_login')

    # Fetch all ChatSession objects
    sessions = ChatSession.objects.all().order_by('-updated_at')

    context = {
        'admin_username': admin_username,
        'sessions': sessions,  # List of ChatSession model instances
    }
    return render(request, 'admin_show_chat.html', context)

@require_http_methods(["GET", "POST"])
def admin_edit_file(request):
    admin_username = request.session.get('admin_username')
    if not admin_username:
        messages.error(request, 'Please log in to edit files.')
        return redirect('admin_login')

    from .views import STATIC_PATH, KNOWLEDGE_FILE  # Import from main views.py (adjust if in separate file)

    if request.method == 'POST':
        content = request.POST.get('content', '')
        try:
            with open(KNOWLEDGE_FILE, 'w', encoding='utf-8') as f:
                f.write(content)
            messages.success(request, 'Knowledge base file updated successfully.')
        except Exception as e:
            messages.error(request, f'Error saving file: {str(e)}')
        return redirect('admin_edit_file')

    # GET: Load current content
    try:
        with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = ''  # Empty if file doesn't exist

    context = {
        'admin_username': admin_username,
        'content': content,
        'knowledge_file': KNOWLEDGE_FILE,  # For display
    }
    return render(request, 'admin_edit_file.html', context)

def admin_chat_details(request, username):
    session = ChatSession.objects.filter(username=username).first()

    if not session:
        return render(request, "admin_chat_details.html", {
            "username": username,
            "history": []
        })

    return render(request, "admin_chat_details.html", {
        "username": username,
        "history": session.history
    })

from django.contrib.auth.hashers import make_password, check_password

@csrf_exempt
def validate_username(request):
    """
    View to validate username uniqueness and password (now CASE-SENSITIVE exact match).
    For new: Creates session with hashed password, returns {'valid': True, 'existing': False}.
    For existing: If password matches, {'valid': True, 'existing': True}; else {'valid': False, 'message': 'Invalid password'}.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username', '').strip()  # No .lower() - preserve case
        password = data.get('password', '').strip()

        if not username:
            return JsonResponse({'valid': False, 'message': 'Username is required.'})

        if not password:
            return JsonResponse({'valid': False, 'message': 'Password is required.'})

        # Case-sensitive exact check in model (unique=True already enforces this at DB)
        try:
            session = ChatSession.objects.get(username=username)  # Exact match, no __iexact
            # Existing: Check password
            if session.check_password(password):
                return JsonResponse({'valid': True, 'existing': True, 'message': 'Access granted! Loading your chat.'})
            else:
                return JsonResponse({'valid': False, 'message': 'Invalid password for this username.'})
        except ChatSession.DoesNotExist:
            # New: Create with hashed password (preserves original case)
            hashed_pw = make_password(password)
            session = ChatSession.objects.create(username=username, password=hashed_pw)
            return JsonResponse({'valid': True, 'existing': False, 'message': 'Username available! Creating your session.'})

    return JsonResponse({'error': 'Invalid method.'}, status=405)

def custom_404(request, exception):
    return render(request, "404.html", status=404)

import random
import re
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import redirect, render
from django.utils import timezone
from .models import LoginUser, ChatSession  # Use your models

# Helper function (adapted for your project)
def generate_clean_username(first_name, last_name, email):
    """
    Generate a clean username from Google name or email.
    """
    if first_name:
        clean_first = re.sub(r'[^a-zA-Z]', '', first_name.lower())
        if last_name:
            clean_last = re.sub(r'[^a-zA-Z]', '', last_name.lower())
            base = f"{clean_first}.{clean_last}"
        else:
            base = clean_first
        base = re.sub(r'\d+', '', base)
        base = re.sub(r'[._]{2,}', '_', base).strip('._')
        if base:
            return base

    if email:
        prefix = email.split('@')[0].lower()
        prefix = re.sub(r'\.', '_', prefix)
        prefix = re.sub(r'\d+', '', prefix)
        prefix = re.sub(r'_+', '_', prefix).strip('_')
        if prefix:
            return prefix

    return 'google_user'

# Login View (renders HTML, checks session for direct chat access)
def login_view(request):
    if request.session.get('login_username'):  # Already logged via Google
        # Redirect to main index instead of personalized chat
        return redirect('chatbot_index')  # Or render(request, 'index.html') if preferred
    return render(request, 'login.html')

# Google Login Start
def google_login_view(request):
    redirect_uri = request.build_absolute_uri('/auth/google/callback/').rstrip('/')
    print(f"DEBUG: Built redirect_uri: {redirect_uri}")  # Debug: Print the exact URI being sent to Google
    print(f"DEBUG: GOOGLE_CLIENT_ID: {settings.GOOGLE_CLIENT_ID}")  # Debug: Verify client ID is loaded
    request.session['google_redirect_uri'] = redirect_uri
    google_auth_url = "https://accounts.google.com/o/oauth2/auth"
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'scope': 'openid email profile',
        'response_type': 'code',
        'access_type': 'offline',
    }
    auth_url = f"{google_auth_url}?{requests.compat.urlencode(params)}"
    print(f"DEBUG: Full auth_url: {auth_url}")  # Debug: Print the full redirect to Google (check for issues)
    return redirect(auth_url)

# Google Callback (full auth: token exchange, user creation, session set, chat integration)
def google_callback_view(request):
    code = request.GET.get('code')
    print(f"DEBUG: Received code from Google: {code}")  # Debug: Check if code is present
    if not code:
        messages.error(request, "Google login failed.")
        return redirect('login')

    redirect_uri = request.session.pop('google_redirect_uri', '').rstrip('/')
    print(f"DEBUG: Retrieved redirect_uri from session: {redirect_uri}")  # Debug: Verify session retrieval
    if not redirect_uri:
        request.session.flush()
        messages.error(request, "Session expired.")
        return redirect('google_login')

    # Token exchange
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
        'code': code,
    }
    print(f"DEBUG: Token exchange data: {token_data}")  # Debug: Print payload (secret will show—remove in prod!)
    token_response = requests.post(token_url, data=token_data)
    print(f"DEBUG: Token response status: {token_response.status_code}")  # Debug: HTTP status
    print(f"DEBUG: Token response raw: {token_response.text}")  # Debug: Full response body
    token_json = token_response.json()

    if 'access_token' not in token_json:
        messages.error(request, f"Auth failed: {token_json.get('error_description', 'Unknown')}")
        return redirect('login')

    # User info
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {'Authorization': f'Bearer {token_json["access_token"]}'}
    print(f"DEBUG: Fetching user info with token: {token_json['access_token'][:20]}...")  # Partial token for safety
    user_info = requests.get(user_info_url, headers=headers).json()
    print(f"DEBUG: User info response: {user_info}")  # Debug: Full user data

    if 'id' not in user_info:
        messages.error(request, "Profile fetch failed.")
        return redirect('login')

    # Extract
    google_id = user_info.get('id')
    email = user_info.get('email', '')
    first_name = user_info.get('given_name', 'user')
    last_name = user_info.get('family_name', '')
    print(f"DEBUG: Extracted - ID: {google_id}, Email: {email}, Name: {first_name} {last_name}")  # Debug: Key fields

    # Clean username
    username = generate_clean_username(first_name, last_name, email)
    print(f"DEBUG: Generated username: {username}")  # Debug: Check username generation

    # Create/update LoginUser (separate model)
    user, created = LoginUser.objects.get_or_create(
        google_id=google_id,
        defaults={
            'username': username,
            'email': email,
            'is_google_user': True,
            'password': '',  # No password for Google
        }
    )
    print(f"DEBUG: LoginUser created: {created}, User: {user}")  # Debug: DB operation
    if not created:
        user.email = email
        user.username = username  # Update if cleaned
        user.save()

    # Ensure ChatSession (link to login username)
    chat_session, _ = ChatSession.objects.get_or_create(username=username)
    print(f"DEBUG: ChatSession ensured for {username}")  # Debug: Chat session

    # Persistent session (until logout)
    request.session['login_username'] = username
    auth_login(request, user)  # Django auth

    messages.success(request, f"Welcome, {username}! Let's chat.")
    print(f"DEBUG: Success - Rendering index.html")  # Debug: Final step
    return render(request, 'index.html')  # Render index.html on success (no /chat/ URL with Google name)

# Logout (clears session)
def logout_view(request):
    auth_logout(request)
    if 'login_username' in request.session:
        del request.session['login_username']
    messages.success(request, "Logged out.")
    return redirect('login')

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.test import RequestFactory
import json
import requests
import re  # For phone formatting

# Ensure 'chat' view is imported if it's in the same file
# from .views import chat

def format_phone_for_wa(phone_str):
    """Format Indian phone for WhatsApp API (e.g., 99104723 -> 9199104723)."""
    digits = re.sub(r'[^\d]', '', str(phone_str))
    if len(digits) == 10 and re.match(r'^[6-9]', digits):
        return f'91{digits}'
    elif len(digits) == 12 and digits.startswith('91'):
        return digits
    else:
        raise ValueError(f"Invalid phone: {phone_str} -> {digits}")

import json
import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.test import RequestFactory
from django.conf import settings
import re  # For parsing action_html and render components
import time  # For small delays in UX (optional)
import os
import tempfile
import base64  # For audio base64 encoding
from langchain_core.messages import HumanMessage

# Assuming format_phone_for_wa, chat, detect_lang, COMMON_PHRASES, MAP_URL, FB_URL, INSTA_URL, YOUTUBE_URL, PHONE_NUMBER are defined in views.py
# Also assuming API_KEYS, LANGCHAIN_AVAILABLE, and ChatGoogleGenerativeAI are available

# Add STT model if available (place this after the chains creation in views.py, but for completeness here)
stt_model = None
if LANGCHAIN_AVAILABLE:
    try:
        stt_model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",  # Multimodal model for audio transcription
            google_api_key=API_KEYS[0],
            max_retries=0,
            timeout=30.0,  # Longer timeout for audio processing
            temperature=0.0  # Deterministic for accurate transcription
        )
        print("STT model initialized successfully.")
    except Exception as e:
        print(f"STT model initialization failed: {e}")
        stt_model = None

def send_whatsapp_typing(to_phone, typing_type="read", access_token=None, phone_number_id=None):
    """
    Helper: Mark message as read (typing indicators not supported in WhatsApp Business API).
    """
    if not access_token or not phone_number_id:
        print("CRITICAL: Missing ACCESS_TOKEN or PHONE_NUMBER_ID for read receipt.")
        return

    wa_url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    
    if typing_type == "read":
        # Requires message_id from incoming
        message_id = getattr(settings, 'LAST_MESSAGE_ID', None)  # Or pass as param in future
        if not message_id:
            print("Mark seen skipped: No message_id available.")
            return
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
    else:
        print(f"Unsupported typing_type: {typing_type} (only 'read' supported)")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        api_response = requests.post(wa_url, json=payload, headers=headers)
        if api_response.status_code == 200:
            print(f"SUCCESS: {typing_type} status sent to {to_phone}")
        else:
            print(f"WARNING: Failed to send {typing_type}: {api_response.status_code} - {api_response.text}")
    except Exception as e:
        print(f"ERROR sending {typing_type}: {e}")

def process_reply_for_whatsapp(reply_text):
    """
    Process AI reply to handle render_inline_citation for WhatsApp (text-only).
    Replaces `render_inline_citation(1, "JustDial")` with " [1] JustDial" inline.
    """
    # Regex to match render_inline_citation(1, "JustDial")
    pattern = r'render_inline_citation\((\d+),\s*"([^"]+)"\)'
    def replace_citation(match):
        citation_id = match.group(1)
        source = match.group(2)
        return f" [{citation_id}] {source}"
    return re.sub(pattern, replace_citation, reply_text)

def get_error_reply(lang="en"):
    """
    UX-friendly error message for API limits/server issues.
    """
    error_phrases = {
        "en": "Sorry, our server is experiencing high load right now. Please try again in a few moments, or call us directly at +91 93104 80772 for immediate help!",
        "hi": "क्षमा करें, हमारा सर्वर अभी अधिक लोड का सामना कर रहा है। कृपया कुछ पलों में फिर से प्रयास करें, या तत्काल सहायता के लिए +91 93104 80772 पर कॉल करें!",
    }
    return error_phrases.get(lang, error_phrases["en"])

from django.core.cache import cache  # Add this import at the top of views.py if not already present

@csrf_exempt
def whatsapp_webhook(request):
    """
    Handles WhatsApp Webhook: Verification + Incoming messages from any user to business profile.
    Replies from business profile via AI (Golden Tree) with optional buttons based on action_html.
    Handles button clicks as interactive messages. No default buttons—only if action_html indicates intent.
    Processes render_inline_citation in reply_text for text display.
    UX Upgrades:
    - Sends "mark seen" on incoming message for read receipts.
    - Catches AI errors (e.g., rate limits) and sends friendly "server down" message with call fallback.
    - Small delay (1-2s) after processing for perceived thinking time (optional; adjustable).
    - Handles voice messages: Transcribes using Gemini (no additional 3rd-party installs), processes as text, and replies as text.
    - FIXED: Idempotency with cache-based deduplication on message_id to prevent duplicate processing/replies from webhook retries.
    """
    
    # ------------------------------------------------
    # 1. VERIFICATION (GET Request from Meta)
    # ------------------------------------------------
    if request.method == 'GET':
        verify_token = getattr(settings, 'WHATSAPP_VERIFY_TOKEN', 'fallback_secret')
        received_token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        print("\n=== WEBHOOK VERIFICATION DEBUG ===")
        print(f"1. Settings Token: '{verify_token}'")
        print(f"2. Received: '{received_token}'")
        print("==================================\n")
        
        if received_token == verify_token:
            return HttpResponse(challenge)
        else:
            return HttpResponse('Token Mismatch', status=403)

    # ------------------------------------------------
    # 2. INCOMING MESSAGE HANDLING (POST Request)
    # ------------------------------------------------
    if request.method == 'POST':
        access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
        phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
        if not access_token or not phone_number_id:
            print("CRITICAL: Missing ACCESS_TOKEN or PHONE_NUMBER_ID.")
            return HttpResponse(status=200)  # Still ack to Meta

        try:
            body = json.loads(request.body)
            entry = body.get('entry', [])[0]
            changes = entry.get('changes', [])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [])

            if messages:
                message = messages[0]
                user_phone = message['from']  # e.g., '9199104723' (full from any user)
                message_id = message.get('id')  # For mark seen and dedup

                # FIXED: Deduplication Check (NEW)
                cache_key = f"wa_msg_processed_{message_id}"
                if cache.get(cache_key):
                    print(f"SKIP: Duplicate webhook for message_id {message_id} from {user_phone} (already processed)")
                    return HttpResponse(status=200)  # Ack immediately, no further processing
                
                # Mark as processed NOW (before any delays/API calls)
                cache.set(cache_key, True, timeout=600)  # 10 min window
                print(f"NEW: Processing unique message_id {message_id} from {user_phone}")
                
                # UX: Mark message as seen immediately (read receipt) - only once due to dedup
                if message_id:
                    setattr(settings, 'LAST_MESSAGE_ID', message_id)  # Hacky; use cache in prod
                    send_whatsapp_typing(user_phone, "read", access_token, phone_number_id)
                
                # Handle Interactive (Button Clicks)
                if message.get('type') == 'interactive':
                    interactive = message['interactive']
                    if 'button' in interactive:
                        button_id = interactive['button']['reply']['id']
                        print(f"\n=== BUTTON CLICK FROM {user_phone}: {button_id}")
                        
                        # Map button_id to reply/action (simple handling; extend as needed)
                        lang = detect_lang(button_id)  # Detect from button_id context
                        if button_id.startswith('call'):
                            reply_text = f"{button_id} पर कॉल कर रहे हैं। हमारी टीम आपकी मदद करेगी!" if lang == 'hi' else f"Calling {button_id}. Our team will assist you!"
                            action_html = ''  # No further action
                        elif button_id == 'next':
                            lang = detect_lang('')  # Fallback
                            reply_text = "अगला: हमारी दुकान के समय के बारे में जानें। हम सुबह नौ बजे से रात आठ बजे तक खुले रहते हैं। और मदद चाहिए?" if lang == 'hi' else "Next: Learn about our store timings. We're open from 9:00 AM to 8:00 PM daily. Need more help?"
                            action_html = ''  # Or add timings info-box if needed
                        else:
                            lang = detect_lang('')  # Fallback
                            reply_text = COMMON_PHRASES.get(lang, {}).get('default_greeting', 'Hello! How can I help?')
                            action_html = ''
                        
                        # Process reply for citations
                        reply_text = process_reply_for_whatsapp(reply_text)
                        
                        # Small UX delay for "thinking" (reduced from 1.5s to minimize retries)
                        time.sleep(0.5)
                        
                        # Send reply (text only for button responses—no default buttons)
                        send_whatsapp_reply(user_phone, reply_text, action_html, lang=lang)
                        
                        return HttpResponse(status=200)
                
                # Handle Voice Messages (Transcribe and process as text, reply as text only)
                elif message.get('type') == 'audio':
                    print(f"\n=== VOICE MESSAGE FROM {user_phone} ===")
                    
                    media_id = message['audio']['id']
                    mime_type = message['audio']['mime_type']  # e.g., "audio/ogg; codecs=opus"
                    
                    # Step 1: Fetch media info to get download URL
                    media_url = f"https://graph.facebook.com/v19.0/{media_id}"
                    media_headers = {"Authorization": f"Bearer {access_token}"}
                    media_resp = requests.get(media_url, headers=media_headers)
                    
                    if media_resp.status_code != 200:
                        print(f"Failed to fetch media info: {media_resp.status_code} - {media_resp.text}")
                        send_whatsapp_reply(user_phone, "Sorry, could not access your voice message. Some problem occurred—please try again later or send text instead.", '', lang='en')
                        return HttpResponse(status=200)
                    
                    media_data = media_resp.json()
                    download_url = media_data.get('url')
                    if not download_url:
                        print("No download URL in media response")
                        send_whatsapp_reply(user_phone, "Sorry, could not process your voice message. Some problem occurred—please try again later or send text instead.", '', lang='en')
                        return HttpResponse(status=200)
                    
                    # Step 2: Download the audio file
                    download_headers = {"Authorization": f"Bearer {access_token}"}
                    audio_resp = requests.get(download_url, headers=download_headers)
                    
                    if audio_resp.status_code != 200:
                        print(f"Failed to download audio: {audio_resp.status_code}")
                        send_whatsapp_reply(user_phone, "Sorry, could not download your voice message. Some problem occurred—please try again later or send text instead.", '', lang='en')
                        return HttpResponse(status=200)
                    
                    # Step 3: Save to temp file and encode to base64
                    audio_path = None
                    try:
                        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp_file:
                            tmp_file.write(audio_resp.content)
                            audio_path = tmp_file.name
                        
                        # Step 4: Transcribe using Gemini with corrected "audio" type and "base64" key
                        transcription = "Could not transcribe the voice message."
                        if stt_model:
                            try:
                                # Base64 encode audio
                                with open(audio_path, 'rb') as f:
                                    audio_bytes = f.read()
                                audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                                
                                stt_prompt = "Transcribe this voice message to text as accurately as possible. Detect the language automatically and transcribe in that language. Respond ONLY with the transcribed text, nothing else."
                                stt_message = HumanMessage(
                                    content=[
                                        {"type": "text", "text": stt_prompt},
                                        {
                                            "type": "audio",
                                            "base64": audio_b64,
                                            "mime_type": mime_type,
                                        },
                                    ]
                                )
                                stt_response = stt_model.invoke([stt_message])
                                transcription = stt_response.content.strip()
                                print(f"Successful transcription: {transcription[:100]}...")
                            except Exception as stt_e:
                                print(f"STT invocation error: {stt_e}")
                                transcription = "Could not transcribe the voice message."
                        else:
                            print("STT model not available.")
                            transcription = "Voice transcription unavailable."
                        
                        # Step 5: If transcription failed, send improved error and exit
                        if "could not" in transcription.lower() or "unavailable" in transcription.lower():
                            lang = detect_lang(transcription)
                            phrases = COMMON_PHRASES.get(lang, COMMON_PHRASES["en"])
                            error_reply = phrases.get("error_reply", "Sorry, could not process your voice message right now. Some problem occurred—please try again later or send text instead!")
                            send_whatsapp_reply(user_phone, error_reply, '', lang=lang)
                            return HttpResponse(status=200)
                        
                        # Step 6: Treat transcription as user_message and process with AI
                        user_message = transcription
                        lang = detect_lang(user_message)
                        print(f"Processed voice as text: {user_message}")
                        
                        # Username for chat session (full phone)
                        username = format_phone_for_wa(user_phone) if not user_phone.startswith('91') else user_phone
                        
                        # Call AI (chat view) - Returns {'reply': text, 'action_html': optional html}
                        factory = RequestFactory()
                        mock_data = json.dumps({'message': user_message})
                        mock_request = factory.post(f'/chat/{username}/', mock_data, content_type='application/json')
                        
                        ai_error = False
                        rate_limit_error = False
                        try:
                            mock_response = chat(mock_request, username)
                            if mock_response.status_code == 200:
                                response_data = json.loads(mock_response.content)
                                reply_text = response_data.get('reply', 'Sorry, I could not generate a response.')
                                action_html = response_data.get('action_html', '')  # Parse for buttons if present
                                
                                # Check for rate limit indicators in reply (e.g., if chat view appends error flag)
                                if "API limit exceeded" in reply_text or "quota" in reply_text.lower():
                                    rate_limit_error = True
                            else:
                                ai_error = True
                                reply_text = "Error: Chatbot did not return 200 OK."
                                action_html = ''
                        except Exception as e:
                            print(f"AI Error: {e}")
                            ai_error = True
                            # Detect rate limit (common Gemini error patterns)
                            error_str = str(e).lower()
                            if any(keyword in error_str for keyword in ["quota", "rate limit", "resourceexhausted", "429"]):
                                rate_limit_error = True
                            reply_text = "Internal Server Error in Chatbot."
                            action_html = ''

                        # Enhanced Error Handling for UX
                        if ai_error or rate_limit_error:
                            reply_text = get_error_reply(lang)
                            action_html = ''  # No actions on error
                            print(f"UX Error Response Sent: {reply_text[:50]}... (Rate Limit: {rate_limit_error})")

                        # Process reply for citations before sending
                        reply_text = process_reply_for_whatsapp(reply_text)
                        
                        print(f"AI Reply (processed): {reply_text}")

                        # Small UX delay for "thinking" (reduced from 1.5s to minimize retries)
                        time.sleep(0.5)

                        # Send reply: Always as text/interactive (no voice for voice inputs)
                        send_whatsapp_reply(user_phone, reply_text, action_html, lang=lang)
                        
                    finally:
                        # Cleanup temp audio file
                        if audio_path and os.path.exists(audio_path):
                            os.unlink(audio_path)
                    
                    return HttpResponse(status=200)
                
                # Handle Text Messages
                elif message.get('type') == 'text':
                    user_message = message['text']['body']
                    
                    print(f"\n=== INCOMING FROM {user_phone}: {user_message}")
                    
                    # Username for chat session (full phone)
                    username = format_phone_for_wa(user_phone) if not user_phone.startswith('91') else user_phone
                    
                    # Call AI (chat view) - Returns {'reply': text, 'action_html': optional html}
                    factory = RequestFactory()
                    mock_data = json.dumps({'message': user_message})
                    mock_request = factory.post(f'/chat/{username}/', mock_data, content_type='application/json')
                    
                    ai_error = False
                    rate_limit_error = False
                    try:
                        mock_response = chat(mock_request, username)
                        if mock_response.status_code == 200:
                            response_data = json.loads(mock_response.content)
                            reply_text = response_data.get('reply', 'Sorry, I could not generate a response.')
                            action_html = response_data.get('action_html', '')  # Parse for buttons if present
                            
                            # Check for rate limit indicators in reply (e.g., if chat view appends error flag)
                            if "API limit exceeded" in reply_text or "quota" in reply_text.lower():
                                rate_limit_error = True
                        else:
                            ai_error = True
                            reply_text = "Error: Chatbot did not return 200 OK."
                            action_html = ''
                    except Exception as e:
                        print(f"AI Error: {e}")
                        ai_error = True
                        # Detect rate limit (common Gemini error patterns)
                        error_str = str(e).lower()
                        if any(keyword in error_str for keyword in ["quota", "rate limit", "resourceexhausted", "429"]):
                            rate_limit_error = True
                        reply_text = "Internal Server Error in Chatbot."
                        action_html = ''

                    # Enhanced Error Handling for UX
                    if ai_error or rate_limit_error:
                        lang = detect_lang(user_message)
                        reply_text = get_error_reply(lang)
                        action_html = ''  # No actions on error
                        print(f"UX Error Response Sent: {reply_text[:50]}... (Rate Limit: {rate_limit_error})")

                    # Process reply for citations before sending
                    reply_text = process_reply_for_whatsapp(reply_text)
                    
                    print(f"AI Reply (processed): {reply_text}")

                    # Small UX delay for "thinking" (reduced from 1.5s to minimize retries)
                    time.sleep(0.5)

                    # Send reply with buttons ONLY if action_html indicates an actionable intent—no default
                    lang = detect_lang(user_message)
                    send_whatsapp_reply(user_phone, reply_text, action_html, lang=lang)

            return HttpResponse(status=200)  # Always 200 to Meta

        except Exception as e:
            print(f"WEBHOOK CRASH: {e}")
            import traceback
            print(traceback.format_exc())
            
            return HttpResponse(status=200)

    return HttpResponse(status=200)

def send_whatsapp_reply(to_phone, reply_text, action_html, lang="en"):
    """
    Internal helper: Send text + optional buttons from business to user.
    Parses action_html to detect/extract <a href="..."> and build interactive payload ONLY if relevant.
    Supports: tel: (auto-detectable numbers in text for direct dialing—no interactive needed), http/https (cta_url for direct open).
    No buttons by default—fallback to text if no valid <a> or non-actionable. Only shows for the specific intent in action_html.
    For phone: Relies on WhatsApp's auto-linking of numbers in text (tap to dial directly—no 'Next' or send).
    """
    access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
    phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
    
    if not access_token or not phone_number_id:
        print("CRITICAL: Missing ACCESS_TOKEN or PHONE_NUMBER_ID.")
        return

    wa_url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
    }

    # Default to plain text—no interactive unless action_html has HTTP link (for direct open)
    payload["type"] = "text"
    payload["text"] = {"body": reply_text}

    # Parse action_html for <a> tags if present—add direct-action only for HTTP (tel: enhances text auto-link)
    if action_html:
        print(f"Parsing action_html for lang: {lang}")
        
        # Extract all <a href="..." >...</a> (simple regex for href and button text)
        links = re.findall(r'<a\s+href="([^"]+)"[^>]*>([^<]+)</a>', action_html, re.IGNORECASE | re.DOTALL)
        
        if links:
            # For multiple links (e.g., two tel:), process all; prioritize HTTP for interactive
            http_links = [(h, l) for h, l in links if h.startswith('http')]
            tel_links = [(h, l) for h, l in links if h.startswith('tel:')]
            
            # If HTTP present: Use cta_url for direct open (single, as limit 1 per msg)
            if http_links:
                href, button_label = http_links[0]
                button_label = button_label.strip()  # e.g., "Open Map"
                
                # Translate label if needed (simple; extend with COMMON_PHRASES)
                translated_label = button_label  # Default
                if lang == 'hi':
                    if 'map' in button_label.lower():
                        translated_label = "नक्शा खोलें"
                    elif 'facebook' in button_label.lower():
                        translated_label = "फेसबुक खोलें"
                    elif 'instagram' in button_label.lower():
                        translated_label = "इंस्टाग्राम खोलें"
                    elif 'youtube' in button_label.lower():
                        translated_label = "यूट्यूब खोलें"
                    elif 'website' in button_label.lower() or 'vmanshi' in href:
                        translated_label = "वेबसाइट खोलें"
                    elif 'calendar' in button_label.lower():
                        translated_label = "कैलेंडर में जोड़ें"
                    else:
                        translated_label = "लिंक खोलें"
                # Add more langs/translations as needed
                
                # Truncate to 20 chars max (WhatsApp CTA limit)
                translated_label = translated_label[:20] if len(translated_label) > 20 else translated_label
                
                payload["type"] = "interactive"
                payload["interactive"] = {
                    "type": "cta_url",
                    "body": {"text": reply_text},
                    "action": {
                        "name": "cta_url",
                        "parameters": {
                            "display_text": translated_label,
                            "url": href  # Use extracted href (specific to intent)
                        }
                    },
                    "footer": {"text": "Golden Tree Garments"}
                }
                print(f"Direct URL open setup for: {href} (label truncated to: {translated_label})")
            
            # For tel: links: Enhance reply_text with formatted numbers (WhatsApp auto-links for tap-to-dial)
            if tel_links:
                primary_num = re.sub(r'tel:\+?91?', '', tel_links[0][0])  # e.g., '9310480772'
                secondary_num = re.sub(r'tel:\+?91?', '', tel_links[1][0]) if len(tel_links) > 1 else None
                full_primary = f"+91 {primary_num}"  # Spaced for readability/auto-link
                full_secondary = f"+91 {secondary_num}" if secondary_num else None
                
                # Append/ensure numbers in text for auto-dial (no interactive—direct tap on number)
                dial_text = f"\n\n{ 'अभी कॉल करें: ' if lang == 'hi' else 'Tap to call: '}{full_primary}"
                if full_secondary:
                    dial_text += f" or {full_secondary}"
                reply_text += dial_text  # Update body
                payload["text"]["body"] = reply_text
                print(f"Auto-dial numbers added to text: {full_primary}, {full_secondary or 'N/A'}")
        
        # Debug print—only if links found
        if links:
            print(f"Extracted links: {links} → HTTP: {http_links}, Tel: {tel_links} → Payload type: {payload.get('type', 'text')}")

    # Send the payload (text with auto-dial numbers or cta_url—no reply-sending buttons)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    api_response = requests.post(wa_url, json=payload, headers=headers)
    
    if api_response.status_code == 200:
        print("SUCCESS: Reply sent from business profile." + (" (with direct action)" if payload.get('type') != 'text' else " (with auto-dial numbers)"))
    else:
        print(f"ERROR Sending: {api_response.status_code} - {api_response.text}")

@csrf_exempt
@require_http_methods(["GET"])
def send_whatsapp_chatbot_response(request):
    """
    Tests: Simulate user msg to business → AI reply → Send FROM business profile TO recipient with optional buttons.
    Usage: GET /send-whatsapp-response/?phone=9199104723&msg=Hi (phone must start with 91 for India).
    - phone: Recipient (e.g., your personal number).
    - Works with business profile—no sandbox limits post-setup. No default buttons—only if AI intent requires.
    UX Upgrades:
    - Handles AI errors with friendly "server down" message.
    - Includes small delay for realism.
    """
    print("=== Testing Send FROM Business Profile with Optional Buttons ===")
    
    # Get params
    raw_phone = request.GET.get('phone', getattr(settings, 'WHATSAPP_TEST_RECEIVER', '9199104723'))
    user_message = request.GET.get('msg', 'Store timings?')
    
    print(f"Step 1: Recipient: '{raw_phone}', Simulated msg: {user_message}")
    
    # Business profile (sender)
    access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
    phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
    
    if not access_token or not phone_number_id:
        return JsonResponse({'error': 'Missing credentials in settings.py'}, status=500)
    
    print(f"Step 2: Business Sender ID: {phone_number_id}")
    
    # Format recipient
    try:
        receiver_wa = format_phone_for_wa(raw_phone)
        username = receiver_wa  # For AI session
    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)
    
    print(f"Step 3: Formatted Recipient: '{receiver_wa}'")
    
    # Step 4: Simulate incoming → Get AI response
    factory = RequestFactory()
    mock_data = json.dumps({'message': user_message})
    mock_request = factory.post(f'/chat/{username}/', mock_data, content_type='application/json')
    
    ai_error = False
    rate_limit_error = False
    try:
        mock_response = chat(mock_request, username)
        if mock_response.status_code == 200:
            response_data = json.loads(mock_response.content)
            arya_reply = response_data.get('reply', 'Sorry, something went wrong.')
            action_html = response_data.get('action_html', '')  # For button detection
            
            # Check for rate limit indicators in reply (e.g., if chat view appends error flag)
            if "API limit exceeded" in arya_reply or "quota" in arya_reply.lower():
                rate_limit_error = True
        else:
            ai_error = True
            arya_reply = 'Error processing message.'
            action_html = ''
    except Exception as e:
        print(f"AI Error: {e}")
        ai_error = True
        # Detect rate limit (common Gemini error patterns)
        error_str = str(e).lower()
        if any(keyword in error_str for keyword in ["quota", "rate limit", "resourceexhausted", "429"]):
            rate_limit_error = True
        arya_reply = 'Error processing message.'
        action_html = ''
    
    # Enhanced Error Handling for UX
    if ai_error or rate_limit_error:
        lang = detect_lang(user_message)
        arya_reply = get_error_reply(lang)
        action_html = ''  # No actions on error
        print(f"UX Error Response Sent: {arya_reply[:50]}... (Rate Limit: {rate_limit_error})")
    
    # Process reply for citations before sending
    arya_reply = process_reply_for_whatsapp(arya_reply)
    
    print(f"Step 5: AI Reply (processed): {arya_reply[:100]}...")
    
    # Small UX delay for "thinking"
    time.sleep(1.5)
    
    # Step 6: Send FROM business TO recipient with optional buttons (no default—only per action_html)
    lang = detect_lang(user_message)
    send_whatsapp_reply(receiver_wa, arya_reply, action_html, lang=lang)
    
    return JsonResponse({
        'success': True,
        'sender': f"Business Profile ({phone_number_id})",
        'recipient': raw_phone,
        'simulated_msg': user_message,
        'ai_reply': arya_reply,
        'action_html': action_html,  # For debug
        'message': f"Reply (with auto-dial numbers or direct actions only if AI intent requires—no reply-sending) sent to {raw_phone} from business profile!",
        'whatsapp_web_link': f"https://web.whatsapp.com/send?phone={receiver_wa}"
    })

# from django.conf import settings
# from django.http import JsonResponse
# import requests
# import json

# def test_send_message(request):
#     print("=== Starting test_send_message view ===")
    
#     # Use values from settings.py
#     test_sender = getattr(settings, 'WHATSAPP_TEST_SENDER', '')  # Test sender number (e.g., +15551909765)
#     print(f"Step 1: Loaded test_sender from settings: {test_sender}")
    
#     access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')  # Full token
#     print(f"Step 2: Loaded access_token from settings: {access_token[:20]}... (redacted for security)")
    
#     phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')  # e.g., 501...
#     print(f"Step 3: Loaded phone_number_id from settings: {phone_number_id}")
    
#     test_message = request.GET.get('msg', 'Hi Arya, what are the store timings?')  # Optional custom message via ?msg=...
#     print(f"Step 4: Loaded test_message from request: {test_message}")

#     if not access_token or not phone_number_id:
#         print("ERROR: Missing WHATSAPP_ACCESS_TOKEN or WHATSAPP_PHONE_NUMBER_ID in settings.py")
#         return JsonResponse({'error': 'Missing WHATSAPP_ACCESS_TOKEN or WHATSAPP_PHONE_NUMBER_ID in settings.py'}, status=500)

#     print("Step 5: All config loaded successfully.")

#     # Clean sender (remove + for payload)
#     clean_sender = test_sender.replace('+', '')
#     print(f"Step 6: Cleaned sender for payload: {clean_sender}")

#     # API call to simulate message from test sender to business number (triggers webhook)
#     wa_url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
#     print(f"Step 7: Built wa_url: {wa_url}")

#     wa_payload = {
#         "messaging_product": "whatsapp",
#         "to": clean_sender,  # Sends to test sender (Meta flips for webhook as "from")
#         "type": "text",
#         "text": {"body": test_message}
#     }
#     print(f"Step 8: Built wa_payload: {json.dumps(wa_payload, indent=2)}")  # Pretty print payload for debug

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }
#     print(f"Step 9: Built headers (Authorization redacted): Content-Type=application/json, Authorization length={len(access_token)}")

#     try:
#         print("Step 10: Making requests.post to WhatsApp API...")
#         api_response = requests.post(wa_url, json=wa_payload, headers=headers)
#         print(f"Step 10 Complete: API response status_code: {api_response.status_code}")
#         print(f"Step 10 Complete: API response headers: {dict(api_response.headers)}")  # Key headers
#         print(f"Step 10 Complete: API response text: {api_response.text}")  # Full response body for error details
        
#         if api_response.status_code == 200:
#             print("SUCCESS: API call succeeded - Webhook should be triggered now.")
#             # Success: Webhook triggered, Arya reply should arrive in test number's WhatsApp
#             return JsonResponse({
#                 'success': True,
#                 'test_sender': test_sender,
#                 'sent_message': test_message,
#                 'message': f"Test sent! Webhook triggered. Open WhatsApp Web for {test_sender} to see message and Arya reply.",
#                 'whatsapp_web_link': f"https://web.whatsapp.com/send?phone={clean_sender}"  # Link to open chat in browser
#             })
#         else:
#             print(f"ERROR: API call failed with status {api_response.status_code}. Full response: {api_response.text}")
#             return JsonResponse({
#                 'success': False,
#                 'error': f"WhatsApp API error ({api_response.status_code}): {api_response.text}",
#                 'test_sender': test_sender
#             }, status=500)
    
#     except Exception as e:
#         print(f"EXCEPTION in requests.post: Type={type(e).__name__}, Message={str(e)}")
#         import traceback
#         print("Full traceback:")
#         print(traceback.format_exc())
#         return JsonResponse({'error': f"Request failed: {str(e)}"}, status=500)

# print("=== test_send_message view definition complete ===")

# from django.conf import settings  # Already present
# from django.http import HttpResponse, JsonResponse  # Already present
# from django.test import RequestFactory  # Already present
# import json  # Already present
# import requests  # Ensure this is at the top of views.py (for API send)

# def test_whatsapp_send(request):
#     # Default test sender number (use Meta sandbox number for real WhatsApp visibility)
#     default_sender = getattr(settings, 'WHATSAPP_TEST_SENDER', '+15551909765')  # e.g., US test number; change to yours
#     test_message = request.GET.get('msg', 'Hi Arya, what are the store timings?')  # Optional ?msg=... for custom message
    
#     # Mock webhook payload with default sender (simulates incoming message)
#     mock_body = {
#         "entry": [{
#             "changes": [{
#                 "value": {
#                     "messages": [{
#                         "type": "text",
#                         "from": default_sender,  # Default sender phone (no +)
#                         "text": {"body": test_message}
#                     }]
#                 }
#             }]
#         }]
#     }
    
#     # Simulate request to your webhook's POST logic (extract/process/send)
#     try:
#         # Reuse webhook parsing (copy-paste core logic for isolation)
#         body = mock_body
#         change = body['entry'][0]['changes'][0]
#         message = change['value']['messages'][0]
#         user_phone = message['from']  # Default sender
#         user_message = message['text']['body']
#         username = user_phone.replace('+', '')  # Clean for session
        
#         # Simulate POST to chat view (Arya response) with error handling
#         factory = RequestFactory()
#         mock_data = json.dumps({'message': user_message})
#         mock_request = factory.post(f'/chat/{username}/', mock_data, content_type='application/json')
        
#         try:
#             mock_response = chat(mock_request, username)
#             print(f"Chat view response status: {mock_response.status_code}")  # Log for debug
#             print(f"Chat view content preview: {mock_response.content[:200]}...")  # Log snippet
#         except Exception as chat_error:
#             print(f"Chat view call error: {chat_error}")  # Log exact error
#             reply = COMMON_PHRASES.get('en', {}).get('error_reply', 'Error processing your message.')
#         else:
#             # Parse response with error handling
#             try:
#                 response_data = json.loads(mock_response.content)
#                 reply = response_data.get('reply', 'Sorry, something went wrong. Please try again.')
#             except (json.JSONDecodeError, ValueError) as parse_error:
#                 print(f"JSON parse error on chat response: {parse_error} (content: {mock_response.content})")
#                 reply = COMMON_PHRASES.get('en', {}).get('error_reply', 'Error processing your message.')
        
#         # Send reply via WhatsApp API to default sender
#         wa_access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
#         phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
#         if not wa_access_token or not phone_number_id:
#             return JsonResponse({'error': 'Missing WhatsApp config in settings.py'}, status=500)
        
#         wa_url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
#         wa_payload = {
#             "messaging_product": "whatsapp",
#             "to": user_phone,  # Sends to default sender
#             "type": "text",
#             "text": {"body": reply}  # Arya's response
#         }
#         headers = {
#             "Authorization": f"Bearer {wa_access_token}",
#             "Content-Type": "application/json"
#         }
#         api_response = requests.post(wa_url, json=wa_payload, headers=headers)
        
#         if api_response.status_code == 200:
#             return JsonResponse({
#                 'success': True,
#                 'sender_phone': user_phone,
#                 'sent_message': test_message,
#                 'arya_reply': reply,
#                 'message': f"Test sent! Check WhatsApp on {user_phone} for Arya's response."
#             })
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'error': f"WhatsApp API error: {api_response.text}",
#                 'sender_phone': user_phone
#             }, status=500)
    
#     except Exception as e:
#         print(f"Test view overall error: {e}")  # Log top-level error
#         return JsonResponse({'error': f"Test failed: {str(e)}"}, status=500)