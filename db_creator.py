import asyncio
import json

from src.extensions.DBWorkerExtension import DataBase


# consts TEST SERVER
# data_str = json.dumps(data)
# data = json.loads(data_str)
# A, H, P - последние


smiles_channel = ['➕', '●']
afk_channel_id = '1049384644669354014'
parrent_channel_ids = {
    '1128735946288930940': 'RU:СБ:SB:1119274677274153090',
    '1128735907118338178': 'RU:РБ:RB:1119275461038575716',
    '1128735830270283976': 'RU:АБ:AB:1119275516088815626',
    '1128735559062409398': 'RU:Полигон:DR:1119275995300638720',
    '1128739999450411140': 'EN:SB:SB:1119360770753441903',
    '1128739940423979009': 'EN:RB:RB:1119361141957738596',
    '1128739857779392552': 'EN:AB:AB:1119362343311245412',
    '1128739766351966229': 'EN:Polygon:DR:1119363204183773295',
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
