import asyncio
import time
import os
from pixivpy3 import *
import pixiv_config
import discord
from art import Art
from tables import subscriptions
from tables import channels
from tables import subs_mutex
from tables import channels_mutex
from backoff_timer import Backoff_Timer

illust_url = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id="

user_cache = dict()
api = AppPixivAPI()
api.login(pixiv_config.user, pixiv_config.password)


def valid_pixiv_id(pixiv_id):
    return not "error" in api.user_detail(pixiv_id)


def init_user_cache(user_id):

    json_result = api.user_bookmarks_illust(user_id)
    # print(json_result)
    bookmarks = json_result.illusts
    user_cache[user_id] = list()
    
    for illust in bookmarks:
        user_cache[user_id].append(illust.id)


def set_rating(tags):

    if not "R-18" in tags and not "R-18G" in tags:
        return "SAFE"
    elif not "R-18G" in tags:
        return "R-18"
    return "R-18G"


def get_user_bookmarks(user_id):

    illust_list = list()
    json_result = api.user_bookmarks_illust(user_id)
    # print(json_result.next_url)
    # next_qs = api.parse_qs(json_result.next_url)
    # print(next_qs)
    
    # newBookmarks = True
    # while newBookmarks:
    if not "illusts" in json_result:   
        api.login(pixiv_config.user, pixiv_config.password)
        json_result = api.user_bookmarks_illust(user_id)

    bookmarks = json_result.illusts

    for illust in bookmarks:

        if illust.id in user_cache[user_id]:
            #newBookmarks = False
            break

        print("new art")
        rating = set_rating(illust.tags)

        if len(illust.meta_single_page) > 0:
            album = False
            picture = illust.meta_single_page.original_image_url
        else:
            album = True
            picture = illust.meta_pages[0].image_urls.original
        
        # print(illust)
        art = Art(illust.id, illust.title, rating, illust.type, album, picture, illust.user.name)
        illust_list.append(art)
        user_cache[user_id].pop()
        user_cache[user_id] = [illust.id] + user_cache[user_id]

        # next_qs = api.parse_qs(json_result.next_url)
        # print(next_qs)
        # json_result = api.illust_related(**next_qs)
        # illust = json_result.illust.meta_single_page.original_image_url
        # api.download(illust)

    return illust_list


def post_user_bookmarks(client, user, bookmarks):
    
    channels_mutex.acquire()
    username = api.user_detail(user).user.name
    while len(bookmarks) != 0:
        illust = bookmarks.pop()
        if illust.rating == "SAFE":
            post = username + " bookmarked a work by " + illust.artist +":\n" +\
                        illust.title + "\n<" + illust_url + str(illust.id) + ">\n"
            if illust.album:
                post = post + "***ALBUM** - MULTIPLE IMAGES THROUGH LINK*"
            if illust.illust_type == "ugoira":
                post = post + "***UGOIRA** - Animation visible through link"
            api.download(illust.original_image)
            path = os.path.basename(illust.original_image)
            for server in subscriptions[user]:
                    channel = client.get_channel(channels[server])
                    fut = asyncio.run_coroutine_threadsafe(client.send_file(channel, path, content=post), client.loop)
                    fut.result()
            os.remove(path)

    channels_mutex.release()


def monitor_bookmarks(client):

    timer = Backoff_Timer()

    print("Starting monitor")
    subs_mutex.acquire()
    for user in subscriptions:
        init_user_cache(user)
    subs_mutex.release()

    while True:
        print("sleeping...")
        time.sleep( timer.get_wait_time() )
        print("woken up!...")
        subs_mutex.acquire()
        for user in subscriptions:
            if len(subscriptions[user]) > 0:
                latest_bookmarks = get_user_bookmarks(user)
                if len(latest_bookmarks) > 0:
                    timer.reset_time()
                    post_user_bookmarks(client, user, latest_bookmarks)
        subs_mutex.release()
