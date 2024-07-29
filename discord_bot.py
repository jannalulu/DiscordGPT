import discord
import openai
import os
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
from keep_alive import keep_alive

load_dotenv() # loads environment variables
openai.api_key=os.getenv("OPENAI_API_KEY")

# Define intents
intents = discord.Intents.default()  # This sets up the intents your bot will use.
intents.messages = True  # If you want the bot to read messages
intents.message_content = True # enable message content intent

chatgpt_behaviour = os.getenv("BEHAVIOUR") #Retrieve behavior settings

# Start webserver
keep_alive()

# Initialize the Discord client
bot = commands.Bot(command_prefix='!', intents=intents)

# This is an event listener for when the bot has switched from offline to online.
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# This event listener checks for new messages from users in the servers.
@bot.command(name='ask')
async def ask(ctx, *, question: str=None):
    if question is None:  # If no question was provided
        await ctx.send("Please provide a question.")
        return
    try:
        # Create a list of past interactions; for a simple scenario, it can just be the current question
        messages = [
            {"role": "user", "content": question}
        ]

        # Call the GPT API with the question
        response = openai.chat.completions.create(
          model="gpt-4o",
          messages=messages,
          temperature=0.2,
          max_tokens=4096
        )
        message_content = response.choices[0].message.content if response.choices else "I'm unable to answer that question."

        # Check if the message is too long for one Discord message
        if message_content and len(message_content) > 2048:
            # Break the message into chunks that are less than 2048 characters
            message_chunks = [message_content[i:i + 2048] for i in range(0, len(message_content), 2048)]
            
            for chunk in message_chunks:
                # Send the chunks one by one
                await ctx.send(chunk)
                await asyncio.sleep(1)  # Small delay to prevent rate limiting
        else:
            # Send the message as normal if it's within the limit
            await ctx.send(message_content)

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

# Start the bot with the Discord token
try: 
    bot.run(os.getenv("DISCORD_TOKEN"))
except KeyboardInterrupt:
    print("Shutting down...")
    asyncio.run(bot.close())