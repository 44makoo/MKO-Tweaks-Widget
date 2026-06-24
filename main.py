import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime

# ========================================================
# CONFIUGRAZIONE ID (Sostituisci con i tuoi ID di Discord)
# ========================================================
ID_RUOLO_VERIFICATO = 1519307669364674662
ID_RUOLO_STAFF_SETUP = 1519316973614268566  # Ruolo che può usare /setup e /widget

# URL del tuo Banner per la verifica
URL_BANNER_VERIFICA = "https://cdn.discordapp.com/attachments/1516457598369533952/1518983715479490580/ce2828a1-7b03-46bb-b7d3-710697e0ae07.png?ex=6a3c9013&is=6a3b3e93&hm=e0d3d0c7f75e4cc65bab163778db658e5f8d6c72dbc2cdbec73f4dc4ab0cce40&"

# ========================================================
# AGGIUNTI RIGUARDANTI IL SISTEMA DI VERIFICA
# ========================================================
class VistaConferma(View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Conferma e Accetta", style=discord.ButtonStyle.green, emoji="✅", custom_id="conferma_finale_univoco")
    async def conferma_button(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        ruolo = guild.get_role(ID_RUOLO_VERIFICATO)

        if ruolo is None:
            await interaction.response.send_message("❌ Errore: Ruolo di verifica non trovato.", ephemeral=True)
            return

        if ruolo in interaction.user.roles:
            await interaction.response.send_message("ℹ️ Sei già verificato nel server!", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(ruolo)
                for child in self.children:
                    child.disabled = True
                await interaction.response.edit_message(content="🎉 **Verifica completata!** Ruolo assegnato. Benvenuto!", view=self)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Errore di gerarchia: Metti il ruolo del Bot sopra quello da assegnare.", ephemeral=True)

class VistaVerificaPrincipale(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Inizia Verifica", style=discord.ButtonStyle.primary, emoji="🛡️", custom_id="pulsante_verifica_principale")
    async def inizia_verifica(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        ruolo = guild.get_role(ID_RUOLO_VERIFICATO)
        
        if ruolo and ruolo in interaction.user.roles:
            await interaction.response.send_message("ℹ️ Hai già completato la verifica!", ephemeral=True)
            return

        embed_regole = discord.Embed(
            title="👋 Ci sei quasi!",
            description=(
                "Accetta i punti fondamentali prima di entrare:\n\n"
                "🔹 **Rispetto:** Rispetta tutti i membri.\n"
                "🔹 **No Spam:** Non inviare link non autorizzati.\n"
                "🔹 **Regolamento:** Segui i Termini di Servizio di Discord.\n\n"
                "*Clicca sul pulsante verde per completare.*"
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed_regole, view=VistaConferma(), ephemeral=True)

# ========================================================
# STRUTTURA DEL BOT NOVO
# ========================================================
class MioBotNuovo(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Registra la vista persistente del pulsante di verifica
        self.add_view(VistaVerificaPrincipale())
        # Sincronizza i comandi slash (/) globalmente
        await self.tree.sync()

    async def on_ready(self):
        print(f"🚀 [{datetime.now().strftime('%H:%M:%S')}] Bot Online come: {self.user}")

bot = MioBotNuovo()

# --------------------------------------------------------
# COMANDO 1: /setup (Per il widget di verifica)
# --------------------------------------------------------
@bot.tree.command(name="setup", description="Invia il portale di verifica strutturato con banner.")
async def setup_verifica(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    ruolo_staff = interaction.guild.get_role(ID_RUOLO_STAFF_SETUP)
    
    if ruolo_staff not in interaction.user.roles:
        await interaction.followup.send("❌ Permessi insufficienti.", ephemeral=True)
        return

    embed_widget = discord.Embed(
        title="🔒 PORTALE DI VERIFICA",
        description=(
            "Benvenuto/a! Sblocca i canali del server superando la sicurezza.\n\n"
            "📌 **Istruzioni:**\n"
            "1️⃣ Clicca su **Inizia Verifica** qui sotto.\n"
            "2️⃣ Accetta il regolamento nel messaggio che apparirà.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=discord.Color.blurple()
    )
    embed_widget.set_image(url=URL_BANNER_VERIFICA)
    
    icona_server = interaction.guild.icon.url if interaction.guild.icon else None
    embed_widget.set_footer(text=f"{interaction.guild.name} • Sicurezza", icon_url=icona_server)
    
    await interaction.channel.send(embed=embed_widget, view=VistaVerificaPrincipale())
    await interaction.followup.send("✅ Widget di verifica inviato!", ephemeral=True)

# --------------------------------------------------------
# COMANDO 2: /widget (Per il listino stile Yusa Tweaks)
# --------------------------------------------------------
@bot.tree.command(name="widget", description="Crea il widget listino/servizi avanzato.")
@app_commands.describe(
    titolo="Titolo personalizzato dell'embed",
    sottotitolo="Descrizione sotto il titolo",
    colore_hex="Colore barra laterale (Es: #FF1493)",
    banner_url="Link di un'immagine/banner per il fondo"
)
async def crea_widget_personalizzato(
    interaction: discord.Interaction, 
    titolo: str = None, 
    sottotitolo: str = None, 
    colore_hex: str = None, 
    banner_url: str = None
):
    await interaction.response.defer(ephemeral=True)
    ruolo_staff = interaction.guild.get_role(ID_RUOLO_STAFF_SETUP)
    
    if ruolo_staff not in interaction.user.roles:
        await interaction.followup.send("❌ Permessi insufficienti.", ephemeral=True)
        return

    # Valori di default stile Yusa Tweaks
    titolo_def = "📦 Yusa Tweaks — Packages"
    desc_def = "Everything you need to get your PC running at full potential."
    colore_embed = discord.Color.from_str("#E91E63") # Rosa/Fucsia dell'immagine
    
    if colore_hex:
        try:
            colore_embed = discord.Color.from_str(colore_hex if colore_hex.startswith("#") else f"#{colore_hex}")
        except ValueError:
            pass

    embed = discord.Embed(
        title=titolo if titolo else titolo_def,
        description=sottotitolo if sottotitolo else desc_def,
        color=colore_embed
    )

    # Griglia Pacchetti (3 per riga)
    embed.add_field(name="BIOS Only — $15", value="BIOS configuration\n& tuning", inline=True)
    embed.add_field(name="Windows Tweak — $35", value="Full Windows\noptimization tweak", inline=True)
    embed.add_field(name="Advanced — $50", value="• Full BIOS tuning\n• Full Windows cleanup and optimization", inline=True)
    
    # Seconda riga pacchetti
    embed.add_field(name="Ultimate — $100", value="• Everything in Advanced\n• Deeper overclocking (CPU, GPU, RAM)\n• Advanced BIOS optimization", inline=True)
    embed.add_field(name="Gatekept — ~~~$250~~~ $200 (20% OFF)", value="• Everything in Ultimate\n• Max overclocks across the board\n• Prioritized service queue", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True) # Bilanciatore griglia

    # Sezioni full-width
    embed.add_field(name="🎬 Additional Services", value="**OBS Setup** — $35 · Hidden settings & stream config\n**Dual PC Setup** — $80 · Capture card, audio routing & optimization", inline=False)
    embed.add_field(name="⚡ Priority Upgrade", value="Any package can be upgraded to priority for **+$25** — moves you up in the service queue.", inline=False)
    embed.add_field(name="⚠️ Requirements", value="• **Must have a USB drive**\n• Staff will install Windows for you if needed", inline=False)
    embed.add_field(name="🔒 Chargeback Policy", value="If any customer attempts a chargeback after receiving a tweak — we record everything. We have full proof of purchase and the entire session recorded. All information will be provided to the bank to reverse the chargeback.", inline=False)

    embed.timestamp = datetime.now()

    if banner_url:
        embed.set_image(url=banner_url)

    await interaction.channel.send(embed=embed)
    await interaction.followup.send("✅ Widget listino inviato!", ephemeral=True)


# ========================================================
# AVVIO BOT (Railway)
# ========================================================
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("ERRORE: Variabile DISCORD_TOKEN mancante.")