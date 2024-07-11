import inspect

from src.square_sys import Square
from src.minihelps.minihelp_base import MiniHelpBase

class SquareInfo(MiniHelpBase):
    square: Square
    location: int
    can_purchase: bool
    is_special_square: bool

    @staticmethod
    def check_init_preconditions(
        square: Square,
        *args,
        **kwargs,
    ) -> bool:
        return True

    @staticmethod
    def check_init_preconditions_and_raise(*args, **kwargs) -> None:
        precond_fn = __class__.check_init_preconditions
        if not precond_fn(*args, **kwargs):
            precond_fn_pysrc = inspect.getsource(precond_fn)
            raise Exception(precond_fn_pysrc)

    def __init__(
        self,
        square: Square,
        *args,
        **kwargs,
    ) -> None:
        super().__init__()
        __class__.check_init_preconditions_and_raise(
            square,
            *args,
            **kwargs,
        )
        self.square = square
        self.location = square.info.location
        self.can_purchase = square.info.can_purchase
        self.is_special_square = not self.can_purchase
