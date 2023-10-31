import asyncio
import json

from src.extensions.DBWorkerExtension import DataBase


# consts TEST SERVER
# data_str = json.dumps(data)
# data = json.loads(data_str)
# A, H, P - последние


smiles_channel = ['➕', '●']
afk_channel_id = '1133731589285748737'
parrent_channel_ids = {
    # RU
    '1156970907651297311': 'RU:АБ:AB:1156972463926808708:-', # AB
    '1157343155864227850': 'RU:АБ:AB:1156972463926808708:-',

    '1156970856883425310': 'RU:РБ:RB:1156972432716988537:-', # RB
    '1157343213292625990': 'RU:РБ:RB:1156972432716988537:-',

    '1156970787434135623': 'RU:СБ:SB:1156972335765655594:-', # SB
    '1157343290308444210': 'RU:СБ:SB:1156972335765655594:-', # 0, 1, 2

    # ENG
    '1156971600046993480': 'EN:AB:AB:1156973006384541716:-', # AB
    '1157368893938073700': 'EN:AB:AB:1156973006384541716:-',

    '1156971554127745064': 'EN:RB:RB:1156972968753246329:-', # RB
    '1157368955778900070': 'EN:RB:RB:1156972968753246329:-',

    '1156971512134389770': 'EN:SB:SB:1156972894329520158:-', # SB
    '1157369001807200356': 'EN:SB:SB:1156972894329520158:-',
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
    

    # admincog

    # Создание таблицы для хранения изменяемых данных о пользователе
    """
    0 userId INTEGER - id человека с наказанием
    1 adminId INTEGER - id админа, выдавшего наказание
    2 punishmentId INTEGER - id наказания (варн, мут, бан)
    3 punihsmentTime INTEGER - время на которое выдали наказание в секундах
    4 punihsmentComment TEXT - комментарий который указали при наказании
    5 punihsmentSetTime INTEGER - время когда выдали наказание
    6 punihsmentEndTime INTEGER - время конца наказания (для удобства)
    7 randomHash TEXT - индивидуальный id каждого наказания
    8 statusId INTEGER - статус заявления 0 - Ошибка, 1 - В ожидании, 2 - Выполнено
    """
    await db.run_que(
        "CREATE TABLE AdminPunishmentUsers "
        "(userId INTEGER, adminId INTEGER, "
        "punishmentId INTEGER, punihsmentTime INTEGER, "
        "punihsmentComment TEXT, punihsmentSetTime INTEGER, "
        "punihsmentEndTime INTEGER, randomHash TEXT, "
        "statusId INTEGER)" 
    )
    # Создание таблицы для хранения неизменяемых данных о пользователе
    """
    0 userId INTEGER - id человека с наказанием
    1 adminId INTEGER - id админа, выдавшего наказание
    2 punishmentId INTEGER - id наказания (варн, мут, бан)
    3 punihsmentTime INTEGER - время на которое выдали наказание в секундах
    4 punihsmentComment TEXT - комментарий который указали при наказании
    5 punihsmentSetTime INTEGER - время когда выдали наказание
    6 punihsmentEndTime INTEGER - время конца наказания (для удобства)
    7 randomHash TEXT - индивидуальный id каждого наказания
    8 statusId INTEGER - статус заявления 0 - Ошибка, 1 - В ожидании, 2 - Выполнено
    """
    await db.run_que(
        "CREATE TABLE AdminPunishmentUsersSaves "
        "(userId INTEGER, adminId INTEGER, "
        "punishmentId INTEGER, punihsmentTime INTEGER, "
        "punihsmentComment TEXT, punihsmentSetTime INTEGER, "
        "punihsmentEndTime INTEGER, randomHash TEXT, "
        "statusId INTEGER)" 
    )

    """
    
    """
    await db.run_que(
        "CREATE TABLE WTNewsCog (titleArray TEXT, typeNews INTEGER)"
    )
    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
