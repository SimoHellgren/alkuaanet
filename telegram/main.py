import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
from .service import SongsAPI
from .config import token, apiurl

api = SongsAPI(apiurl)
bot = telepot.Bot(token)

def basic_keyboard(data, kind):
    buttons = [[InlineKeyboardButton(text=d['name'], callback_data=f"{kind}_{d['id']}")] for d in data]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def composer_keyboard(composers):
    buttons = [[InlineKeyboardButton(text=f"{c['lastname']}, {c['firstname']}", callback_data=f"composer_{c['id']}")] for c in composers]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def on_chat(message):
    chat_id = message['chat']['id']
    text = message['text'].strip()

    command, _, args = text.partition(' ')

    if text.startswith('/collections'):
        if args:
            collections = api.search_collections(args)
        else:
            collections = api.get_collections()
        
        kb = basic_keyboard(collections, 'collection')
        bot.sendMessage(chat_id, 'Collections', reply_markup=kb)

    elif text.startswith('/composers'):
        if args:
            composers = api.search_composers(args)
        else:
            composers = api.get_composers()

        kb = composer_keyboard(
            sorted(composers, key=lambda x: (x['lastname'], x['firstname'] or ''))
        )

        bot.sendMessage(chat_id, 'Composers', reply_markup=kb)

    else:
        songs = sorted(api.search_songs(text), key=lambda x: x['name'])
        
        if songs:
            kb = basic_keyboard(songs, 'song')
            bot.sendMessage(chat_id, f'Results for {text}', reply_markup=kb)
        else:
            bot.sendMessage(chat_id, f'No results for {text}')

def song_to_message(song):
    return '\n'.join(f'{k}: {v}' for k,v in song.items() if k not in ('id', ))

def on_callback(message):
    query_id, chat_id, callback = telepot.glance(message, flavor='callback_query')

    kind, rid = callback.split('_')

    if kind == 'song':
        song = api.get_song(rid)
        opus = api.get_song_opus(rid)
        bot.sendMessage(chat_id, song_to_message(song))
        bot.sendVoice(chat_id, opus)

    elif kind == 'collection':
        songs = sorted(api.get_collection_songs(rid), key=lambda x: x['name'])
        
        if songs:
            kb = basic_keyboard(songs, 'song')
            bot.sendMessage(chat_id, f'Songs in collection:', reply_markup=kb)
        else:
            bot.sendMessage(chat_id, f'No songs in collection')

    elif kind == 'composer':
        songs = sorted(api.get_composer_songs(rid), key=lambda x: x['name'])

        if songs:
            kb = basic_keyboard(songs, 'song')
            bot.sendMessage(chat_id, f'Songs by composer:', reply_markup=kb)
        else:
            bot.sendMessage(chat_id, f'No songs by composer')

message_loop = MessageLoop(
        bot,
        {'chat': on_chat, 'callback_query': on_callback}
    )
