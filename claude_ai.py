import logging
import random
import anthropic
import config

logger = logging.getLogger(__name__)
_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

_VELCAVS_SYSTEM = """
You are the content writer for Velcavs, a premium Kenyan Telegram channel.
Your voice:
- Write in a natural mix of English, Kiswahili, and Sheng
- Warm, dramatic, and emotionally gripping
- Romantic, suggestive, and spicy — think romance novel energy
- Occasionally funny and relatable
- Always leave the reader wanting more
Sheng words to use: babe, mpenzi, usiku, upendo, roho, moyoni, dame, dude,
sawa, kweli, niko, nilikuwa, alikuwa, maze, aki, eish, ngai, eti, yaani
All characters are adults aged 22 and above.
"""


def _ask(prompt, max_tokens=600):
    try:
        resp = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=max_tokens,
            system=_VELCAVS_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text.strip()
    except Exception as exc:
        logger.error(f"Claude API error: {exc}")
        return ""


def heartbreak_story():
    hooks = [
        "She sent back his hoodie. Inside the pocket was a note that said 'I found the receipt for her ring.'",
        "He said 'I need space.' Three days later her best friend posted a photo from his bedroom.",
        "They were together four years. She found out through a wedding invitation that came to her address.",
        "He said she was crazy for suspecting. Then his phone lit up at 2am. The contact name was 'Work'.",
        "She packed her things at midnight. He didn't even come out of the bedroom to stop her.",
    ]
    hook = random.choice(hooks)
    text = _ask(
        f"Write a gripping heartbreak story for Velcavs. Start with: '{hook}' "
        f"200-280 words. English-Kiswahili-Sheng mix. End on an emotional gut-punch line.",
        max_tokens=500,
    )
    return text or f"💔 {hook}\n\n[Story loading — check back soon...]"


def romantic_fiction_story():
    settings = [
        "a late-night matatu ride from town to Westlands",
        "a rooftop party in Kilimani where two strangers keep finding each other",
        "a Nairobi coffee shop during a thunderstorm",
        "a gym in Karen where two people have been stealing glances for weeks",
        "an elevator in a CBD office building that gets stuck",
    ]
    setting = random.choice(settings)
    text = _ask(
        f"Write a romantic fiction story set in: {setting}. "
        f"For Velcavs. 220-300 words. English-Kiswahili-Sheng mix. "
        f"Two adult characters aged 24-32. Sensual tension, slow burn. "
        f"End with a cliffhanger. Sign off with: Full story iko VIP side tu.",
        max_tokens=550,
    )
    return text or f"A story is brewing in {setting}... stay tuned."


def situationship_story():
    text = _ask(
        "Write a relatable situationship story for Velcavs. 200-260 words. "
        "Two adults in that confusing space between together and strangers. "
        "English-Kiswahili-Sheng mix. Emotional, a little funny, a little painful. "
        "End with a question that makes readers want to share their own story.",
        max_tokens=500,
    )
    return text or "Situationship stories hit different... 🫠"


def cheating_twist_story():
    text = _ask(
        "Write a dramatic cheating story with a shocking twist ending for Velcavs. "
        "200-270 words. English-Kiswahili-Sheng mix. "
        "The twist comes in the last paragraph. Characters are adults. "
        "End with: Did you see that coming? Drop your reaction below.",
        max_tokens=500,
    )
    return text or "Some stories you don't see coming..."


def late_night_thoughts():
    text = _ask(
        "Write a late-night emotional monologue for Velcavs. "
        "The kind of thing someone texts their ex at 1am but deletes before sending. "
        "150-200 words. First person. English-Kiswahili-Sheng mix. "
        "Start with the time e.g. 1:47am. "
        "End with them deciding NOT to send it.",
        max_tokens=400,
    )
    return text or "1:47am and the thoughts won't stop... 🌙"


def love_confession():
    text = _ask(
        "Write a romantic love confession story for Velcavs. "
        "One person finally tells their best friend they are in love with them. "
        "200-260 words. English-Kiswahili-Sheng mix. "
        "Nervous energy, racing heart, almost funny but deeply sweet. "
        "Leave the reaction for the premium version. "
        "End with: Full story na conclusion iko VIP side tu.",
        max_tokens=500,
    )
    return text or "Some words take years to say... ❤️"


def breakup_scene():
    text = _ask(
        "Write a raw emotional breakup scene for Velcavs. "
        "The final conversation between two people who still love each other but cannot make it work. "
        "230-290 words. Written like a script with dialogue. "
        "English-Kiswahili-Sheng mix. "
        "Last line should be the one that stays with you.",
        max_tokens=550,
    )
    return text or "Some goodbyes take forever and a second at the same time... 💔"


_STORY_FNS = {
    "heartbreak": heartbreak_story,
    "romantic_fiction": romantic_fiction_story,
    "situationship": situationship_story,
    "cheating_twist": cheating_twist_story,
    "late_night_thoughts": late_night_thoughts,
    "love_confession": love_confession,
    "breakup": breakup_scene,
    "relationship_drama": situationship_story,
}


def generate_story(category=None):
    if not category or category not in _STORY_FNS:
        category = random.choice(list(_STORY_FNS.keys()))
    return _STORY_FNS[category]()


def generate_premium_story(category=None):
    story = generate_story(category)
    return "👑 VIP EXCLUSIVE — Full Story\n\n" + story


def promo_caption():
    angles = [
        "tease what is in the premium channel — longer stories, no censorship, exclusive content",
        "create FOMO — what premium members are reading right now that public cannot see",
        "make it about value — less than lunch money for a month of premium content",
        "emotional angle — the stories that make you feel everything are in the VIP side",
    ]
    angle = random.choice(angles)
    text = _ask(
        f"Write a short enticing promo message for Velcavs public channel. "
        f"Angle: {angle}. Max 120 words. English-Kiswahili-Sheng mix. "
        f"Use emojis. Sound like a friend hyping something. "
        f"End with a clear call to action to tap the join button below.",
        max_tokens=250,
    )
    return text or (
        "Watu wa VIP channel wanasoma content ambayo public side haitawahi ona...\n\n"
        "Longer stories. More drama. Zero censorship.\n\n"
        "Jiunge sasa — bei ni chini kuliko lunch yako 👇"
    )


def auto_post_story_with_promo():
    story = generate_story()
    promo = _ask(
        "Write a 2-sentence teaser that connects to a romantic story just read "
        "and pushes the reader to join the premium Velcavs channel. "
        "English-Kiswahili-Sheng. Casual, exciting, FOMO-inducing.",
        max_tokens=120,
    )
    divider = "\n\n" + "—" * 20 + "\n\n"
    return story + divider + (promo or "Full version + more premium stories — VIP tu!")


def welcome_message(first_name):
    text = _ask(
        f"Write a warm welcome message for {first_name} who just started the Velcavs bot. "
        f"Tell them Velcavs is the home of Nairobi's hottest romantic fiction and heartbreak stories. "
        f"Mention the premium channel has full uncut stories. "
        f"Max 150 words. English-Kiswahili-Sheng mix. Friendly and exciting.",
        max_tokens=300,
    )
    return text or (
        f"Aisee {first_name}! Karibu Velcavs!\n\n"
        "Hapa ndio home ya Nairobi's hottest stories — romance, heartbreak, drama.\n\n"
        "Public channel ina the teaser. VIP channel ina the full story — uncut, uncensored.\n\n"
        "Chagua plan yako na uingie VIP side 👇"
    )


def plans_intro():
    text = _ask(
        "Write a short enticing message max 120 words for Velcavs presenting subscription plans. "
        "Make premium sound irresistible. English-Kiswahili-Sheng. "
        "End asking them to pick their plan.",
        max_tokens=250,
    )
    return text or (
        "💎 Velcavs VIP — Chagua Plan Yako\n\n"
        "Bei ndogo. Content kubwa. Zero regrets.\n\n"
        "Kila plan inakupa full access ya premium stories.\n\n"
        "👇 Chagua plan inakufaa:"
    )


def payment_instructions(first_name, plan_label, amount, phone, paybill):
    text = _ask(
        f"Write friendly M-Pesa payment instructions for {first_name}. "
        f"They chose {plan_label} at KSH {amount}. "
        f"Tell them to send KSH {amount} to Paybill {paybill}, phone {phone}. "
        f"Reassuring, warm, max 100 words. English-Kiswahili mix.",
        max_tokens=200,
    )
    return text or (
        f"Sawa {first_name}!\n\n"
        f"Tuma KSH {amount} via M-Pesa:\n\n"
        f"Paybill: {paybill}\n"
        f"Account: {phone}\n"
        f"Amount: KSH {amount}\n\n"
        "Baada ya kulipa, bonyeza hapo chini — tutakuactivate mara moja!"
    )


def success_message(first_name, plan_label, expiry):
    text = _ask(
        f"Write an exciting welcome-to-VIP message for {first_name} "
        f"who just subscribed to Velcavs {plan_label}. "
        f"Access is active until {expiry}. "
        f"Hype them up. Max 130 words. English-Kiswahili-Sheng.",
        max_tokens=280,
    )
    return text or (
        f"Wewe ni VIP sasa {first_name}!\n\n"
        f"{plan_label} imeactiviwa — valid until {expiry}\n\n"
        "Stories za premium zinakungoja. Full length. Full drama. Zero cuts.\n\n"
        "Bonyeza chini uingie!"
    )


def expiry_warning(first_name, plan_label, hours_left):
    text = _ask(
        f"Write a gentle renewal reminder for {first_name} — their Velcavs "
        f"{plan_label} expires in about {hours_left} hours. "
        f"Casual, friendly, FOMO. Max 80 words. English-Kiswahili-Sheng.",
        max_tokens=160,
    )
    return text or (
        f"{first_name}, VIP yako inakwisha in {hours_left} hours!\n\n"
        "Renew haraka usikose content — stories mpya zinapost kila siku VIP side."
    )


def expired_message(first_name, plan_label):
    text = _ask(
        f"Write a friendly subscription expired message for {first_name} "
        f"Velcavs {plan_label}. Encourage renewal warmly. "
        f"Max 80 words. English-Kiswahili-Sheng.",
        max_tokens=160,
    )
    return text or (
        f"{first_name}, subscription yako imeexpire!\n\n"
        "Usirudi nyuma — renew sasa na uendelee na stories za moto!"
    )

