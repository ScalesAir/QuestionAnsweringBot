from aiogram.utils.exceptions import ChatNotFound, \
    CantInitiateConversation, \
    BadRequest, \
    NetworkError, \
    CantParseEntities, \
    MessageTextIsEmpty, \
    TelegramAPIError, \
    BotBlocked

from aiohttp.client_exceptions import ClientConnectorError, \
    ClientOSError

# *************UTILS************** #
# ChatNotFound - Чат не найден
# CantInitiateConversation - бот не может начать разговор с пользователем
# BadRequest - Неподдерживаемый режим parse_mode
# NetworkError - Не удается подключиться к хосту api.telegram.org:443 ssl:default [Превышен таймаут семафора]
# CantParseEntities - Не удается разобрать объекты: несоответствующий конечный тег
# MessageTextIsEmpty - Пустое сообщение
# TelegramAPIError - Все ошибки
# BotBlocked - Запрещено: бот был заблокирован пользователем
_ChatNotFound = ChatNotFound
_CantInitiateConversation = CantInitiateConversation
_BadRequest = BadRequest
_NetworkError = NetworkError
_CantParseEntities = CantParseEntities
_MessageTextIsEmpty = MessageTextIsEmpty
_TelegramAPIError = TelegramAPIError
_BotBlocked = BotBlocked

# *************CLIENT************* #
# ClientConnectorError - Не удается подключиться к хосту api.telegram.org:443 ssl:default[Превышен таймаут семафора]
# ClientOSError -[WinError 1236] Подключение к сети было разорвано локальной системой
_ClientConnectorError = ClientConnectorError
_ClientOSError = ClientOSError
