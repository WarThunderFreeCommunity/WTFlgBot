import asyncio
import json

from src.extensions.DBWorkerExtension import DataBase


# consts TEST SERVER
# data_str = json.dumps(data)
# data = json.loads(data_str)
# A, H, P - последние
debug = 0
if debug == 1:
    smiles_channel = ['➕', '●']
    afk_channel_id = '1049384644669354014'
    parrent_channel_ids = {
        '1049377480273829940': 'RU:T:SB:1049377740295524415',
        '1049377740295524415': 'RU:A:SB:-',
        '1049377837892771870': 'RU:T:RB:1049378068831154227',
        '1049378068831154227': 'RU:A:RB:-',
        '1049377874018308127': 'RU:T:AB:1049378105422254090',
        '1049378105422254090': 'RU:A:AB:-',
        '1074319482350227576': 'RU:S:SH:1074319540357431337', # морские 
        '1074319540357431337': 'RU:H:HE:-', # вертолёты
        '1049378860124352583': 'RU:P:PO:-', # полигон
        '1074316150894235698': 'EN:T:SB:1074316437969178736',
        '1074316437969178736': 'EN:A:SB:-',
        '1074348447399948319': 'EN:T:RB:1074348529012719726',
        '1074348529012719726': 'EN:A:RB:-',
        '1074349079267647528': 'EN:T:AB:1074349118463426650',
        '1074349118463426650': 'EN:A:AB:-',
        '1074349366279688273': 'EN:S:SH:1074349465797922856', # морские 
        '1074349465797922856': 'EN:H:HE:-', # вертолёты
        '1074349269210906624': 'EN:P:PO:-', # полигон
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
    cmbrId - id боевой рейтинг голосового канала
    techId - id нация голосового канала
    """
    await db.run_que(
        "CREATE TABLE VoiceCogChannels \
        (parrentId INTEGER, channelId INTEGER, \
        creatorId INTEGER, channelTime INTEGER, \
        messageId INTEGER, cmbrId REAL, \
        techId INTEGER)"
    )
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
            ("parrent_channel_ids", f"{json.dumps(parrent_channel_ids)}")
        ]
    )
    
    # Creating table in VKResendCog
    await db.run_que("CREATE TABLE IF NOT EXISTS VKResendCog (valId INTEGER)")
    ids = [8989, 8888, 8465, 4567, 1377, 1376, 1374, 1373, 1371, 1370]
    await db.run_que("INSERT INTO VKResendCog (valId) VALUES (?)", (json.dumps(ids),))
    # 1383, 1380

    
    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
