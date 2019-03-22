import threading
import asyncio
import discord
import config
import tables
import pixiv_reader

client = discord.Client()

ANDREW_ID = "302262516744978434"
MADS_ID = "322457949685415936"

# TODO:
#               FORMATTED POST + multiple images per post + ugoira(?)

HELP_MESSAGE = ("Hello, I'm currently in a prototype stage, report any bugs or suggestions to Avon(Alpacafe#7021)\n"
                            "Coming soon: Nicer looking posts, filtering R-18 to a different channel and subscribing to artist's works\n"
                            "Current R-18 policy: Will not post at all\n"
                            "I can't do anything about pixiv users labelling lewd things as 'All Ages', sorry\n\n"
                            "**Usage:**\n"
                            "    - **&subscribe** *user_id*: where *user_id* is a pixiv id\n"
                            "        Monitors the bookmarks of the pixiv user, if the user exists, and posts them to the pixiv channel\n\n"
                            "    - **&unsubscribe** *user_id*:\n"
                            "        Removes the given pixiv id from the subcription list, if it is there\n\n"
                            "    - **&set channel**:\n"
                            "        Sets the current channel for pixiv posts to be placed. Only one allowed per server. Setting a new channel will overwrite the old one.")

class Monitor(threading.Thread):

    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client
    
    def run(self):
        pixiv_reader.monitor_bookmarks(client)


def init_bot():
    client.change_presence(game=discord.Game(name="in Rabbit House", type=0))
    t = Monitor(client)
    t.start()
    client.run(config.token)
    try:
        t.join()
    except KeyboardInterrupt:  
        client.logout()
    

def is_andrew(m):
    return m.author.id == ANDREW_ID

def is_mads(m):
    print("checking message...")
    return m.author.id == MADS_ID



@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("&cawfee"):
        print("Received: ", message.content)
        print(message.channel)
        await client.send_message(message.channel, "Can I go home?")

    elif message.content.startswith("&purgeme") and message.author.id == ANDREW_ID:
        for channel in message.server.channels:
            await client.purge_from(channel, check=is_andrew)

    elif message.content.startswith("&purgetest"):
        print("purging ", message.channel)
        
        async for record in client.logs_from(message.channel, limit=None):
            if record.author.id == MADS_ID:
                await client.delete_message(record)

    elif isinstance(message.author, discord.Member) \
                            and message.author.server_permissions.manage_server:

        if message.content.startswith("&subscribe "):
            pixiv_id = message.content[11:]
            if pixiv_reader.valid_pixiv_id(pixiv_id):
                tables.subscribe(message.server, pixiv_id)
                pixiv_reader.init_user_cache(pixiv_id)
                await client.send_message(message.channel, "Subscribed to " + pixiv_id)

        elif message.content.startswith("&unsubscribe "):
            pixiv_id = message.content[13:]
            if tables.unsubscribe(message.server, pixiv_id):
                await client.send_message(message.channel, "Unsubscribed from " + pixiv_id)
            else:
                await client.send_message(message.channel, "It doesn't seem you were subscribed to that")

        elif message.content.startswith("&set channel"):
            tables.update_channel_data(message.server, message.channel)
            await client.send_message(message.channel, "Channel set as pixiv dump")

        elif message.content.startswith("&help"):
            await client.send_message(message.author, HELP_MESSAGE)

    #elif message.content.startswith("&list channels"):
    #    await client.send_message(message.channel, str(tables.channels))

    #elif message.content.startswith("&list subs"):
    #    await client.send_message(message.channel, str(tables.subscriptions))

    #elif message.content.startswith("&exit"):
    #    await client.close()

init_bot()

# pixiv_reader.monitor_bookmarks(client)
# set_status()
