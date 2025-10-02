import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, Defaults, filters
)
from telegram.error import Forbidden

# ---------- LOGGING ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("krudtdk-bot")

# ---------- TEKSTER ----------
WELCOME = (
    "👋 Velkommen til KrudtDK! 💪🔥\n\n"
    "Jeg er KrudtDK's bot – din guide til alt om peptides, tilskud, cycles og mere 💉🧪\n\n"
    "❓ Spørg løs! Her er plads til både nye drenge i gården og gamle kæmper – ingen spørgsmål er for dumme 💬\n\n"
    "👇 Nedenfor finder du alt det saftige samlet ét sted:\n"
    "🥦 Health Guide – hvordan du passer på kroppen\n"
    "💊 Tilskud & protokoller – hvad virker og hvad er spild af penge\n"
    "📈 Performance – maks ud af dit stack\n"
    "💸 Forhandlere, betaling & fragt – hvem, hvad, hvor og hvordan\n"
    "💉 Peptides & Krudt – viden, erfaringer og doserings-tips\n\n"
    "⚠️ HUSK: Det her er ikke et spil – lyt til kroppen, lav din research og tag ansvar. "
    "Det handler om at blive større, stærkere og blive ved med at være i game 💯"
)



PAGES = {
    "blodprover": (
        "🩸 <b>Blodprøver Guide - Din Sikkerhed Først</b>\n\n"
        "🧪 <b>Hvorfor blodprøver?</b>\n"
        "Blodprøver er dit vigtigste værktøj for sikker brug af AAS og peptides. De viser dig præcis hvordan kroppen reagerer og hvornår du skal justere.\n\n"
        "📊 <b>Hvad skal du teste?</b>\n\n"
        "<u>Før kur:</u>\n"
        "• Testosteron (total og frit)\n• Estradiol (E2)\n• LH/FSH\n• Prolaktin\n• Blodtal (RBC, HCT, HGB)\n"
        "• Leverværdier (ALT, AST, GGT)\n• Nyrer (kreatinin, eGFR)\n• Lipider (kolesterol, triglycerider)\n\n"
        "<u>Midtvejs (uge 8-10):</u>\n"
        "• Testosteron og E2\n• Leverværdier\n• Blodtal\n• Justér dosering baseret på resultater\n\n"
        "<u>Efter kur:</u>\n"
        "• Alle værdier fra før kur\n• Sammenlign og vurder skade\n\n"
        "🏥 <b>Hvor kan du tage prøver?</b>\n"
        "• Privat klinik (fx private laboratorier)\n"
        "• Egen læge (nogle er villige)\n"
        "• Online services (kommercielle test-tjenester)\n\n"
        "💰 <b>Priser (cirka):</b>\n• Basis pakke: 800-1200 kr.\n• Komplet pakke: 1500-2500 kr.\n\n"
        "⚠️ <b>VIGTIGT:</b>\n"
        "• Tag altid blodprøver før du starter\n• Justér dosering baseret på resultater\n"
        "• Stop kur og kontakt læge ved markante afvigelser\n\n"
        "🔬 <b>Læs mere:</b>\nSe vores FAQ/Wiki for detaljerede guides."
        "https://www.nayamr.dk/vi-tilbyder/blodproever/hansen-pakken.aspx"
    ),

    # Forhandlere bruger variablen (nem at copy-paste/udskifte)
    "forhandlere": (
        """🔒 KRUDT DK – LEGIT LISTE

Brug kun godkendte forhandlere, for at undgå scams, svindel og uoriginale produkter.

LABTEST M.M FINDES PÅ https://t.me/krudtdkfaq

✅(Legit forhandlere med labtestet mærker)✅

@jensensboeffer1 / @BoeffensParadis (Jylland)
(ADEX PHARMA) (NEXGEN PEPTIDES)
• Krudt • Peptider • Potens • Medicin • Slankemidler
FRAGT TILBYDES

@Topshop.11 (Signal) / @Topshopkbh4 (Telegram) 
(ADVAR PHARMA)
• Krudt • Medicin • Tilbehør
FRAGT TILBYDES

@Gangland5 (Sjælland) 
(ADVAR PHARMA) 
• Krudt • Peptider • Potens • Medicin • Slankemidler
FRAGT TILBYDES

@AdexpharmDK (Sjælland) 
(ADEX PHARMA) 
• Krudt • Peptider • Potens • Medicin • Slankemidler
FRAGT TILBYDES

@Krudtogkugler3 (Sjælland) 
(ADVAR PHARMA) 
• Krudt • Peptider • Potens • Medicin • Slankemidler 
FRAGT TILBYDES

@muskelfar (jylland) 
(Driada Medical)
• Krudt • Peptider • Potens • Medicin • Slankemidler
FRAGT TILBYDES

(Legit forhandlere uden labtestet produkter)‼️

@mathigear (Sjælland) 
(Vaxinas)
• Krudt • Peptider • Potens

📑 Dokumentation & Kontrol
Alle forhandlere på listen skal løbende levere dokumentation for deres handler.
Dette sikrer, at kun seriøse og stabile sælgere forbliver på listen.

📩 Spørgsmål? Kontakt Krudt DK – Admin Team.

⸻

🚫 SCAMMER- & SVINDLERLISTE
@Overarm21 """
        ),
        
    "trt": (
        "💉 <b>TRT & Blodprøver – vigtigt at holde styr på!</b> 💉\n\n"
        "Hvis du kører TRT (eller anden kørsel), så husk at blodprøver ikke bare er en formalitet – de er din sikkerhed for at kroppen faktisk har det, som den skal.\n\n"
        "🔍 <b>Det vigtigste du bør holde øje med:</b>\n"
        "• Total testosteron & fri testosteron – stabilt, ikke for lavt/højt\n"
        "• Østradiol (E2) – for meget: bivirkninger; for lidt: led/humør/libido\n"
        "• SHBG – hvor meget test er frit tilgængeligt\n"
        "• Hæmatokrit & hæmoglobin – for tykt blod øger risici\n"
        "• Lever- og nyretal (ALAT, ASAT, kreatinin, eGFR)\n"
        "• Lipider (total, HDL, LDL, triglycerider)\n"
        "• PSA – prostata-sundhed\n\n"
        "📌 <b>Tip:</b> Tag prøver hver 3.–6. måned hvis du er på TRT.\n\n"
        "⚖️ <b>TRT dosering – typiske rammer</b>\n"
        "• Testosteron Enanthate / Cypionate: <b>125–180 mg/uge</b> (1 stik eller delt i 2 for mere stabile niveauer)\n\n"
        "Bemærk: Dosering bør altid justeres ud fra blodprøver og kliniske symptomer. Tal med læge ved afvigelser."
    ),

    "fragt": (
        "📦 <b>Fragt-info</b> 📦\n\n"
        "Fragt aftales altid direkte med forhandleren. Oftest bruges DAO til levering.\n\n"
        "✅ Kunden kan købe eget DAO-label (ofte billigst og nemmest)\n"
        "✅ Levering til pakkeshop anbefales for fleksibel afhentning\n"
        "✅ Angiv korrekt <b>e-mail</b>, så du modtager hentekode og status\n\n"
        "🔒 <b>Privatliv & regler</b>\n"
        "• Del kun nødvendige oplysninger og følg transportørens krav\n"
        "• Brug pakkeshop når muligt, og medbring gyldig legitimation ved afhentning\n"
        "• Overhold altid gældende lovgivning og fragtudbyderens handelsbetingelser"
    ),

    "firstcycle": (
        "💥 <b>Blast Cycle Guide</b>\n\n"
        "For at få adgang til blast cycle guide, start venligst en privat chat med botten:\n\n"
        "👉 <a href=\"https://t.me/KrudtDK_Bot\">@KrudtDK_Bot</a> 👈 <b>KLIK HER</b>\n\n"
        "Har du allerede en aktiv chat med botten så åben den og skriv /menu\n\n"
        "Der finder du: ⚠️ Sikkerhedsregler • 📊 Blodprøver først • 💉 Korrekt dosering • 📅 Timing og planlægning\n\n"
        "🏆 <b>Cycle Designs:</b>\n"
        "• Holy Trinity: Test/Primo/Anavar\n"
        "• Cutstack: Test/Mast/Tren\n"
        "• SU-kuren: Test/EQ\n"
        "• Hannah Montana: Test/Primo/Mast\n"
        "• Rafineret Super Bulk: Test/NPP/Mast\n"
        "• Greek God Unlocked: Test/Primo/Mast/Tren/Anavar"
    ),

    "troll": (
        "🚀 <b>Troll Command</b>\n\n"
        "For at få adgang til troll funktionen, start venligst en privat chat med botten:\n\n"
        "👉 <a href=\"https://t.me/KrudtDK_Bot\">@KrudtDK_Bot</a> 👈 <b>KLIK HER</b>\n\n"
        "Der finder du:\n🚀💎 /CHAD_EFFECT - hop ind i Chads hellige cryptokrig\n💎🚀 FLYV TIL MÅNEN 💎🚀"
    ),

    "coaching": (
        "🔥 <b>Online Coaching – Resultater der taler for sig selv</b> 🔥\n\n"
        "💰 <b>Priser:</b>\n"
        "• 125$ / 800 kr. pr. måned\n"
        "• 315$ / 2.000 kr. / 3 mdr.\n"
        "• 595$ / 3.800 kr. / 6 mdr.\n"
        "• 940$ / 6.000 kr. / 12 mdr.\n\n"
        "✅ <b>Du får som klient:</b>\n"
        "• Skræddersyet kost- & træningsplan\n"
        "• Supplement- & evt. PED-plan\n"
        "• Blodprøveanalyse for sundhed & performance\n"
        "• Posing-coaching\n"
        "• 24/7 Telegram-support\n"
        "• Opkald/sparring + check-ins (oftere i prep)\n"
        "• Fokus på mental sundhed & performance\n\n"
        "📍 Personlig træning i Aarhus, Odense, Kbh, Kolding & Esbjerg\n\n"
        "👉 Vil du høre mere? Skriv til <a href=\"https://t.me/RevZyro\">@RevZyro</a>"
    ),

    "peptides": (
        "💉 <b>Peptider – de skjulte værktøjer i din toolbox</b>\n\n"
        "Peptider er små kæder af aminosyrer – kroppens egne byggesten. De kan hjælpe på flere måder alt efter hvilket peptide du bruger:\n"
        "• 🔥 Øget fedtforbrænding & energi\n"
        "• 💪 Hurtigere restitution & mindre inflammation\n"
        "• 🍽️ Øget appetit eller bedre søvn\n"
        "• 🧠 Fokus & velvære\n\n"
        "⚠️ Vigtigt: Peptider er ikke legetøj – det kræver viden og ansvar at bruge dem rigtigt. Lyt til kroppen, lav din research og husk, at mindre ofte er mere."
    ),

    "betaling": (
        "💳 <b>Betaling</b>\nBetaling aftales altid direkte med sælgeren. Metode og detaljer varierer, så husk at afklare alt, inden du handler ✅"
    ),

    "supplements": (
        "💊 <b>Supplements & Krudt – hvorfor det hænger sammen</b>\n\n"
        "Når man kører gear, stiller man kroppen på overarbejde – hormoner, organer og kredsløb bliver presset langt mere end normalt. "
        "Her kan de rigtige kosttilskud gøre en kæmpe forskel:\n"
        "• ❤️ Hjerte & blodtryk – f.eks. Omega-3, CoQ10, Taurin\n"
        "• 🩸 Lever & nyrer – NAC, TUDCA, elektrolytter\n"
        "• 🧠 Mentalt & søvn – Magnesium, Glycin\n"
        "• 💪 Performance – Creatin, EAA, L-Carnitin\n\n"
        "⚠️ Husk: Krudt uden health-support er som at køre bil uden bremser."
    ),

    "cycledesign": "💪 Cycle Design – struktur, deloads, sundhedschecks."
}

# ---------- MENU ----------
def main_menu_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🧰 Forhandlere", callback_data="forhandlere"),
         InlineKeyboardButton("💳 Betaling & Krypto", callback_data="betaling")],
        [InlineKeyboardButton("📦 Fragt", callback_data="fragt"),
         InlineKeyboardButton("🧬 Peptides", callback_data="peptides")],
        [InlineKeyboardButton("🧔 TRT", callback_data="trt"),
         InlineKeyboardButton("🎯 First Cycle", callback_data="firstcycle")],
        [InlineKeyboardButton("💪 Cycle Design", callback_data="cycledesign"),
         InlineKeyboardButton("💊 Supplements", callback_data="supplements")],
        [InlineKeyboardButton("🩸 Blodprøver", callback_data="blodprover"),
         InlineKeyboardButton("🏋️ Coaching", callback_data="coaching")],
        [InlineKeyboardButton("🚀 Troll", callback_data="troll")],
    ]
    return InlineKeyboardMarkup(rows)

# ---------- HANDLERS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /start svarer i den chat, hvor brugeren skriver
    await update.message.reply_text(WELCOME, reply_markup=main_menu_keyboard())

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Når /menu skrives: prøv at sende menuen som DM til brugeren.
    Hvis botten ikke kan sende DM (Forbidden), så svar i gruppen med instruktion.
    """
    user = update.effective_user
    bot_username = context.bot.username or "KrudtDK_Bot"
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=WELCOME,
            reply_markup=main_menu_keyboard(),
            parse_mode=ParseMode.HTML
        )
        # Hvis kommandoen kom fra en gruppe, sig at DM er sendt
        if update.effective_chat and update.effective_chat.type != "private":
            await update.message.reply_text("📩 Jeg har sendt dig menuen i en privat besked.")
    except Forbidden:
        # Bot kan ikke sende DM (brugeren skal starte en samtale med botten først)
        start_link = f"https://t.me/{bot_username}"
        reply = (
            "❗ Jeg kan ikke sende dig en privat besked. Det betyder enten, at du ikke "
            "har startet en samtale med botten endnu, eller at du har blokeret private beskeder.\n\n"
            f"For at få menuen: start en privat chat med botten her: {start_link} og skriv /menu igen."
        )
        # Svar i samme chat (gruppe/privat)
        if update.effective_chat:
            await update.message.reply_text(reply)

# Inline-knapper: send ALTID NY besked (ingen redigering)
async def on_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data
    text = PAGES.get(key, "Ups – siden findes ikke endnu.")
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=main_menu_keyboard(), parse_mode=ParseMode.HTML)

# Grupper: keywords/banter
async def group_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    text = (msg.text or msg.caption or "").lower()

    # Synthol svar
    if "syntholan" in text or "synthol" in text:
        await msg.reply_text("FLUESUPPE🤮")
        return

    # Banter trigger
    if "luk røven bot" in text:
        await msg.reply_text("luk selv røven lille natty")
        return

def build_app():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("Sæt BOT_TOKEN som miljøvariabel.")
    defaults = Defaults(parse_mode=ParseMode.HTML)
    app = ApplicationBuilder().token(token).defaults(defaults).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(on_click))
    app.add_handler(
        MessageHandler(
            (filters.TEXT | filters.CAPTION) & ~filters.COMMAND & filters.ChatType.GROUPS,
            group_text_router
        )
    )
    return app

if __name__ == "__main__":
    app = build_app()
    log.info("Starting KrudtDK bot…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
