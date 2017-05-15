import asyncio
from urllib.parse import urlencode

import aiohttp
import requests
import slacker

from .compat import AIOHTTP_2, PY_350, ensure_future

__version__ = '0.0.6'

Error = slacker.Error

Response = slacker.Response


class BaseAPI(slacker.BaseAPI):

    def __init__(
        self,
        token=None,
        timeout=slacker.DEFAULT_TIMEOUT,
        *, loop=None
    ):
        if loop is None:
            loop = asyncio.get_event_loop()

        self.loop = loop

        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                use_dns_cache=False,
                loop=self.loop,
            ),
        )

        self.methods = {
            requests.get: 'GET',
            requests.post: 'POST',
        }

        self.futs = set()

        super().__init__(token=token, timeout=timeout)

    @asyncio.coroutine
    def __request(self, method, api, **kwargs):
        method = self.methods[method]

        kwargs.setdefault('params', {})
        kwargs.setdefault('timeout', None)

        if self.token:
            kwargs['params']['token'] = self.token

        kwargs['params'] = urlencode(kwargs['params'], doseq=True)

        if method == 'POST':
            files = kwargs.pop('files', None)

            if files is not None:
                data = kwargs.pop('data', {})

                _data = aiohttp.FormData()

                for k, v in files.items():
                    _data.add_field(k, open(v.name, 'rb'))

                for k, v in data.items():
                    if v is not None:
                        _data.add_field(k, str(v))

                kwargs['data'] = _data

        _url = slacker.API_BASE_URL.format(api=api)

        _request = self.session.request(method, _url, **kwargs)

        _response = None

        try:
            with aiohttp.Timeout(self.timeout, loop=self.loop):
                _response = yield from _request

            _response.raise_for_status()

            text = yield from _response.text()
        finally:
            if _response is not None:
                yield from _response.release()

        response = Response(text)

        if not response.successful:
            raise Error(response.error)

        return response

    def _request(self, method, api, **kwargs):
        coro = self.__request(method, api, **kwargs)

        fut = ensure_future(coro, loop=self.loop)

        self.futs.add(fut)

        fut.add_done_callback(self.futs.remove)

        return fut

    @asyncio.coroutine
    def close(self):
        if self.futs:
            yield from asyncio.gather(*self.futs, loop=self.loop)

        coro = self.session.close()

        if AIOHTTP_2:
            return

        yield from coro


class IM(BaseAPI, slacker.IM):
    pass


class API(BaseAPI, slacker.API):
    pass


class DND(BaseAPI, slacker.DND):
    pass


class RTM(BaseAPI, slacker.RTM):
    pass


class Auth(BaseAPI, slacker.Auth):
    pass


class Bots(BaseAPI, slacker.Bots):
    pass


class Chat(BaseAPI, slacker.Chat):
    pass


class TeamProfile(BaseAPI, slacker.TeamProfile):
    pass


class Team(BaseAPI, slacker.Team):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._profile = TeamProfile(*args, **kwargs)

    def close(self):
        coros = [
            super().close(),
            self._profile.close(),
        ]
        return asyncio.gather(*coros, loop=self.loop)


class Pins(BaseAPI, slacker.Pins):
    pass


class MPIM(BaseAPI, slacker.MPIM):
    pass


class UsersProfile(BaseAPI, slacker.UsersProfile):
    pass


class Users(BaseAPI, slacker.Users):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._profile = UsersProfile(*args, **kwargs)

    def close(self):
        coros = [
            super().close(),
            self._profile.close(),
        ]
        return asyncio.gather(*coros, loop=self.loop)


class FilesComments(BaseAPI, slacker.FilesComments):
    pass


class Files(BaseAPI, slacker.Files):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._comments = FilesComments(*args, **kwargs)

    def close(self):
        coros = [
            super().close(),
            self._comments.close(),
        ]
        return asyncio.gather(*coros, loop=self.loop)


class Stars(BaseAPI, slacker.Stars):
    pass


class Emoji(BaseAPI, slacker.Emoji):
    pass


class Search(BaseAPI, slacker.Search):
    pass


class Groups(BaseAPI, slacker.Groups):
    pass


class Channels(BaseAPI, slacker.Channels):
    pass


class Presence(BaseAPI, slacker.Presence):
    pass


class Reminders(BaseAPI, slacker.Reminders):
    pass


class Reactions(BaseAPI, slacker.Reactions):
    pass


class IDPGroups(BaseAPI, slacker.IDPGroups):
    pass


class UserGroupsUsers(BaseAPI, slacker.UserGroupsUsers):
    pass


class UserGroups(BaseAPI, slacker.UserGroups):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._users = UserGroupsUsers(*args, **kwargs)

    def close(self):
        coros = [
            super().close(),
            self._users.close(),
        ]
        return asyncio.gather(*coros, loop=self.loop)


class IncomingWebhook(BaseAPI, slacker.IncomingWebhook):

    def __init__(
        self,
        url=None,
        timeout=slacker.DEFAULT_TIMEOUT,
        *, loop=None
    ):
        self.url = url

        super().__init__(token=None, timeout=timeout, loop=loop)

    @asyncio.coroutine
    def post(self, data):
        if not self.url:
            raise slacker.Error('URL for incoming webhook is undefined')

        _request = self.session.request(
            'POST',
            self.url,
            data=data,
            timeout=None,
        )

        _response = None

        try:
            with aiohttp.Timeout(self.timeout, loop=self.loop):
                _response = yield from _request

            _response.raise_for_status()

            _json = yield from _response.json()
        finally:
            if _response is not None:
                yield from _response.release()

        return _json


class Slacker(slacker.Slacker):

    def __init__(
        self,
        token,
        incoming_webhook_url=None,
        timeout=slacker.DEFAULT_TIMEOUT,
        *, loop=None
    ):
        if loop is None:
            loop = asyncio.get_event_loop()

        self.loop = loop

        self.im = IM(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.api = API(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.dnd = DND(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.rtm = RTM(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.auth = Auth(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.bots = Bots(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.chat = Chat(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.team = Team(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.pins = Pins(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.mpim = MPIM(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.users = Users(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.files = Files(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.stars = Stars(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.emoji = Emoji(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.search = Search(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.groups = Groups(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.channels = Channels(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.presence = Presence(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.reminders = Reminders(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.reactions = Reactions(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.idpgroups = IDPGroups(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.usergroups = UserGroups(
            token=token,
            timeout=timeout,
            loop=self.loop,
        )
        self.incomingwebhook = IncomingWebhook(
            url=incoming_webhook_url,
            timeout=timeout,
            loop=self.loop,
        )

    def close(self):
        coros = [
            self.im.close(),
            self.api.close(),
            self.dnd.close(),
            self.rtm.close(),
            self.auth.close(),
            self.bots.close(),
            self.chat.close(),
            self.team.close(),
            self.pins.close(),
            self.mpim.close(),
            self.users.close(),
            self.files.close(),
            self.stars.close(),
            self.emoji.close(),
            self.search.close(),
            self.groups.close(),
            self.channels.close(),
            self.presence.close(),
            self.reminders.close(),
            self.reactions.close(),
            self.idpgroups.close(),
            self.usergroups.close(),
            self.incomingwebhook.close(),
        ]

        return asyncio.gather(*coros, loop=self.loop)

    if PY_350:
        @asyncio.coroutine
        def __aenter__(self):  # noqa
            return self

        def __aexit__(self, *exc_info):  # noqa
            return self.close()
