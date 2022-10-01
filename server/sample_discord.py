
# This example requires the 'message_content' intent.

import discord


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')


my_intents = discord.Intents.default()
my_intents.message_content = True

client = MyClient(intents=my_intents)
client.run('my token goes here')
