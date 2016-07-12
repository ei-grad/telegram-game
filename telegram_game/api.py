"""Telegram API implementation."""

import asyncio
import aiohttp
import logging

logger = logging.getLogger(__name__)


RETRY_TIMEOUT = 30
RETRY_CODES = [429, 500, 502, 503, 504]


class BotAPIError(Exception):
    pass


class BotAPI:
    """Telegram Bot API Wrapper.
    """

    API_URL = "https://api.telegram.org"

    def __init__(self, api_token, session=None):
        """Create BotAPI instance.

        :param str api_token:
            bot API token, get it from http://telegram.me/BotFather

        :param aiohttp.ClientSession session:
            http session object to make requests to API
        """
        self.api_token = api_token
        self._http = session or aiohttp.ClientSession()
        self._offset = None

    async def __call__(self, method, **params):
        """Call Telegram Bot API.

        :param str method: Telegram API method
        :param params: Arguments for the method call
        """

        logger.debug("API request: %s %s", method, params)

        url = "{0}/bot{1}/{2}".format(self.API_URL, self.api_token, method)

        while True:

            async with self._http.post(url, data=params) as response:

                if response.status == 200:
                    data = await response.json()
                    if data['ok']:
                        return data['result']
                    else:
                        raise BotAPIError(data['description'])

                elif response.status in RETRY_CODES:
                    logger.info("Server returned %d, retrying in %d sec.",
                                response.status, RETRY_TIMEOUT)

                else:
                    if response.headers['content-type'] == 'application/json':
                        data = await response.json()
                        err_msg = data["description"]
                    else:
                        err_msg = await response.read()
                    raise BotAPIError(err_msg)

            await asyncio.sleep(RETRY_TIMEOUT)

    def getMe(self):
        """A simple method for testing your bot's auth token.

        Requires no parameters.

        :return: basic information about the bot in form of a User object.
        """
        return self('getMe')

    async def sendMessage(self, chat_id, text,
                          parse_mode=None,
                          disable_web_page_preview=None,
                          disable_notification=None,
                          reply_to_message_id=None,
                          reply_markup=None):
        """Use this method to send text messages.

        :param int|str chat_id:
            Unique identifier for the target chat or username of the target
            channel (in the format @channelusername)
        :param str text: Text of the message to be sent
        :param str parse_mode: Send Markdown or HTML, if you want Telegram apps
            to show bold, italic, fixed-width text or inline URLs in your bot's
            message.
        :param bool disable_web_page_preview: Disables link previews for links
            in this message
        :param bool disable_notification: Sends the message silently. iOS users
            will not receive a notification, Android users will receive a
            notification with no sound.
        :param int reply_to_message_id: If the message is a reply, ID of the
            original message
        :param str reply_markup: Additional interface options. A JSON-serialized
            object for an inline keyboard, custom reply keyboard, instructions
            to hide reply keyboard or to force a reply from the user.
            InlineKeyboardMarkup or ReplyKeyboardMarkup or ReplyKeyboardHide or
            ForceReply.

        :return: On success, the sent Message is returned.
        """
        params = {
            'chat_id': chat_id,
            'text': text,
        }
        if parse_mode is not None:
            params['parse_mode'] = parse_mode
        if disable_web_page_preview is not None:
            params['disable_web_page_preview'] = disable_web_page_preview
        if disable_notification is not None:
            params['disable_notification'] = disable_notification
        if reply_to_message_id is not None:
            params['reply_to_message_id'] = reply_to_message_id
        if reply_markup is not None:
            params['reply_markup'] = reply_markup
        return await self('sendMessage', **params)

    async def sendChatAction(self, chat_id, action):
        """Use this method when you need to tell the user that something is
        happening on the bot's side. The status is set for 5 seconds or less
        (when a message arrives from your bot, Telegram clients clear its typing
        status).

        .. note::

            Example: The ImageBot needs some time to process a request and upload
            the image. Instead of sending a text message along the lines of
            “Retrieving image, please wait…”, the bot may use sendChatAction with
            action = upload_photo. The user will see a “sending photo” status for
            the bot.

        We only recommend using this method when a response from the bot will
        take a noticeable amount of time to arrive.

        :param int|str chat_id:

            Unique identifier for the target chat or username of the target
            channel (in the format @channelusername)

        :param str action:

            Type of action to broadcast. Choose one, depending on what the user
            is about to receive: `typing` for text messages, `upload_photo` for
            photos, `record_video` or `upload_video` for videos, `record_audio`
            or `upload_audio` for audio files, `upload_document` for general
            files, `find_location` for location data.
        """
        return await self('sendChatAction', chat_id, action)

    async def getUpdates(self, offset=None, limit=None, timeout=None):
        """Use this method to receive incoming updates using long polling
        (`wiki`_).

        It automatically manage offset, so normaly you only have to pass a
        reasonable `timeout` value here (30 seconds is a good one, for example).

        :param int offset:

            Identifier of the first update to be returned. Must be greater by
            one than the highest among the identifiers of previously received
            updates. By default, updates starting with the earliest unconfirmed
            update are returned. An update is considered confirmed as soon as
            getUpdates is called with an _offset_ higher than its update_id.

            The negative offset can be specified to retrieve updates starting
            from -_offset_ update from the end of the updates queue. All
            previous updates will forgotten.

        :param int limit:

            Limits the number of updates to be retrieved. Values between 1—100
            are accepted. Defaults to 100.

        :param int timeout:

            Timeout in seconds for long polling. Defaults to 0, i.e. usual short
            polling

        :return: An Array of Update objects is returned.

        .. _wiki: http://en.wikipedia.org/wiki/Push_technology#Long_polling
        """

        params = {}

        if offset is None:
            offset = self._offset

        if offset is not None:
            params['offset'] = offset
        if limit is not None:
            params['limit'] = limit
        if timeout is not None:
            params['timeout'] = timeout

        updates = await self('getUpdates', **params)

        if updates:
            self._offset = max(i['update_id'] for i in updates) + 1

        return updates


class Chat:
    """An API wrapper for chat-related methods"""

    def __init__(self, api, chat_id):
        self.api = api
        self.chat_id = chat_id

    async def sendMessage(self, text,
                          parse_mode=None,
                          disable_web_page_preview=None,
                          disable_notification=None,
                          reply_to_message_id=None,
                          reply_markup=None):
        """Use this method to send text messages.

        :param str text: Text of the message to be sent
        :param str parse_mode: Send Markdown or HTML, if you want Telegram apps
            to show bold, italic, fixed-width text or inline URLs in your bot's
            message.
        :param bool disable_web_page_preview: Disables link previews for links
            in this message
        :param bool disable_notification: Sends the message silently. iOS users
            will not receive a notification, Android users will receive a
            notification with no sound.
        :param int reply_to_message_id: If the message is a reply, ID of the
            original message
        :param str reply_markup: Additional interface options. A JSON-serialized
            object for an inline keyboard, custom reply keyboard, instructions
            to hide reply keyboard or to force a reply from the user.
            InlineKeyboardMarkup or ReplyKeyboardMarkup or ReplyKeyboardHide or
            ForceReply.

        :return: On success, the sent Message is returned.
        """
        params = {
            'chat_id': self.chat_id,
            'text': text,
        }
        if parse_mode is not None:
            params['parse_mode'] = parse_mode
        if disable_web_page_preview is not None:
            params['disable_web_page_preview'] = disable_web_page_preview
        if disable_notification is not None:
            params['disable_notification'] = disable_notification
        if reply_to_message_id is not None:
            params['reply_to_message_id'] = reply_to_message_id
        if reply_markup is not None:
            params['reply_markup'] = reply_markup
        return await self.api('sendMessage', **params)

    async def sendChatAction(self, action):
        """Use this method when you need to tell the user that something is
        happening on the bot's side. The status is set for 5 seconds or less
        (when a message arrives from your bot, Telegram clients clear its typing
        status).

        .. note::

            Example: The ImageBot needs some time to process a request and upload
            the image. Instead of sending a text message along the lines of
            “Retrieving image, please wait…”, the bot may use sendChatAction with
            action = upload_photo. The user will see a “sending photo” status for
            the bot.

        We only recommend using this method when a response from the bot will
        take a noticeable amount of time to arrive.

        :param str action:

            Type of action to broadcast. Choose one, depending on what the user
            is about to receive: `typing` for text messages, `upload_photo` for
            photos, `record_video` or `upload_video` for videos, `record_audio`
            or `upload_audio` for audio files, `upload_document` for general
            files, `find_location` for location data.
        """
        return await self.api('sendChatAction', chat_id=self.chat_id, action=action)
