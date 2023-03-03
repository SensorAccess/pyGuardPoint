from asyncio import Future
from concurrent.futures import ThreadPoolExecutor
from .guardpoint import GuardPoint, GuardPointError


class GuardPointAsync:

    def __init__(self, **kwargs):
        self.gp = GuardPoint(**kwargs)
        self.executor = ThreadPoolExecutor(max_workers=1)

    def get_card_holder(self, on_finished, uid=None, card_code=None):
        def handle_future(future):
            try:
                r = future.result()
                on_finished(r)
            except GuardPointError as e:
                on_finished(e)
            except Exception as e:
                on_finished(GuardPointError(e))

        future = self.executor.submit(self.gp.get_card_holder, uid=uid, card_code=card_code)
        future.add_done_callback(handle_future)

    def get_card_holders(self, on_finished, offset=0, limit=10, search_terms=None, cardholder_type_name=None):
        def handle_future(future):
            try:
                r = future.result()
                on_finished(r)
            except GuardPointError as e:
                on_finished(e)
            except Exception as e:
                on_finished(GuardPointError(e))

        future = self.executor.submit(self.gp.get_card_holders, offset=offset, limit=limit, search_terms=search_terms,
                                      cardholder_type_name=cardholder_type_name)
        future.add_done_callback(handle_future)

    def get_areas(self, on_finished):
        def handle_future(future):
            try:
                r = future.result()
                on_finished(r)
            except GuardPointError as e:
                on_finished(e)
            except Exception as e:
                on_finished(GuardPointError(e))

        future = self.executor.submit(self.gp.get_areas)
        future.add_done_callback(handle_future)



