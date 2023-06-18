import asyncio
import json

from src.extensions.DBWorkerExtension import DataBase


# consts TEST SERVER
# data_str = json.dumps(data)
# data = json.loads(data_str)
# A, H, P - последние
debug = 1
if debug == 1:
    smiles_channel = ['➕', '●']
    afk_channel_id = '1049384644669354014'
    parrent_channel_ids = {
        '1049377480273829940': 'RU:СБ:SB:1049375830108807239',
        '1049377837892771870': 'RU:РБ:RB:1049375910106759249',
        '1049377874018308127': 'RU:АБ:AB:1049375990998118461',
        '1074319482350227576': 'RU:Полигон:DR:1049378707581718630', # морские 
    }
    tech_ids = {
        '-': "❌",
        '0': "🚙",
        '1': "✈",
        '2': "🚢",
    }
    nation_ids = {
        '-': "❌",
        '0': "🦅",
        '1': "⚒",
        '2': "🍣",
    }
else:
    smiles_channel = ['➕', '●']
    afk_channel_id = '691184292830904399'
    parrent_channel_ids = {
        '1119276330253566042': 'RU:T:SB:1119287140585582723',
        '1119287140585582723': 'RU:A:SB:-',
        '1119276441952063518': 'RU:T:RB:1119276522000367676',
        '1119276522000367676': 'RU:A:RB:-',
        '1119276788422561802': 'RU:T:AB:1119276934061375608',
        '1119276934061375608': 'RU:A:AB:-',
        '1119277201704099860': 'RU:S:SH:1119277285531451564', # морские 
        '1119277285531451564': 'RU:H:HE:-', # вертолёты
        '1119277359158276166': 'RU:P:PO:1119357957893799937', # полигон
        '1119357957893799937': 'RU:O:OP:-', # общалка
        '1119363801561714830': 'EN:T:SB:1119363908415791174',
        '1119363908415791174': 'EN:A:SB:-',
        '1119364907868115065': 'EN:T:RB:1119364910753792201',
        '1119364910753792201': 'EN:A:RB:-',
        '1119366275265724577': 'EN:T:AB:1119366324745932810',
        '1119366324745932810': 'EN:A:AB:-',
        '1119366554337951744': 'EN:S:SH:1119366610738741269', # морские 
        '1119366610738741269': 'EN:H:HE:-', # вертолёты
        '0000000000000000000': 'EN:P:PO:0000000000000000000', # полигон
        '0000000000000000000': 'EN:O:OP:-' # общалка
    }


async def main():
    db = DataBase("WarThunder.db")
    await db.connect()
    
    # Создание таблицы для хранения настроек активных каналов.
    """
    parrentId - id категории, используется в ...
    channelId - id канала, используется в ...
    creatorId - id админа канала, используется в ...
    channelTime - время создания, нигде не используется
    messageId - id сообщения в голосовом канале 
    techId - id нация голосового канала
    nationId - id нации которая установлена в голосовом канале
    cmbrVar - float боевой рейтинг голосового канала
    limitVar - int число лимита канала
    """
    await db.run_que(
        "CREATE TABLE VoiceCogChannels \
        (parrentId INTEGER, channelId INTEGER, \
        creatorId INTEGER, channelTime INTEGER, \
        messageId INTEGER, techId INTEGER, \
        nationId INTEGER, cmbrVar REAL, \
        limitVar INTEGER, commandTime INTEGER)"
    )

    # Создание таблицы для сохранения настроек пользователей
    """
    creatorId - id админа канала, в него сохраняются настройки
    techId - id нация голосового канала
    nationId - id нации которая установлена в голосовом канале
    cmbrVar - float боевой рейтинг голосового канала
    limitVar - int число лимита канала
    """
    await db.run_que(
        "CREATE TABLE VoiceCogChannelsSaves \
        (creatorId INTEGER, techId INTEGER, nationId INTEGER, \
        cmbrVar REAL, limitVar INTEGER)"
    )

    # Создание таблицы для одноразовой рассылки пользователям с инструкцией
    #  нужно будет сделать, при полной готовности серевера TODO



    # Создание таблицы для констант VoiceCog
    """
    constantName - имя константы
    constantValue - значение константы
    """
    await db.run_que(
        "CREATE TABLE VoiceCogConstants \
        (constantName TEXT, constantValue TEXT)"
    )

    # Заполнение констант для VoiceCog
    await db.run_que(
        "INSERT INTO VoiceCogConstants (constantName, constantValue) VALUES (?, ?)",
        [
            ("smiles_channel", f"{json.dumps(smiles_channel)}"),
            ("afk_channel_id", f"{afk_channel_id}"),
            ("parrent_channel_ids", f"{json.dumps(parrent_channel_ids)}"),
            ("tech_ids", f"{json.dumps(tech_ids)}"),
            ("nation_ids", f"{json.dumps(nation_ids)}")
        ]
    )
    
    # Создание таблицы in VKResendCog
    await db.run_que("CREATE TABLE IF NOT EXISTS VKResendCog (valId INTEGER)")
    ids = [0000, 1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888, 9999]
    await db.run_que("INSERT INTO VKResendCog (valId) VALUES (?)", (json.dumps(ids),))
    

    
    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
