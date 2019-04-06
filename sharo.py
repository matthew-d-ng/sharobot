#!/usr/bin/python3

import threading
import asyncio
import discord
import config
import tables
import pixiv_reader
import time
from random import randint
import todd
import os

client = discord.Client()

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

MASTER_1200 = [
              "Listen up retard, that's a compressed sample size image that you just posted, \
               don't do that. Here's the full size from pixiv.",

              "Ok so apparently your retarded self doesn't know how to save an image and you've posted a 'master1200' sample.\
               Here's the full image, don't do it again.",

              ">master1200\n Save the proper sizes from pixiv, here's the full size:",

              "I am actually going to murder you\n \
               non-sample version:",

              "ok retard stop saving sample size images, here is the proper version",

              "listen up liberal stop posting these compressed images and take a proper one, here is the full uncompressed version:",

              "fuck you, here is the full size",

              "what the heck is that? an image for ryners? save the full size or you will be cursed with dwarfism and shit taste"
              ]

SAMPLE =      [
              "Listen up retard, that's a compressed sample size image that you just posted, \
               don't do that.",

               "why are you actually unable to save an image from the internet properly",

               "listen up liberal stop posting these compressed images and go get the full size yourself",

               ">sample_",

               ">posting sample",

               "stop saving sample size aaaggggggggghhhhhhhhhhhhhhhh"
              ]

class Monitor(threading.Thread):

    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client
    
    def run(self):
        pixiv_reader.monitor_bookmarks(client)


def init_bot():
    # client.change_presence(game=discord.Game(name="in Rabbit House", type=0))
    t = Monitor(client)
    t.start()
    client.run(config.token)
    try:
        t.join()
    except KeyboardInterrupt:  
        client.logout()


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

    if len(message.attachments) > 0:
        for pic in message.attachments:
            if pic["filename"].endswith("_master1200.jpg"):

                if message.author != todd.ID:
                    post = MASTER_1200[randint(0, len(MASTER_1200)-1)]
                else:
                    post = todd.MASTER_1200.format("<@"+todd.ID+">")

                path = pixiv_reader.get_illust_from_filename(pic["filename"])
                if path:
                    await client.send_file(message.channel, path, content=post)
                    os.remove(path)

            elif pic["filename"].startswith("sample_") \
                 and (pic["filename"].endswith(".jpg") or pic["filename"].endswith(".png")):

                if message.author != todd.ID:
                    post = SAMPLE[randint(0, len(SAMPLE)-1)]
                    await client.send_message(message.channel, post)

    #elif message.content.startswith("&list channels"):
    #    await client.send_message(message.channel, str(tables.channels))

    #elif message.content.startswith("&list subs"):
    #    await client.send_message(message.channel, str(tables.subscriptions))

    #elif message.content.startswith("&exit"):
    #    await client.close()

init_bot()

# pixiv_reader.monitor_bookmarks(client)
# set_status()
