import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import yt_dlp
import aiohttp
from discord.ui import Button, View
import os

intents = discord.Intents.default()
intents.message_content = True  # jeśli chcesz używać !komend
TOKEN = os.getenv("DISCORD_TOKEN")
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

async def setup_hook(self):
    guild = discord.Object(id=GUILD_ID)
    synced = await self.tree.sync(guild=guild)
    print(f"✅ Zsynchronizowano {len(synced)} komend slash na guild {GUILD_ID}.")

bot = MyBot()  # ← ZMIENNA bot MUSI BYĆ UTWORZONA przed dekoratorem @bot.event


@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')

# Komenda !status – zmiana statusu bota
@bot.command()
async def status(ctx, *, new_status: str):
    await bot.change_presence(activity=discord.Game(name=new_status))
    await ctx.send(f"✅ Status bota zmieniony na: **{new_status}**")

# Komenda !info – informacje o bocie
@bot.command()
async def info(ctx):
    embed = discord.Embed(title="🤖 C4ackPoland", color=discord.Color.blue())
    embed.add_field(name="Autor", value="cedek.aep", inline=True)
    embed.add_field(name="Wersja", value="3.0", inline=True)
    embed.add_field(name="Serwery", value=len(bot.guilds), inline=True)
    await ctx.send(embed=embed)

# Komenda !userinfo – informacje o użytkowniku
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 Informacje o użytkowniku: {member.name}", color=discord.Color.green())
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Dołączył", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)
@bot.command()
@commands.is_owner()
async def reset(ctx):
    await ctx.send("🔄 Bot się restartuje...")
    await bot.close()
    # Restart bota przez ponowne uruchomienie pliku
    os.execl(sys.executable, sys.executable, *sys.argv)
    
# Komenda !serverinfo – informacje o serwerze
@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title="🏰 Informacje o serwerze", color=discord.Color.purple())
    embed.add_field(name="Nazwa", value=guild.name, inline=True)
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Właściciel", value=guild.owner, inline=True)
    embed.add_field(name="Liczba członków", value=guild.member_count, inline=True)
    await ctx.send(embed=embed)

# Moderacja – blokowanie przekleństw
BAD_WORDS = ["przekleństwo1", "przekleństwo2", "przekleństwo3"]

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    for word in BAD_WORDS:
        if word in message.content.lower():
            await message.delete()
            await message.channel.send(f"🚨 {message.author.mention}, nie używaj takich słów!")
    
    await bot.process_commands(message)
# System XP i poziomów
user_xp = {}

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user = message.author
    user_xp[user.id] = user_xp.get(user.id, 0) + random.randint(5, 15)

    if user_xp[user.id] % 100 == 0:
        await message.channel.send(f"🎉 {user.mention} awansował na wyższy poziom!")

    await bot.process_commands(message)

@bot.command()
async def rank(ctx, member: discord.Member = None):
    member = member or ctx.author
    xp = user_xp.get(member.id, 0)
    await ctx.send(f"🏆 {member.mention} ma **{xp} XP**!")

# System ekonomii
user_money = {}

@bot.command()
async def saldo(ctx, member: discord.Member = None):
    member = member or ctx.author
    balance = user_money.get(member.id, 0)
    await ctx.send(f"💰 {member.mention} ma **{balance} monet**!")

@bot.command()
async def zarob(ctx, amount: int):
    user_money[ctx.author.id] = user_money.get(ctx.author.id, 0) + amount
    await ctx.send(f"💸 {ctx.author.mention} zarobił **{amount} monet**!")

# Tickety - system zgłoszeń
@bot.command()
async def ticket(ctx):
    guild = ctx.guild
    category = discord.utils.get(guild.categories, name="Tickety")
    
    if category is None:
        category = await guild.create_category("Tickety")

    ticket_channel = await guild.create_text_channel(f"ticket-{ctx.author.name}", category=category)
    await ticket_channel.send(f"{ctx.author.mention} zgłosił ticket! 🚀")
# Mini gry
@bot.command()
async def rzutkostka(ctx):
    wynik = random.randint(1, 6)
    await ctx.send(f"🎲 {ctx.author.mention} wyrzucił **{wynik}**!")

@bot.command()
async def quiz(ctx):
    pytania = [
        ("Który język programowania używany jest do tworzenia botów na Discorda?", "Python"),
        ("Jak nazywa się najdłuższa rzeka na świecie?", "Amazonka"),
        ("Ile boków ma pięciokąt?", "5")
    ]
    pytanie, odpowiedz = random.choice(pytania)
    
    await ctx.send(f"🧠 **Quiz:** {pytanie}")
    
    def check(m):
        return m.author == ctx.author

    try:
        msg = await bot.wait_for("message", check=check, timeout=10.0)
    except asyncio.TimeoutError:
        await ctx.send(f"⏳ {ctx.author.mention}, czas minął! Prawidłowa odpowiedź to: **{odpowiedz}**")
    else:
        if msg.content.lower() == odpowiedz.lower():
            await ctx.send(f"✅ {ctx.author.mention}, poprawnie!")
        else:
            await ctx.send(f"❌ {ctx.author.mention}, błędna odpowiedź! Poprawna: **{odpowiedz}**")

# Odtwarzanie muzyki
@bot.command()
async def play(ctx, url: str):
    voice_channel = ctx.author.voice.channel
    vc = await voice_channel.connect()
    
    ydl_opts = {"format": "bestaudio"}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info["url"]
    
    vc.play(discord.FFmpegPCMAudio(url2))
    await ctx.send(f"🎵 Odtwarzam: {info['title']}")

@bot.command()
async def stop(ctx):
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()
        await ctx.send("🛑 Muzyka zatrzymana!")

# AI Chat
@bot.command()
async def chatbot(ctx, *, message):
    odpowiedzi = ["Ciekawe pytanie!", "Hmm, muszę się nad tym zastanowić...", "Nie jestem pewien, ale brzmi dobrze!"]
    await ctx.send(f"🤖 AI Bot: {random.choice(odpowiedzi)}")

# Powiadomienia systemowe
@bot.command()
async def urodziny(ctx, member: discord.Member, data: str):
    await ctx.send(f"🎂 {member.mention} ma urodziny **{data}**!")

@bot.command()
async def stream(ctx, *, nazwa):
    await ctx.send(f"📢 **Stream:** {nazwa} zaczyna się teraz!")
# **Losowe Fakty**
@bot.command()
async def fakt(ctx):
    fakty = [
        "🌍 Na Wenus dzień trwa dłużej niż rok!",
        "🐙 Ośmiornice mają trzy serca!",
        "⚡ Energia wyprodukowana przez burzę wystarczyłaby do oświetlenia miasta!",
        "🍫 Czekolada była kiedyś używana jako waluta!"
    ]
    await ctx.send(random.choice(fakty))

# **Motywacyjne Cytaty**
@bot.command()
async def cytat(ctx):
    cytaty = [
        "💪 'Nie poddawaj się. Wielkie rzeczy wymagają czasu!'",
        "🚀 'Nie czekaj na okazję – stwórz ją sam!'",
        "🔥 'Każda porażka to krok do sukcesu!'",
        "✨ 'Bądź zmianą, którą chcesz zobaczyć w świecie.'"
    ]
    await ctx.send(random.choice(cytaty))

# **Generowanie żartów**
@bot.command()
async def zart(ctx):
    zarty = [
        "😆 Dlaczego komputer nie chodzi na siłownię? Bo ma za dużo RAMu!",
        "😂 Dlaczego matematyk został detektywem? Bo zawsze znajdzie X!",
        "🤣 Czemu programista nie lubi wody? Bo zawsze dostaje błędy typu 'float'!"
    ]
    await ctx.send(random.choice(zarty))

# **Losowe Wyzwania**
@bot.command()
async def wyzwanie(ctx):
    wyzwania = [
        "🏆 Wyzwanie! Napisz coś miłego dla kogoś na serwerze!",
        "🚀 Wyzwanie! Zmień swój status na coś zabawnego!",
        "🔥 Wyzwanie! Opowiedz swój ulubiony żart w czacie!"
    ]
    await ctx.send(random.choice(wyzwania))

# **Sprawdzanie czasu**
@bot.command()
async def czas(ctx):
    teraz = datetime.datetime.now().strftime("%H:%M:%S")
    await ctx.send(f"🕒 Aktualny czas: **{teraz}**!")

# **Personalizacja Bota**
@bot.command()
async def kolor(ctx, color: str):
    await ctx.send(f"🎨 Kolor bota zmieniony na: **{color}**!")

@bot.command()
async def nazwa(ctx, *, name: str):
    await bot.user.edit(username=name)
    await ctx.send(f"🤖 Nazwa bota zmieniona na: **{name}**!")

# **Easter Egg – Ukryta Komenda**
@bot.command()
async def sekretny(ctx):
    await ctx.send("🕵️‍♂️ Właśnie odkryłeś **sekretną komendę**!")

# **Lista Wszystkich Komend**
@bot.command()
async def komendy(ctx):
    embed = discord.Embed(
        title="📜 Lista komend bota",
        description=(
            "!info - informacje o bocie\n"
            "!serverinfo - informacje o serwerze\n"
            "!userinfo - informacje o użytkowniku\n"
            "!status - zmiana statusu bota\n"
            "!rank - wyświetla XP użytkownika\n"
            "!saldo - pokazuje saldo użytkownika\n"
            "!zarob - zarabianie monet\n"
            "!ticket - otwarcie ticketa\n"
            "!rzutkostka - rzut kostką\n"
            "!quiz - mini quiz\n"
            "!play - odtwarzanie muzyki\n"
            "!stop - zatrzymanie muzyki\n"
            "!chatbot - prosty chatbot\n"
            "!urodziny - powiadomienia urodzinowe\n"
            "!stream - powiadomienia o streamie\n"
            "!fakt - losowy fakt\n"
            "!cytat - motywujący cytat\n"
            "!zart - generowanie żartów\n"
            "!wyzwanie - losowe wyzwanie\n"
            "!czas - aktualny czas\n"
            "!kolor - zmiana koloru bota (tekstowo)\n"
            "!nazwa - zmiana nazwy bota\n"
            "!sekretny - ukryta komenda\n"
            "!propozycja - wysyłanie propozycji\n"
            "!robloxuser - informacje o użytkowniku Roblox\n"
            "!gry - darmowe gry\n"
            "!kasyno - gra kasynowa slot\n"
            "!say - powtórz wiadomość\n"
            "!tworca - informacje o twórcy\n"
            "!komende - ta lista komend"
        ),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)
@bot.command()
async def sprawdzamy(ctx):
    await ctx.send("TAK! Już sprawdzamy czy w naszej bazie danych jest taka gra. Prosimy o Poczekanie")
@bot.command()
async def hasla(ctx):
    embed = discord.Embed(
        title="WSZYSTKIE HASŁA",
        description="Tu znajdziesz wszystkie hasła",
        color=discord.Color.red()
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed.add_field(name="paczki", value="||c4ackpoland||", inline=True)
    embed.add_field(name="online-fix", value="||online-fix.me||", inline=True)
    embed.set_footer(text="Stworzył: cedek.aep")

    await ctx.send(embed=embed)
@bot.command()
async def tworca(ctx):
    embed = discord.Embed(
        title="Twórca Mnie ||XD||",
        description="Tu znajdziesz wszystko o mnie lol",
        color=discord.Color.red()
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed.add_field(name="Twórca", value="<@1068529373533184061>", inline=True)
    embed.add_field(name="Kiedy zostałem stworzony", value="06.05.2025", inline=True)
    embed.add_field(name="Wersja Bota", value="3.2", inline=True)
    embed.add_field(name="Twórcy serwera", value="<@1068529373533184061> , <@1358673876141473833>", inline=True)
    embed.add_field(name="Komendy pod:", value="!komendy", inline=True)
    embed.set_footer(text="Stworzył: cedek.aep")
    await ctx.send(embed=embed)
@bot.command()
async def say(ctx, *, message: str):
    try:
        await ctx.message.delete()  # Usuwa wiadomość użytkownika
    except discord.Forbidden:
        await ctx.send("❌ Nie mam uprawnień do usuwania wiadomości.")
        return
    except discord.HTTPException:
        await ctx.send("❌ Wystąpił błąd przy usuwaniu wiadomości.")
        return

    await ctx.send(message)
SUGGESTION_CHANNEL_ID = 1366790960679485488

@bot.command()
async def propozycja(ctx, *, tresc: str):
    channel = bot.get_channel(SUGGESTION_CHANNEL_ID)
    if channel is None:
        await ctx.send("❌ Nie mogę znaleźć kanału na propozycje.")
        return

    embed = discord.Embed(
        title="📢 Nowa propozycja!",
        description=tresc,
        color=discord.Color.blue()
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed.set_footer(text=f"ID użytkownika: {ctx.author.id}")

    try:
        await ctx.message.delete()  # Usuwa wiadomosc
        message = await channel.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        await ctx.send("✅ Twoja propozycja została wysłana!")

        # ==== DM do trzech użytkowników ====
        target_ids = [
            1338087563482890240,  # ← Wklej prawdziwe ID
            1358673876141473833,
            1068529373533184061
        ]

        for user_id in target_ids:
            user = await bot.fetch_user(user_id)
            if user:
                try:
                    await user.send(
                        f"📬 Nowa propozycja od **{ctx.author.name}**:\n```{tresc}```"
                    )
                except Exception as dm_error:
                    print(f"❌ Nie mogę wysłać DM do {user_id}: {dm_error}")

    except Exception as e:
        await ctx.send("❌ Wystąpił błąd przy wysyłaniu propozycji.")
        print(e)
@bot.command()
async def robloxuser(ctx, username: str):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            # 1. Pobranie ID
            async with session.get(f"https://api.roblox.com/users/get-by-username?username={username}") as resp:
                if resp.status != 200:
                    await ctx.send("❌ Błąd podczas łączenia z Roblox API.")
                    return
                data = await resp.json()
                if "Id" not in data:
                    await ctx.send("❌ Nie znaleziono takiego użytkownika.")
                    return
                user_id = data["Id"]

            # 2. Pobranie profilu
            async with session.get(f"https://users.roblox.com/v1/users/{user_id}") as resp:
                profile = await resp.json()

            # 3. Status online
            async with session.post("https://presence.roblox.com/v1/presence/users", json={"userIds": [user_id]}) as resp:
                presence = await resp.json()
                presence_data = presence["userPresences"][0]
                status = presence_data["userPresenceType"]
                place = presence_data.get("lastLocation", "Brak danych")

                if status == 0:
                    online_status = "🔴 Offline"
                elif status == 1:
                    online_status = "🟢 Online"
                elif status == 2:
                    online_status = f"🎮 W grze: {place}"
                else:
                    online_status = "❓ Nieznany status"

            # 4. Liczba znajomych
            async with session.get(f"https://friends.roblox.com/v1/users/{user_id}/friends/count") as resp:
                friends = await resp.json()
                friend_count = friends.get("count", "Nieznana")

            # 5. Avatar
            avatar_url = f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png"

            # 6. Historia nazw
            async with session.get(f"https://users.roblox.com/v1/users/{user_id}/username-history?limit=5&sortOrder=Desc") as resp:
                history_data = await resp.json()
                if history_data.get("data"):
                    names = [entry["name"] for entry in history_data["data"]]
                    name_history = ", ".join(names)
                else:
                    name_history = "Brak"

            # 7. Grupy (maks 3)
            async with session.get(f"https://groups.roblox.com/v2/users/{user_id}/groups/roles") as resp:
                group_data = await resp.json()
                if group_data.get("data"):
                    groups_info = []
                    for group in group_data["data"][:3]:
                        g_name = group["group"]["name"]
                        g_role = group["role"]["name"]
                        groups_info.append(f"{g_name} ({g_role})")
                    group_info = "\n".join(groups_info)
                else:
                    group_info = "Brak"

            # 8. Liczba stworzonych gier
            async with session.get(f"https://games.roblox.com/v2/users/{user_id}/games?accessFilter=All&sortOrder=Asc&limit=50") as resp:
                games_data = await resp.json()
                game_count = len(games_data.get("data", []))

            # 9. Link do profilu
            profile_url = f"https://www.roblox.com/users/{user_id}/profile"

            # === EMBED ===
            embed = discord.Embed(
                title=f"👤 Roblox: {profile['name']}",
                description=profile.get("description", "*Brak opisu*"),
                color=discord.Color.blurple()
            )
            embed.set_thumbnail(url=avatar_url)
            embed.add_field(name="🆔 ID", value=user_id, inline=True)
            embed.add_field(name="📶 Status", value=online_status, inline=True)
            embed.add_field(name="👥 Znajomi", value=friend_count, inline=True)
            embed.add_field(name="📅 Konto utworzone", value=profile['created'][:10], inline=True)
            embed.add_field(name="🔁 Historia nazw", value=name_history, inline=False)
            embed.add_field(name="🏷️ Grupy", value=group_info, inline=False)
            embed.add_field(name="🎮 Gry stworzone", value=str(game_count), inline=True)
            embed.add_field(name="🔗 Profil", value=f"[Kliknij tutaj]({profile_url})", inline=False)
            embed.set_footer(text="Dane pobrane z Roblox API")

            # === BUTTON ===
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Odwiedź profil Roblox", url=profile_url))

            await ctx.send(embed=embed, view=view)

    except aiohttp.ClientConnectorError:
        await ctx.send("🚫 Nie udało się połączyć z API Roblox. Sprawdź połączenie z Internetem lub DNS.")
    except asyncio.TimeoutError:
        await ctx.send("⏱️ Czas oczekiwania na odpowiedź z Roblox API minął.")
    except Exception as e:
        await ctx.send(f"⚠️ Wystąpił nieznany błąd: `{e}`")
@bot.command()
async def rax(ctx):
    await ctx.send("https://cdn.discordapp.com/attachments/1367809844152897578/1372563218832035840/ezgif.com-animated-gif-maker_2.gif?ex=68273a9c&is=6825e91c&hm=5e9761d87d1d365586236b7e69a250a2dea9b95b367c8c105c2caf0f46a8f7de&")
@bot.command()
async def gry(ctx):
    url = "https://www.gamerpower.com/api/giveaways"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()

                if not data:
                    await ctx.send("😕 Obecnie brak dostępnych darmowych gier.")
                    return

                embed = discord.Embed(
                    title="🆓 Darmowe gry z różnych platform",
                    description="Oto aktualne promocje z gier, które są **całkowicie za darmo!**",
                    color=discord.Color.green()
                )

                for gra in data[:20]:  # pokazujemy tylko 5 gier
                    tytul = gra['title']
                    platformy = gra['platforms']
                    link = gra['open_giveaway_url']
                    koniec = gra.get('end_date', 'Nieznany')

                    embed.add_field(
                        name=f"🎮 {tytul}",
                        value=f"🖥️ **Platformy**: {platformy}\n📅 **Koniec**: {koniec}\n🔗 [Kliknij tutaj]({link})",
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("⚠️ Nie udało się pobrać listy gier. Spróbuj ponownie później.")
# Salda graczy (tymczasowo w pamięci)
kontrola_salda = {}

slot_emoji = ["🍒", "🍋", "🍇", "💎", "🔔", "7️⃣", "🍀"]

# Funkcja losowania slotów
def zakrec_slotami():
    wynik = [random.choice(slot_emoji) for _ in range(3)]
    if wynik.count(wynik[0]) == 3:
        rezultat = ("🎉 **JACKPOT! Wszystkie 3 takie same!**", 100, discord.Color.gold())
    elif wynik.count(wynik[0]) == 2 or wynik.count(wynik[1]) == 2:
        rezultat = ("✨ **Dwie takie same! Wygrywasz 20 zł!**", 20, discord.Color.purple())
    else:
        rezultat = ("💀 **Pech! Tracisz 10 zł.**", -10, discord.Color.red())
    return wynik, *rezultat

# Komenda kasyno
@bot.command()
async def kasyno(ctx):
    user_id = ctx.author.id
    if user_id not in kontrola_salda:
        kontrola_salda[user_id] = 100  # startowe saldo

    saldo = kontrola_salda[user_id]

    if saldo < 10:
        await ctx.send(f"💸 {ctx.author.mention}, masz za mało pieniędzy (masz tylko {saldo} zł).")
        return

    wynik, opis, wygrana, kolor = zakrec_slotami()
    saldo += wygrana
    kontrola_salda[user_id] = saldo

    wynik_text = " | ".join(wynik)

    embed = discord.Embed(
        title="🎰 Kasyno 3000™",
        description=f"{ctx.author.mention} zakręcił slotami...\n\n🎲 | {wynik_text} | 🎲\n\n{opis}\n\n💰 **Saldo:** {saldo} zł",
        color=kolor
    )
    embed.set_footer(text="Zakład kosztuje 10 zł.")
    embed.set_thumbnail(url="https://i.imgur.com/o6xU1Md.png")

    # Przycisk do ponownej gry
    button = Button(label="Zagraj ponownie 🎰", style=discord.ButtonStyle.success)

    async def button_callback(interaction):
        if interaction.user.id != ctx.author.id:
            await interaction.response.send_message("To nie Twój zakład!", ephemeral=True)
            return
        await kasyno(ctx)

    button.callback = button_callback
    view = View()
    view.add_item(button)

    await ctx.send(embed=embed, view=view)
class TicTacToeButton(Button):
    def __init__(self, x, y):
        super().__init__(label="⬜", style=discord.ButtonStyle.secondary, row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeView = self.view

        if interaction.user != view.current_player:
            await interaction.response.send_message("Nie twoja tura!", ephemeral=True)
            return

        if view.board[self.y][self.x] != 0:
            await interaction.response.send_message("To pole jest już zajęte!", ephemeral=True)
            return

        symbol = "❌" if view.current_player == view.player1 else "⭕"
        self.label = symbol
        self.style = discord.ButtonStyle.danger if symbol == "❌" else discord.ButtonStyle.success
        self.disabled = True
        view.board[self.y][self.x] = symbol
        await interaction.response.edit_message(view=view)

        winner = view.check_winner()
        if winner:
            for child in view.children:
                child.disabled = True
            await interaction.followup.send(f"🎉 {interaction.user.mention} wygrał!", ephemeral=False)
        elif view.is_draw():
            for child in view.children:
                child.disabled = True
            await interaction.followup.send("🤝 Remis!", ephemeral=False)
        else:
            view.switch_player()

class TicTacToeView(View):
    def __init__(self, player1, player2):
        super().__init__(timeout=None)
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.board = [[0 for _ in range(3)] for _ in range(3)]

        for y in range(3):
            for x in range(3):
                self.add_item(TicTacToeButton(x, y))

    def switch_player(self):
        self.current_player = self.player2 if self.current_player == self.player1 else self.player1

    def check_winner(self):
        lines = []

        # Wiersze i kolumny
        lines.extend(self.board)
        lines.extend([[self.board[y][x] for y in range(3)] for x in range(3)])
        # Przekątne
        lines.append([self.board[i][i] for i in range(3)])
        lines.append([self.board[i][2 - i] for i in range(3)])

        for line in lines:
            if line[0] != 0 and all(cell == line[0] for cell in line):
                return line[0]
        return None

    def is_draw(self):
        return all(cell != 0 for row in self.board for cell in row)

@bot.command(name="xo")
async def start_xo(ctx, opponent: discord.Member):
    if opponent.bot or opponent == ctx.author:
        await ctx.send("Wybierz innego gracza (nie bota i nie siebie).")
        return

    view = TicTacToeView(ctx.author, opponent)

    embed = discord.Embed(
        title="🎮 Kółko i Krzyżyk",
        description=f"{ctx.author.mention} vs {opponent.mention}\n❌ zaczyna!",
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed, view=view)
@bot.command()
async def krakow(ctx):
    await ctx.send("https://media.discordapp.net/attachments/673619715582590976/1182797256282357760/caption-1.gif?ex=68270689&is=6825b509&hm=4a28b130596c8f6c96ec7324090b0cc3b88a0853661037d07f8be9c1a73ce627&")
@bot.command()
async def rzeczy(ctx):
    embed = discord.Embed(
        title="Ekwipunek Cedek'a",
        description="Tu znajdziesz wszsytkie rzeczy cedek'a",
        color=discord.Color.red()
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed.add_field(name="Moje laptopy", value="[Main](https://www.euro.com.pl/laptopy-i-netbooki/sony-vaio-sve1512h1ew-w8-bialy.bhtml?msockid=1fccc038b3cc69ea3b15d5edb2ed6855), [Drugi do testów](https://komputerymarkowe.pl/laptopy-poleasingowe/2033-dell-vostro-3550-core-i3-21ghz-2310m.html)", inline=True)
    embed.add_field(name="Moje specyfikacje laptopa main ", value="Procesor    Intel(R) Core(TM) i3-3110M CPU @ 2.40GHz   2.40 GHz   Zainstalowana pamięć RAM    6,00 GB   Pamięć    112 GB SSD GIGABYTE GP-GSTFS31120GNTD   Karta graficzna    AMD Radeon HD 7500M/7600M Series (1006 MB)   Typ systemu    64-bitowy system operacyjny, procesor x64   Pióro i urządzenia dotykowe    Brak obsługi pióra i wprowadzania dotykowego dla tego ekranu", inline=True)
    embed.add_field(name="Klawiatura", value="[Klawiatura](https://maddog.pl/produkty/klawiatury/5,mad-dog-gk700-rgb)", inline=True)
    embed.add_field(name="Myszka", value="[Myszka](https://www.action.com/pl-pl/p/3203556/myszka-do-gier-battletron/)", inline=True)
    embed.add_field(name="Telefony", value="[Motorola Moto G24 Main](https://www.mediaexpert.pl/smartfony-i-zegarki/smartfony/smartfon-motorola-moto-g24-8-128gb-6-56-90hz-grafitowy?msockid=1fccc038b3cc69ea3b15d5edb2ed6855) , [Samsung Galaxy A50](https://www.mgsm.pl/pl/katalog/samsung/galaxya50dualsim/)", inline=True)
    embed.set_footer(text="Rzeczy cedek'a")
    await ctx.send(embed=embed)

@bot.tree.command(name="mp3", description="Pobierz audio z YouTube jako mp3 (192 kbps)")
@app_commands.describe(url="Link do filmu YouTube")
async def mp3(interaction: discord.Interaction, url: str):
    await interaction.response.defer()  # pokaż, że bot pracuje

    ydl_opts = {
    'ffmpeg_location': r'C:\ffmpeg\bin\ffmpeg.exe',
    'format': 'bestaudio/best',
    'outtmpl': 'downloaded.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,  # <<< tu
}


    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename = os.path.splitext(filename)[0] + ".mp3"

        filesize = os.path.getsize(filename)
        max_size = 8 * 1024 * 1024  # 8 MB limit
        if filesize > max_size:
            await interaction.followup.send("❌ Plik jest za duży (>8MB), spróbuj krótszy film lub niższą jakość.")
            os.remove(filename)
            return

        await interaction.followup.send(file=discord.File(filename))
        os.remove(filename)

    except Exception as e:
        await interaction.followup.send(f"❌ Wystąpił błąd: {e}")

# Losowe słowa do wyszukiwania
keywords = [
    "music", "remix", "song", "trap", "2024", "vibes", "pop", "jazz", "rap", "metal", "indie", "funk", "lofi"
]

@bot.tree.command(name="losuj", description="Losuje losową piosenkę z YouTube.")
async def losuj(interaction: discord.Interaction):
    await interaction.response.defer()

    # Losujemy słowo kluczowe
    query = random.choice(keywords)
    search_query = f"ytsearch10:{query}"

    # Konfiguracja yt-dlp
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': 'bestaudio',
        'default_search': 'ytsearch',
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            entries = info.get('entries', [])
            if not entries:
                await interaction.followup.send("❌ Nie znaleziono żadnych wyników.")
                return

            los = random.choice(entries)
            title = los.get('title')
            url = los.get('webpage_url')

            embed = discord.Embed(
                title="🎵 Wylosowano utwór!",
                description=f"[{title}]({url})",
                color=discord.Color.random()
            )
            await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ Wystąpił błąd: `{e}`")
GUILD_ID = 1366790958296993802  # Wstaw ID swojego serwera testowego (w Discordzie kliknij na serwer prawym i "Kopiuj ID")
# Uruchomienie bota
TOKEN = "MTM3MDc2NjUyNDE1OTEwMzA3OQ.G-KbQG.Nu8RkddEfPVaaGLr3UkI0dRwsbq_DcIjx6ta94"
bot.run(TOKEN)
