Asyncio
========
pyGuardPoint also can be use aiohttp.

Initial a asyncio connection with the following:

>>> from pyGuardPoint import GuardPointAsyncIO, GuardPointError, GuardPointUnauthorized
>>> gp = GuardPointAsyncIO(host=GP_HOST,
>>>                        username=GP_USER,
>>>                        pwd=GP_PASS,
>>>                        p12_file=TLS_P12,
>>>                        p12_pwd=TLS_P12_PWD,
>>>                        site_uid="11111111-1111-1111-1111-111111111111")