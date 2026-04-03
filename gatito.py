# gatito.py
import os
import discord
from discord.ext import tasks
import datetime
from dotenv import load_dotenv

from modules import parser
from modules import scheduling

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CAMINHA_ID')

ajuda_txt = '''
Boas! Bem-vindo à ajuda do gatito - bot do discord!
1. Na dúvida, pede uma !ajuda
2. Para já podes fazer uma !nota e dizer quando queres ser lembrado\n
\t2.1.  Instruções: "!nota \"[mensagem com espaços]\" [dia da semana]"\n
\t2.2.  Exemplo: "!nota \"ir à cerâmica\" sábado"\n
\t2.3.  Exemplo: "Bro faz aí uma !nota \"cortar o cabelo\" 6a"
3. Podes listar os eventos todos com !lista
4. Podes apagar os eventos com !cancelar [número do evento]
\t4.1   Podes ainda !cancelar tudo - cuidado!
5. Streaks tipo duolingo:
\t5.1   Podes começar uma streak diária com o comando !streak <a-tua-cena>
\t5.2   Podes ver o teu progress usando o comando !progresso
\t5.3   As streaks caducam à meia-noite UTC
'''

def log(message):
    now = datetime.datetime.now()
    iso_now = now.strftime('%Y-%m-%d %H:%M:%S')
    print("{} RUNTIME  {}".format(iso_now,message))
    log_filename = "gatito.log"
    if not os.path.exists(log_filename):
        with open(log_filename, 'w') as file:
            file.write('')
    with open(log_filename, 'a') as file:
        file.write("{} RUNTIME  {}\n".format(iso_now,message))

class Client(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
            self.morning_routine.start()
            self.evening_routine.start()
            self.streak_routine.start()

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        if "!ajuda" in message.content:
            log("!ajuda command received")
            await message.channel.send(ajuda_txt)
            log("!ajuda command sent")

        if "!nota" in message.content:
            log("!nota command received")
            feedback_str = parser.parse_nota(message.content)
            await message.channel.send(feedback_str)
            log("Reply: "+feedback_str)

        if "!lista" in message.content:
            log("!lista command received")
            feedback_str = parser.list_notas()
            await message.channel.send(feedback_str)
            log("Reply: "+feedback_str)

        if message.content.startswith("!cancelar"):
            log("!cancelar command received")
            feedback_str = parser.erase_nota(message.content)
            await message.channel.send(feedback_str)
            log("Reply: "+feedback_str)

        if message.content.startswith("!streak"):
            log("!streak command received")
            feedback_str = parser.update_streak(message.content)
            if len(feedback_str):
                await message.channel.send(feedback_str)
            log("Reply: "+feedback_str)

        if "!progresso" in message.content:
            log("!progresso command received")
            feedback_str = parser.load_list_streaks()
            await message.channel.send(feedback_str)
            log("Reply: "+feedback_str)

        if message.content.startswith("!reboot"):
            log("!reboot command received")
            exit(0)

    @tasks.loop(time=datetime.time(hour=7, minute=30))
    async def morning_routine(self):
        message = scheduling.get_morning_message()
        channel = self.get_channel(int(CHANNEL_ID))
        await channel.send(message)
        log("Morning message sent")
        pass

    @tasks.loop(time=datetime.time(hour=21, minute=30))
    async def evening_routine(self):
        message = scheduling.get_night_message()
        if message != None:
            channel = self.get_channel(int(CHANNEL_ID))
            await channel.send(message)
        log("Night message sent")

    @tasks.loop(time=datetime.time(hour=23, minute=50))
    async def streak_routine(self):
        log("Testing streaks...")
        message = scheduling.test_streaks_message()
        if message != None:
            channel = self.get_channel(int(CHANNEL_ID))
            await channel.send(message)

        log("Starting cleanup...")
        erase_log = scheduling.cleanup_events()
        log(erase_log)

    @morning_routine.before_loop
    @evening_routine.before_loop
    @streak_routine.before_loop

    async def before_tasks(self):
        await self.wait_until_ready()

intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run(TOKEN)