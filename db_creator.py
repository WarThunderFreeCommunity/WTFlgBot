import asyncio
import json

from src.extensions.DBWorkerExtension import DataBase


# consts
# data_str = json.dumps(data)
# data = json.loads(data_str)
# A, H, P - последние
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
    """
    await db.run_que(
        "CREATE TABLE VoiceCogChannels \
        (parrentId INTEGER, channelId INTEGER, \
        creatorId INTEGER, channelTime INTEGER, \
        messageId INTEGER)"
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
    

    await db.close()
    
    


if __name__ == "__main__":
    asyncio.run(main())
