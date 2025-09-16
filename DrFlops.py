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
listener_command_args = ["!add", "!remove", "!caseSensitive", "!excludeWhenPresent", "!trigger:", "!response:", "!frequency:"]
command_list = ["!help", "!listener"]
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
            raise ValueError("Server not found: major issue")

    count = 0
    for arr in server:
        if count == 0:
            count += 1
            continue
        if arr_key == arr[0]:
            return_arr = arr
            break

    return return_arr

async def trigger_message(trigger, message, guild_id):
    parts = trigger.split(restricted_words[0])[0].split(",")
    response_index = parts[0]
    response_probability = parts[1]
    lottery = random.randint(1, int(response_probability))
    if int(lottery) == int(response_probability):
        response = lookup_arr(guild_id, "Responses")
        response_index = int(response_index)
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
                for line in trigger_file.readlines():
                    if line:
                        server_data_arr[server_count][parameter_count].append(line.strip())
            print(f'We have successfully read {arr} from {guild.name}')
            parameter_count+=1
        server_count+=1
    print(f'We have logged in as {client.user}')


# writes an updated array to a file
def write_arr(guild_id, target_file, target_arr):
    filename = f'config/{guild_id}.{target_file}'
    count = 0
    with open(filename, 'w') as write_file:
        for item in target_arr:
            if count == 0:
                count += 1
                continue
            line = str(item).strip()
            if line:
                write_file.write(line + "\n")

# The message sent when a listener command fails
async def listener_command_fail(message):
    await message.channel.send(f"Send Command in this format [either|or] (optional)  "
                               f"\n{command_list[1]} [{listener_command_args[0]} or {listener_command_args[1]}] "
                               f"({listener_command_args[2]} {listener_command_args[3]}:String, "
                               f"{listener_command_args[6]}:Integer) "
                               f"{listener_command_args[4]}String {listener_command_args[5]}String")

#processes an add command
async def listener_command_add(message, trigger, trigger_arr, response, response_arr, frequency):
    # separate exclusion filters into own array
    exclusion_arr = []
    if listener_command_args[3] in message.content:
        exclusion_arr = message.content
        for x in range(len(exclusion_arr)):
            if x != 3:
                exclusion_arr = exclusion_arr.replace(listener_command_args[x], "")
        exclusion_arr = exclusion_arr.replace(trigger, "").replace(response, "").split(listener_command_args[3])

    # if case is case-sensitive send trigger as is, else lowercase trigger
    if listener_command_args[2] in message.content:
        cs = ",cs"
    else:
        cs = ""
        trigger = str(trigger.lower())

    # checks if creating a duplicate response
    index = -1
    for x in range(1, len(response_arr)):
        if str(response).strip() in response_arr[x]:
            index = x
    if index == -1:
        response_arr.append(response)
        write_arr(message.guild.id, parameter_arr[0], response_arr)
        index = len(response_arr) - 1

    # format exclusion tag
    if len(exclusion_arr) > 0:
        exclusion_count = ","
    else:
        exclusion_count = ""
    for _ in exclusion_arr:
        exclusion_count += "&!"

    # build trigger string
    trigger_str = f"{index},{frequency}{cs}{exclusion_count}{restricted_words[0]}{trigger}"
    for exclusion in exclusion_arr:
        trigger_str += f",{exclusion}"

    # checks trigger already exists
    overwrite = False
    for x in range(1, len(trigger_arr)):
        # if trigger will overwrite any existing triggers, rewrite that trigger
        if str(trigger).strip().lower() in str(trigger_arr[x].split(restricted_words[0])[1]).strip().lower():
            trigger_arr[x] = trigger_str
            overwrite = True
    # if trigger doesn't exist, add to triggers
    if not overwrite:
        trigger_arr.append(trigger_str)

    # write new trigger list
    write_arr(message.guild.id, parameter_arr[1], trigger_arr)
    await message.channel.send(f"<@{message.author.id}> Your listener was successfully added to {message.guild.name}")


async def listener_command_remove(message, trigger, trigger_arr):
    print("###TODO## Remove function")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #Command interpreter, if Bot is mentioned in message
    for mention in message.mentions:
        if mention.id == client.user.id:
            if command_list[1] in message.content:

                # test global listener requirements
                if listener_command_args[4] not in message.content or listener_command_args[5] not in message.content:
                    await message.channel.send( f"<@{message.author.id}> {listener_command_args[4]} and {listener_command_args[5]} "
                                                f"tag required in {command_list[1]} command")
                    await listener_command_fail(message)
                    return

                # test global listener requirements
                if listener_command_args[0]  not in message.content and listener_command_args[1] not in message.content:
                    await message.channel.send( f"<@{message.author.id}> {listener_command_args[0]} or {listener_command_args[1]} "
                                                f"tag required in {command_list[1]} command")
                    await listener_command_fail(message)
                    return
                # test global listener requirements
                for restricted in restricted_words:
                    if restricted in message.content:
                        await message.channel.send(
                            f"<@{message.author.id}> Your message contains restricted words: {restricted}")
                        await listener_command_fail(message)
                        return

                # retrieve current response and trigger lists
                response_arr = lookup_arr(message.guild.id, parameter_arr[0])
                trigger_arr = lookup_arr(message.guild.id, parameter_arr[1])

                listener_command = message.content.replace(command_list[1], "")

                # separate trigger from command
                trigger = listener_command.split(listener_command_args[4])[1]
                # separate response from command
                response = listener_command.split(listener_command_args[5])[1]

                # separate frequency from command, define as always triggered if not defined
                if listener_command_args[6] in listener_command:
                    frequency = listener_command.split(listener_command_args[6])[1]
                else:
                    frequency = "1"

                # if frequency is not an integer fail listener command
                if not str(frequency).isdigit():
                    await message.channel.send(f"<@{message.author.id}> Your frequency must be an integer.")
                    await listener_command_fail(message)
                    return

                # for every command with a value attached, it removes any excess values if present
                for arg in listener_command_args:
                    if arg in trigger:
                        trigger = trigger.split(arg)[0]
                    if arg in response:
                        response = response.split(arg)[0]
                    if arg in frequency:
                        frequency = frequency.split(arg)[0]

                # if adding a trigger response pair
                if listener_command_args[0] in message.content:
                    await listener_command_add(message,trigger, trigger_arr, response, response_arr, frequency)
                else:
                    await listener_command_remove(message,trigger, trigger_arr)
                return

            # if Bot is tagged in something unexpected, give a statement
            statements = lookup_arr(message.guild.id, "Statements")
            statement_index = random.randint(0, len(statements) - 1)
            response = statements[statement_index]
            await message.channel.send(f"<@{message.author.id}> {response}")
            return

    triggers = lookup_arr(message.guild.id, parameter_arr[1])
    #search messages for triggers
    for trigger in triggers:
        #if label for triggers
        if parameter_arr[1] == str(trigger).strip(): continue

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


client.run(token)