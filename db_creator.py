import asyncio
import json

from src.extensions.DBWorkerExtension import DataBase


# consts TEST SERVER
# data_str = json.dumps(data)
# data = json.loads(data_str)
# A, H, P - последние


smiles_channel = ['➕', '●']
afk_channel_id = '691184292830904399'
parrent_channel_ids = {
    # RU
    '1128735946288930940': 'RU:СБ:SB:1119274677274153090:-', # SB
    '1129082673080569997': 'RU:СБ:SB:1119274677274153090:1',
    '1129082721076007054': 'RU:СБ:SB:1119274677274153090:0',
    '1129082812637655190': 'RU:СБ:SB:1119274677274153090:2',

    '1128735907118338178': 'RU:РБ:RB:1119275461038575716:-', # RB
    '1129082270133788793': 'RU:РБ:RB:1119275461038575716:1',
    '1129082293936476263': 'RU:РБ:RB:1119275461038575716:0',
    '1129082320951976046': 'RU:РБ:RB:1119275461038575716:2',

    '1128735830270283976': 'RU:АБ:AB:1119275516088815626:-', # AB
    '1129081462008860774': 'RU:АБ:AB:1119275516088815626:1',
    '1129081496070783037': 'RU:АБ:AB:1119275516088815626:0',
    '1129081521861578773': 'RU:АБ:AB:1119275516088815626:2',
    '1128735559062409398': 'RU:Полигон:DR:1119275995300638720:-', # DR

    # обновить def update_message and on_voice_state_update
    # ENG
    '1128739999450411140': 'EN:SB:SB:1119360770753441903:-', # SB
    #'0': '',
    #'0': '',
    #'0': '',

    '1128739940423979009': 'EN:RB:RB:1119361141957738596:-', # RB
    #'0': '',
    #'0': '',
    #'0': '',

    '1128739857779392552': 'EN:AB:AB:1119362343311245412:-', # AB
    #'0': '',
    #'0': '',
    #'0': '',

    '1128739766351966229': 'EN:Polygon:DR:1119363204183773295:-', # DR
}

tech_ids = {
    '-': "-",
    '0': "ТANK",
    '1': "АIR",
    '2': "SHIP",
    '3': "HELI"
}
nation_ids = {
    '-': "-",
    '0': "USA",
    '1': "USSR",
    '2': "JP",
    '3': "DE",
    '4': "UK",
    '5': "IT",
    '6': "FR",
    '7': "CN",
    '8': "SE",
    '9': "IL",
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
