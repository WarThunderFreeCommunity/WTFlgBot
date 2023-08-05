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
    '1135191471952248904': 'RU:АБ:AB:1133741018802569246:-', # AB
    '1135191539602173992': 'RU:АБ:AB:1133741018802569246:-',

    '1135191149674504202': 'RU:РБ:RB:1133741113925181450:-', # RB
    '1135191397293629500': 'RU:РБ:RB:1133741113925181450:-',

    '1135192060157251674': 'RU:СБ:SB:1133741219835555930:-', # SB
    '1135192090532388895': 'RU:СБ:SB:1133741219835555930:-', # 0, 1, 2

    # ENG
    '1135192672571768912': 'EN:AB:AB:1134865039334064239:-', # AB
    '1135192967729119252': 'EN:AB:AB:1134865039334064239:-',

    '1135193034930274334': 'EN:RB:RB:1134865098758955090:-', # RB
    '1135193074499326135': 'EN:RB:RB:1134865098758955090:-',

    '1135193151980707911': 'EN:SB:SB:1134865182657626153:-', # SB
    '1135193123685937212': 'EN:SB:SB:1134865182657626153:-',
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
