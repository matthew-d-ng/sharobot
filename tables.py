import pickle
from threading import Lock

subs_mutex = Lock()
channels_mutex = Lock()

def init_data(file):

    try:
        dict_file = open(file, "rb")
    except FileNotFoundError:
        dict_file = open(file, "bw+")

    try:
        dict_mem = pickle.load(dict_file)
    except EOFError:
        dict_mem = dict()

    dict_file.close()
    return dict_mem


def update_channel_data(server, channel):

    channels_mutex.acquire()
    channels[server.id] = channel.id
    channels_file = open("channels.pickle","wb")
    pickle.dump(channels, channels_file)
    channels_file.close()
    channels_mutex.release()


def subscribe(server, pixiv_id):

    subs_mutex.acquire()
    if not pixiv_id in subscriptions:
        subscriptions[pixiv_id] = list()

    subscriptions[pixiv_id].append(server.id)
    subs_file = open("subscriptions.pickle","wb")
    pickle.dump(subscriptions, subs_file)
    subs_file.close()
    # init_user_cache(pixiv_id)
    subs_mutex.release()


def unsubscribe(server, pixiv_id):

    subs_mutex.acquire()
    success = False
    if pixiv_id in subscriptions and server.id in subscriptions[pixiv_id]:
        subscriptions[pixiv_id].remove(server.id)
        subs_file = open("subscriptions.pickle","wb")
        pickle.dump(subscriptions, subs_file)
        subs_file.close()
        success = True

    subs_mutex.release()
    return success


channels = init_data("channels.pickle")
subscriptions = init_data("subscriptions.pickle")
