#Author: Alice Puppy
#Version 1.0.1

from random import random
import discord, random
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)

file_path= "config/global.token_filepath"
with open(file_path, 'r') as file:
    token_path = file.read()

with open(token_path, 'r') as file:
    token = file.read()

parameter_arr = ["Responses", "Triggers", "Statements", "Parameters"]
restricted_words = [" !program.args! ", " !exclusion.filter! "]
trigger_filters = ["&!", "cs"]
server_data_arr = []

#Helper method, looks up array based on key for specific server
def lookup_arr(guild_id, arr_key):
    server = 0
    return_arr = []
    # Lookup triggers on server
    global server_data_arr
    for arr in server_data_arr:
        if guild_id in arr:
            server = arr
        else:
            print("Server not found: major issue")

    count = 0
    for arr in server:
        if count == 0:
            count += 1
            continue
        else:
            count += 1
        if arr_key == arr[0]:
            return_arr = arr[1]
            break
    if return_arr == []:
        print("Array not found: major issue")
    return return_arr

async def trigger_message(trigger, message, guild_id):
    parts = trigger.split(restricted_words[0])[0].split(",")
    response_index = parts[0]
    response_probability = parts[1]
    lottery = random.randint(1, int(response_probability))
    if int(lottery) == int(response_probability):
        response = lookup_arr(guild_id, "Responses")
        response_index = int(response_index) - 1
        response = response[response_index]
        await message.channel.send(f"<@{message.author.id}> {response}")

@client.event
async def on_ready():
    global server_data_arr
    server_count = 0
    for guild in client.guilds:
        server_data_arr.append([guild.id])
        parameter_count = 1
        for arr in parameter_arr:
            server_data_arr[server_count].append([arr])
            filepath = f'config/{guild.id}.{arr}'
            with open(filepath, 'r') as trigger_file:
                server_data_arr[server_count][parameter_count].append(trigger_file.readlines())
            print(f'We have successfully read {arr} from {guild.name}')
            parameter_count+=1
        server_count+=1
    print(f'We have logged in as {client.user}')


#Look for
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    triggers = lookup_arr(message.guild.id, "Triggers")
    #search messages for triggers
    for trigger in triggers:
        #Set search string if case-sensitive or not
        if trigger_filters[1] in trigger.split(restricted_words[0])[0]:
            search_str = message.content
        else:
            search_str = message.content.lower()

        #If the trigger phrase is in the message, trigger a response based on trigger parameters
        parts = trigger.split(restricted_words[0])
        if restricted_words[1] in parts[1]:
            search_trigger = str(parts[1].split(restricted_words[1])[0]).strip()
        else:
            search_trigger = str(parts[1]).strip()

        if search_trigger in search_str:
            # Search for `and not tag`
            if trigger_filters[0] in parts[0]:
                correct = False
                additional_params = parts[1].split(restricted_words[1])
                for x in range(1, parts[0].count(trigger_filters[0])+1):
                    if str(additional_params[x]).strip() in str(search_str):
                        correct = True
                        break
                if not correct:
                    await trigger_message(trigger, message, message.guild.id)
                    return
            #trigger if trigger in message and no exclusion clauses
            else:
                await trigger_message(trigger, message, message.guild.id)
                return

    #Command interpreter, if Bot is mentioned in message
    for mention in message.mentions:
        if mention.id == client.user.id:
            #if Bot is tagged in something unexpected, give a statement
            statements = lookup_arr(message.guild.id, "Statements")
            statement_index = random.randint(0, len(statements) - 1)
            response = statements[statement_index]
            await message.channel.send(f"<@{message.author.id}> {response}")
            return

client.run(token)