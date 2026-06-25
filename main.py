import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime

# ========================================================
# CONFIGURAZIONE ID
# ========================================================
ID_RUOLO_VERIFICATO = 1519307669364674662
ID_RUOLO_STAFF_SETUP = 1519316973614268566  # Ruolo che può usare /setup e /widget

# URL del Banner per la verifica e il listino shop
URL_BANNER_VERIFICA = "https://cdn.discordapp.com/attachments/1516457598369533952/1518983715479490580/ce2828a1-7b03-46bb-b7d3-710697e0ae07.png?ex=6a3c9013&is=6a3b3e93&hm=e0d3d0c7f75e4cc65bab163778db658e5f8d6c72dbc2cdbec73f4dc4ab0cce40&"

# ========================================================
# COMPONENTI INTERFACCIA (VERIFICA)
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
# STRUTTURA DEL BOT
# ========================================================
class MioBotNuovo(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(VistaVerificaPrincipale())
        await self.tree.sync()

    async def on_ready(self):
        print(f"🚀 Bot Online come: {self.user}")

bot = MioBotNuovo()

# --------------------------------------------------------
# COMANDO 1: /setup (Portale Verifica)
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
# COMANDO 2: /widget (Listino Prezzi e Tier MKO Tweaks)
# --------------------------------------------------------
@bot.tree.command(name="widget", description="Crea il widget listino prezzi ufficiale dei pacchetti.")
@app_commands.describe(
    colore_hex="Colore barra laterale opzionale (Es: #2b2d31)",
    banner_url="Link alternativo per l'immagine di fondo dello shop"
)
async def crea_widget_personalizzato(
    interaction: discord.Interaction, 
    colore_hex: str = None, 
    banner_url: str = None
):
    await interaction.response.defer(ephemeral=True)
    ruolo_staff = interaction.guild.get_role(ID_RUOLO_STAFF_SETUP)
    
    if ruolo_staff not in interaction.user.roles:
        await interaction.followup.send("❌ Permessi insufficienti.", ephemeral=True)
        return

    # Colore scuro integrato a tema Discord (o personalizzato se inserito)
    colore_embed = discord.Color.from_str("#2b2d31")
    if colore_hex:
        try:
            colore_embed = discord.Color.from_str(colore_hex if colore_hex.startswith("#") else f"#{colore_hex}")
        except ValueError:
            pass

    embed = discord.Embed(
        title="🏆 MAKO TWEAKS — OFFICIAL STORE",
        description="Scegli il livello di ottimizzazione perfetto per le tue esigenze hardware e di gaming.\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        color=colore_embed
    )

    # Iniezione dei tuoi Tier reali all'interno della griglia organizzata
    embed.add_field(
        name="🟢 TIER 01: BASIC TWEAK — 5€", 
        value="• Pulizia file temporanei\n• Ottimizzazione Windows base\n• Debloat leggero del sistema", 
        inline=False
    )
    
    embed.add_field(
        name="🔵 TIER 02: ADVANCED TWEAKS — 10€", 
        value="• Tutti i tweak del piano **Basic**\n• Riduzione dell'Input Lag\n• Power Plan personalizzato\n• Ottimizzazione RAM", 
        inline=False
    )
    
    embed.add_field(
        name="👑 TIER 03: ULTRA TWEAKS — 25€", 
        value="• Tutti i tweak del piano **Advanced**\n• Deep Debloat completo\n• Ottimizzazione GPU & CPU\n• Configurazione Bios base\n• Network Lag Reduction", 
        inline=False
    )
    
    embed.add_field(
        name="🔥 TIER 04: ELITE TWEAKS — 45€", 
        value="• Full System Tuning hardware\n• Massimo FPS Boost & Stabilità\n• Ottimizzazione periferiche\n• Overclock sicuro + Stress Test\n• Assistenza VIP prioritaria", 
        inline=False
    )

    embed.add_field(
        name="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        value="🛒 **Come Acquistare:** Apri un ticket nel canale predisposto o contatta direttamente lo Staff.",
        inline=False
    )

    # Imposta il banner (usa quello di default se non viene inserito come parametro nel comando)
    embed.set_image(url=banner_url if banner_url else URL_BANNER_VERIFICA)
    
    icona_server = interaction.guild.icon.url if interaction.guild.icon else None
    embed.set_footer(text="Mako Tweaks • Verified Optimization System", icon_url=icona_server)
    embed.timestamp = datetime.now()

    await interaction.channel.send(embed=embed)
    await interaction.followup.send("✅ Widget listino inviato correttamente!", ephemeral=True)

# ========================================================
# AVVIO
# ========================================================
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("ERRORE: Variabile DISCORD_TOKEN mancante.")
