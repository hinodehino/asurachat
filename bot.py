# -*- coding: utf-8 -*-
DEBUG = True
import json, requests, vk_api, urllib3, traceback, pymorphy2
from hidden import *
from datetime import datetime
from random import randint, choice, shuffle
from threading import Thread
from youtube_search import YoutubeSearch
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
 



def log(error):
    bot = Bot(dev, dev, None, None)
    bot.echo(traceback.format_exc(), keyboard=keyboard([('sleep', 'positive')]))


def admin(id_, cmd, argl, args):
    if id_ in admins:
        bot = Bot(dev, dev, None, None)
        if cmd == 'exec':
           bot.echo(eval(argl))
        elif cmd == 'test':
            bot.echo('tested')
        elif cmd == 'echo':
            eval('bot.echo(' + argl + ')')
        elif cmd == 'newkey':
            if len(args) > 3:
                base = openjson(args[0] + '.json')
                if args[1] == 'foreach':
                    for k in base.keys():
                        base[k][args[2]] = args[3] if not args[3].isnumeric() else int(args[3])
                elif args[1] == 'global':
                    base[args[2]] = args[3] if not args[3].isnumeric() else int(args[3])
                rewritejson(args[0] + '.json', base)
                bot.echo('succesful')
        elif cmd == 'rnkey':
            if len(args) >= 4:
                base = openjson(args[0] + '.json')
                if args[1] == 'foreach':
                    for k in base.keys():
                        val = base[k][args[2]]
                        del base[k][args[2]]
                        base[k][args[3]] = val
                elif args[1] == 'global':
                    val = base[args[2]]
                    del base[args[2]]
                    base[args[3]] = val
                rewritejson(args[0] + '.json', base)
                bot.echo('succesful')


def sleep(msg, frm):
    if msg == 'sleep' and frm in admins:
        bot = Bot(dev, dev, None, None)
        bot.echo('💤')
        exit()


def openjson(f):
    return json.loads(open(f, encoding='utf-8').read())


def rewritejson(f, d):
    open(f, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False))


def getUser(id_, key=None):
    users = openjson('users.json')
    if str(id_) not in users:
        users[str(id_)] = {
            'name': vk.users.get(user_ids=id_)[0]['first_name'] if id_ > 0 else vk.groups.getById(group_ids=int(str(id_)[1:]))[0]['name'],
            'playname': vk.users.get(user_ids=id_)[0]['first_name'] if id_ > 0 else vk.groups.getById(group_ids=int(str(id_)[1:]))[0]['name'],
            'tip': '',
            'reps': 0,
            'likes': 0,
            'repsids': [],
            'likesids': [],
            'balance': 50,
            'chatscore': 0,
            'gamescore': 0,
            'inventory': [],
            'mention': 1
        }
        rewritejson('users.json', users)
    if key:
        if key not in users[str(id_)]:
            return
        return users[str(id_)][key]
    return users[str(id_)]


def updateUser(id_, key, act, value):
    getUser(id_)
    users = openjson('users.json')
    if act == '=':
       users[str(id_)][key] = value
    elif act == '+=':
       users[str(id_)][key] += value
    elif act == '-=':
        users[str(id_)][key] -= value
    rewritejson('users.json', users)


def getNamel(id_, key=None):
    user = getUser(id_)
    mention = getUser(id_, key='mention')
    if key:
        if key in user:
            name = user[key]
        else:
            name = user['name']
    else:
        name = user['name']
    if mention:
        if id_ > 0:
            return f'[id{id_}|{name}]'
        return f'[club{str(id_)[1:]}|{name}]'
    return user[name]


def formLink(id_, s):
    mention = getUser(id_, key='mention')
    if mention:
        if id_ > 0:
            return f'[id{id_}|{s}]'
        else:
            return f'[club{str(id_)[1:]}|{s}]'
    else:
        return s


def checkSpelling(string):
    admiss = True if 2 <= len(string) <= 40 else False
    alphabet = 'abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя0123456789 '
    for s in string:
        if s.lower() not in alphabet:
            admiss = False
    return admiss


def keyboard(*b):
    buttons = []
    for i in b:
        buttons.append([])
        for j in i:
            buttons[-1].append({
                'action': {
                    'type': 'text',
                    'label': j[0]
                },
                'color': j[1]
            })
    return json.dumps({'buttons': buttons, 'inline': True})


def tags(s):
    r, f = '', True
    for i in list(s):
        if f:
            if i == '<':
                f = False
            else:
                r += i
        else:
            if i == '>':
                f = True
    return r


def ids(m):
    if m:
        mentions = m.replace('[', '$sep').replace(']', '$sep').replace('|', '$sep').split('$sep')
        users = [int(m[2:]) for m in mentions if m[:2] == 'id' and m[2:].isdigit()]
        groups = [int('-' + m[4:]) for m in mentions if m[:4] == 'club' and m[4:].isdigit()]
        return users + groups
    return []


def parsementions(s, callid, key=None):
    newstring = s
    names = {}
    m = s.replace('[', '$sep').replace(']', '$sep').replace('|', '$sep').split('$sep')
    fs = []
    for i in range(len(m)):
        if fs:
            if m[i] in fs[-1]:
                continue
        if (m[i][:2] == 'id' and m[i][2:].isdigit()) or (m[i][:4] == 'club' and m[i][4:].isdigit()):
            fs.append([m[i], m[i + 1]])
    for f in fs:
        digitid = int(f[0][2:]) if f[0][:2] == 'id' else int('-' + f[0][4:])
        mention = getUser(digitid, key='mention')
        if key:
            if key == 'playname' and digitid == callid:
                name = getUser(digitid, key='себя')
            else:
                name = getUser(digitid, key=key)
        else:
            name = getUser(digitid, key='name')
        if mention:
            newstring = newstring.replace(f'[{f[0]}|{f[1]}]', f'[{f[0]}|{name}]')
        else:
            newstring = newstring.replace(f'[{f[0]}|{f[1]}]', name)
    return newstring


def getimage(url):
    http = urllib3.PoolManager()
    return {'file': (url, http.request('GET', url, preload_content=False).data)}


def getgif(url, count):
    http = urllib3.PoolManager()
    gifs = json.loads(requests.get(url).text)['data']
    if gifs:
        target = choice(gifs[:count])['images']['downsized']['url']
        return {'file': (target, http.request('GET', target, preload_content=False).data)}
    return None


def uploadfile(file, peer):
    server = vk.docs.getMessagesUploadServer(type='doc', peer_id=peer)
    uploaded_file = json.loads(requests.post(server['upload_url'], files=file).text)['file']
    doc = vk.docs.save(file=uploaded_file, title='asura-bot')['doc']
    id_, ownerid = doc['id'], doc['owner_id']
    return f'doc{ownerid}_{id_}'


def uploadvideo(server):
    return json.loads(requests.post(server, files=file).text)['video_id']


def uploadimage(file, peer):
    server = vk.photos.getMessagesUploadServer(peer_id=peer)
    uploaded_file = json.loads(requests.post(server['upload_url'], files=file).text)
    photo = vk.photos.saveMessagesPhoto(
        server=uploaded_file['server'],
        photo=uploaded_file['photo'],
        hash=uploaded_file['hash'])[0]
    id_, ownerid = photo['id'], photo['owner_id']
    return f'photo{ownerid}_{id_}'


def getAvatar(id_, peer):
    if id_ > 0:
        resolve = vk.users.get(user_ids = id_, fields = ['photo_id'])[0]
        if 'photo_id' in resolve:
            return 'photo' + resolve['photo_id']
        else:
            return 'photo-187703257_457239149'
    else:
        resolve = vk.groups.getById(group_ids = str(id_)[1:], fields = ['photo_200'])[0]
        if 'photo_200' in resolve:
            return uploadimage(getimage(resolve['photo_200']), peer)
        else:
            return 'photo-187703257_457239149'


#init
class Bot:
    def __init__(self, userId, peerId, chatId, reply):
        self.peer = peerId
        self.chat = chatId
        self.id = userId
        self.reply = reply
        self.user = getUser(self.id)
        self.playname = getNamel(self.id, key='playname')
        self.name = getNamel(self.id)


    #echo 
    def echo(self, *args, attach='', keyboard={}, peer=None, chat=None, sticker_id=0):
        if self.chat:
            vk.messages.send(
                chat_id = self.chat if not chat else chat,
                message = ''.join(args) if all([True if str(i) == i else False for i in args]) else args,
                attachment = attach,
                keyboard = keyboard,
                sticker_id = sticker_id,
                random_id = 0)   
        else:
            vk.messages.send(
                peer_id = self.peer if not peer else peer,
                message = ''.join(args) if all([True if str(i) == i else False for i in args]) else args,
                attachment = attach,
                keyboard = keyboard,
                sticker_id = sticker_id,
                random_id = 0)   


    #handle
    def handle(self, msg):
        if '[club187703257|' in msg:
            msg = msg.split(']')[0].strip(',').strip(' ')

        if msg == 'Сбросить имена':
            self.handle('имя сбросить')
            self.handle('имя игровое сбросить')

        cmd, args, argl = '', [], ''
        msg_splitted = msg.split(' ', 1)
        cmd = msg_splitted[0].lower()
        if len(msg_splitted) > 1:
            args = msg_splitted[1].split()
            argl = msg_splitted[1]

        if DEBUG:
            if cmd in cmds.keys():
                print(f'\n"{msg}" at', str(datetime.now())[:-4])

        if cmd == '🤝':
            if argl:
                if ids(argl):
                    uid = ids(argl)[0]
                    if uid == self.id:
                        return self.echo(f'{self.name}, ты не можешь оказывать уважение самому себе 😔')
                    if self.id in getUser(uid, key='repsids'):
                        return self.echo(f'{self.name}, ты уже оказывал уважение этому пользователю 😔')
                    updateUser(uid, 'reps', '+=', 1)
                    updateUser(uid, 'repsids', '+=', [self.id])
                    return self.echo(f'{formLink(uid, "+🤝")} от {self.name}.')

        elif cmd == '❤':
            if argl:
                if ids(argl):
                    uid = ids(argl)[0]
                    if uid == self.id:
                        return self.echo(f'{self.name}, ты не можешь лайкнуть самого себя 😔')
                    if self.id in getUser(uid, key='likesids'):
                        return self.echo(f'{self.name}, ты уже лайкнул этого пользователя 😔')
                    updateUser(uid, 'likes', '+=', 1)
                    updateUser(uid, 'likesids', '+=', [self.id])
                    return self.echo(f'{formLink(uid, "+❤")} от {self.name}.')

        elif cmd == 'рп':
            if not argl:
                return self.echo(cmds['рп'])
            prefix = ''
            for s in argl:
                if s in '"*/<[{(@#$%^&-=+_':
                    prefix += s
                else:
                    break
            if prefix:
                argl = argl[len(prefix):].strip()
                argl = prefix + argl.replace('"', '\"')
                pairs = {
                    '[': ']',
                    '{': '}',
                    '(': ')',
                    '<': '>'
                }
                affix = ''.join([pairs[s] if s in pairs.keys() else s for s in prefix[::-1]])
            else:
                argl = '"' + argl
                affix = '"'
            uid = None
            if self.reply:
                uid = self.reply['from_id']
            print(uid, self.id)
            if uid:
                if uid == self.id:
                    uname = formLink(self.id, 'себя')
                else:
                    uname = getNamel(uid, key='playname')
                argl += f' {uname}{affix}'
            else:
                argl += affix
            parsed = parsementions(argl, self.id, key='playname')
            return self.echo(f'{self.playname}: {parsed}')

        elif cmd == 'имя':
            if argl:
                if args[0] == 'игровое':
                    names = {}
                    for k, v in openjson('users.json').items():
                        names[k] = v['playname']
                    formtype = 'игровое имя'
                    keytype = 'playname'
                    if args[1] == 'сбросить':
                        if str(self.id) in names:
                            del names[str(self.id)]
                        name = vk.users.get(user_ids=self.id)[0]['first_name']
                        updateUser(self.id, keytype, '=', name)
                        return self.echo(f'✅️ Ты сбросил своё {formtype} на {formLink(self.id, name)}.')
                else:
                    names = {}
                    for k, v in openjson('users.json').items():
                        names[k] = v['name']
                    formtype = 'регулярное имя'
                    keytype = 'name'
                    if argl == 'сбросить':
                        if str(self.id) in names:
                            del names[str(self.id)]
                        name = vk.users.get(user_ids=self.id)[0]['first_name']
                        updateUser(self.id, keytype, '=', name)
                        return self.echo(f'✅️ Ты сбросил своё {formtype} на {formLink(self.id, name)}.')
                if len(args) > 1:
                    name = argl.split(' ', 1)[1]
                else:
                    name = argl
                busy = False
                if keytype == 'playname':
                    busy = False
                else:
                    for k, v in names.items():
                        if v.lower() == name.lower():
                            if k == str(self.id):
                                busy = True
                if not busy:
                    admiss = checkSpelling(argl)
                    if admiss:
                        updateUser(self.id, keytype, '=', name)
                        return self.echo(f'✅️ Ты изменил своё {formtype} на {formLink(self.id, name)}.')
                    else:
                        return self.echo(f'{self.name}, этот никнейм имеет некорректное написание.\n💭Напоминаю, что никнеймы состоят только из букв, цифр и пробелов и имеют длину не менее двух и не более 40 символов.')
                else:
                    return self.echo(f'{self.name}, попробуй другое имя, такое уже занято.\n💭 Если ты хочешь сбросить своё имя на свое настоящее, то набери в конце "сбросить".')

        elif cmd == 'заметка':
            if not argl:
                return self.echo(cmds['заметка'])
            if len(argl) > 120:
                return self.echo(f'{self.name}, заметка должна быть длинной не более 120 символов.')
            if argl == '-':
                updateUser(self.id, 'tip', '=', '')
                return self.echo(f'✅ {self.name}, ты сбросил свою заметку в статусе.')
            updateUser(self.id, 'tip', '=', argl.replace('"', '\"'))
            return self.echo(f'✅ {self.name}, ты изменил свою заметку в статусе.')

        elif cmd == 'пара':
            if self.peer == self.id:
                return self.echo(f'{self.name}, такая команда работает только в беседах 😔')
            try:
                people = vk.messages.getConversationMembers(peer_id = self.peer)['profiles']
            except Exception:
                flag = False
                return self.echo(f'{self.name}, такая команда работает только с правами администратора 😔')
            if self.reply:
                t = self.reply['from_id']
            else:
                t = self.id
            t = t['id'] if type(t) == type({}) else t
            if t == self.id:
                self.echo(f'🔍 {self.name}, ищу тебе пару...')
            else:
                self.echo(f'🔍 {self.name}, ищу пару для {getNamel(t)}...')
            t = {
                'id': t,
                'name': self.name if t == self.id else getNamel(t)
            }
            pt = choice(people)
            while pt['id'] == t['id']:
                pt = choice(people)
            pt = {
                'name': self.name if pt['id'] == self.id else getNamel(pt['id'])
            }
            mformatted = choice([
                'Думаю, что {} и {} - отличная пара ❤',
                '{}, тебе очень подходит {}, я уверена 💙',
                'Никто не знал, но {} и {} уже давно нравятся друг другу 💛'
            ]).format(t['name'], pt['name'])
            return self.echo(mformatted)
        
        elif cmd == 'гиф':
            if not argl:
                return self.echo(cmds['гиф'])
            c = None
            f = True
            if len(args) > 1:
                if not args[1].isdigit():
                    if not 1 <= int(args[1]) <= 100:
                        f = False
                else:
                    if 1 <= int(args[1]) <= 100:
                        c = int(args[1])
            if f:
                self.echo(f'{self.name}, ищу гифку по твоему запросу 🔍')
                gif = getgif(
                    'https://api.giphy.com/v1/gifs/search?api_key=wZz52MVyc5G3r5CPKFYNgXl7vgIRwvzo&q=' + argl,
                    c if c else 10
                )
                if gif:
                    return self.echo(f'{formLink(self.id, "✅")}:', attach=(uploadfile(gif, self.peer)))
                else:
                    return self.echo(f'{self.name}, гифок по запросу "{argl}" не оказалось.')
            return self.echo(cmds['гиф'])

        elif cmd == 'ютуб':
            return self.echo('На данный момент команда "ютуб" пока не работает ;(')
            if not argl:
                return self.echo(cmds['ютуб'])
            else:
                self.echo(f'🔍 {self.name}, ищу видео по твоему запросу...')
                res = json.loads(YoutubeSearch(argl, max_results=10).to_json())['videos']
                if not res:
                    return self.echo(f'{self.name}, видео по запросу "{argl}" не оказалось.')
                else:
                    videodata = choice(res)
                    video = vk_user.video.save(name=videodata['title'], is_private=1, wallpost = 0, link=f'youtube.com{videodata["link"]}')
                    requests.get(video['upload_url'])
                    return self.echo(f'{formLink(id_, "✅")}:', attach=(f'video{video["owner_id"]}_{video["video_id"]}'))

        elif cmd == 'статус':
            flag = 0
            uid = self.id
            if self.reply:
                uid = self.reply['from_id']
            if uid == self.id:
                flag = 1
            user = getUser(uid)
            name = user['name']
            if uid > 0:
                resp = vk.users.get(user_ids=uid, fields='screen_name')[0]
                if 'screen_name' not in resp:
                    screenname = f'id{uid}'
                else:
                    screenname = resp['screen_name']
            else:
                resp = vk.groups.getById(group_ids=int(str(uid)[1:]), fields='screen_name')[0]
                if 'screen_name' not in resp:
                    screenname = f'club{str(uid)[1:]}'
                else:
                    screenname = resp['screen_name']
            chatlvl = user['chatscore'] // 50
            gamelvl = user['gamescore'] // 10
            chatlvl = chatmaxlvl if chatlvl > chatmaxlvl else chatlvl
            gamelvl = gamemaxlvl if gamelvl > gamemaxlvl else chatlvl
            chatrank = chatranks[chatlvl // 10 * 10]
            gamerank = gameranks[gamelvl // 10 * 10]
            tip = f'"{user["tip"]}"' if user["tip"] else ''
            form = [
                f'Твоя репутация - {user["reps"]} 🤝🏻 {user["likes"]} ❤',
                f'Твоё игровое имя - {user["playname"]}',
                f'Твой ранг в чате - {chatrank}, {chatlvl} ур.',
                f'А игровой ранг - {gamerank}, {gamelvl} ур.',
                '',
                '💭 Подробнее в комманде "помощь".' 
            ]
            form = '\n'.join(form)
            if flag:
                return self.echo(
                    f'👋🏻 {name}: {tip}\n{form}',
                    keyboard=keyboard(
                        [(f'🤝 @{screenname}', 'positive'), (f'❤ @{screenname}', 'positive')],
                        [('Имя сбросить', 'secondary'), ('Имя игровое сбросить', 'secondary')],
                    )
                )
            return self.echo(
                f'👋🏻 {name}: {tip}\n{form}',
                keyboard=keyboard(
                    [(f'🤝 @{screenname}', 'positive'), (f'❤ @{screenname}', 'positive')]
                )
            )

        elif cmd == 'магазин':
            self.echo('Скоро.')

        elif cmd == 'инвентарь':
            self.echo('Скоро.')

        elif cmd == 'помощь':
            if argl:
                if argl not in cmds.keys():
                    return self.echo(f'{self.name}, такой команды нет в списке команд 😔\nЕсли ты хочешь узнать список команд, введи "помощь".')
                return self.echo(cmds[argl])
            form = ', '.join(list(cmds.keys()))
            return self.echo(
                f'{self.name}, это небольшое FAQ по использованию бота 👇\n\n',
                f'💭 Список команд - {form}.\nЧтобы узнать о команде подробнее, отправь "помощь" и название команды, например "помощь гиф".\n\n'
                '💭 Репутация - это ваши лайки и уважение. Чтобы лайкнуть или респектнуть человека, достаточно в его статусе нажать на соответствующую кнопку. Иногда бот сам определяет, когда уважаете или лайкайте человека, в зависимости от ответа на его сообщение.\n\n'
                '💭 Ранги - это именование вашего уровня. Всего доступно 200 уровней, из которых вы можете открыть 20 рангов. Каждый уровень в чате вам начисляется за 50 очков, 1 очко вы получаете за обычное сообщение, а 3 очка за обращение к боту (вам не будут начисляться очки за сообщения в лс бота). Каждый уровень в играх вам начисляется за 10 очков, 5 очков за 1 победу.'
            )

        elif cmd == 'упоминание':
            if not args:
                return self.echo(cmds['упоминание'])
            if argl not in ['выкл', 'вкл']:
                return self.echo(cmds[argl])
            if argl == 'выкл':
                updateUser(self.id, 'mention', '=', 0)
                return self.echo(f'✅ {self.name}, теперь я не буду @упоминать тебя в сообщениях.')
            elif argl == 'вкл':
                updateUser(self.id, 'mention', '=', 1)
                return self.echo(f'✅ {self.name}, теперь я буду @упоминать тебя в сообщениях.')

        elif cmd == 'число':
            if len(args) < 3:
                if not args[1].isnumeric():
                    return self.echo(f'{self.name}, укажи число корректно.')
                en = int(args[1])
            if len(args) >= 3:
                if not args[1].isnumeric() or not args[2].isnumeric():
                    return self.echo(f'{self.name}, укажи числа корректно.')
                sn = int(args[1])
                en = int(args[1])
            roll = randint(sn, en)
            return self.echo(f'🎲 {self.name}, рулетка выдала {roll}.')
        
        for w in msg.lower().split():
            for i in repkeys:
                if i == w.lower():
                    if self.reply:
                        uid = self.reply['from_id']
                        if uid == self.id:
                            return self.echo(f'{self.name}, ты не можешь оказывать уважение самому себе 😔')
                        if self.id in getUser(uid, key='repsids'):
                            return self.echo(f'{self.name}, ты уже оказывал уважение этому пользователю 😔')
                        updateUser(uid, 'reps', '+=', 1)
                        updateUser(uid, 'repsids', '+=', [self.id])
                        return self.echo(f'{formLink(uid, "+🤝")} от {self.name}.')
            for i in likekeys:
                if i == w.lower():
                    if self.reply:
                        uid = self.reply['from_id']
                        if uid == self.id:
                            return self.echo(f'{self.name}, ты не можешь лайкнуть самого себя 😔')
                        if self.id in getUser(uid, key='likesids'):
                            return self.echo(f'{self.name}, ты уже лайкнул этого пользователя 😔')
                        updateUser(uid, 'likes', '+=', 1)
                        updateUser(uid, 'likesids', '+=', [self.id])
                        return self.echo(f'{formLink(uid, "+❤")} от {self.name}.')

        if DEBUG:
            admin(self.id, cmd, argl, args)
        
        if cmd.lower() not in cmds.keys():
            words = openjson('words.json')
            for word in [i.lower() for i in msg.split()]:
                if not [i for i in word if i in '[]|@/()<>$%&']:
                    words['words'].append(''.join([i for i in word if i not in '.,?.;:"']))
            rewritejson('words.json', words)
        else:
            if self.chat:
                updateUser(event.obj['from_id'], 'chatscore', '+=', 2)


    def perform(self, msg):
        try:
            self.handle(msg)
        except Exception as e:
            if DEBUG:
                log(e)




from hidden import *


bot_session = vk_api.VkApi(token=token)
user_session = vk_api.VkApi(token=usertoken)
vk = bot_session.get_api()
vk_user = user_session.get_api()


if DEBUG:
    print('loaded')


class mainThread(VkBotLongPoll):
    def listen(self):
        while True:
            try:                
                for event in self.check():
                    yield event
            except Exception as e:
                print('error', e)


for event in mainThread(bot_session, 187703257).listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.obj['text']:
            if event.from_chat:
                updateUser(event.obj['from_id'], 'chatscore', '+=', 1)
                chat = int(event.chat_id)
            else:
                chat = 0
            if event.obj['fwd_messages']:
                reply = event.obj['fwd_messages']
            else:
                if 'reply_message' in event.obj:
                    reply = event.obj['reply_message']
                else:
                    reply = 0
            if DEBUG:
                sleep(event.obj['text'], event.obj['from_id'])
            bot = Bot(event.obj['from_id'], event.obj['peer_id'], chat, reply)
            Thread(target=bot.perform, args=(event.obj['text'],)).start()