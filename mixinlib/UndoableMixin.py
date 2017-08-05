class UndoableMixin:
    class UndoableTransaction:

        def __init__(self, func, undo_func, args, undo_args):
            if not callable(func) or not callable(undo_func):
                raise ValueError("UndoableTransaction")
            self.func = func
            self.args = args
            self.undo_func = undo_func
            self.undo_args = undo_args

        def apply(self):
            return self.func(*self.args)

        def revert(self):
            return self.undo_func(*self.undo_args)

        def __repr__(self):
            return f'{type(self).__name__}({self.func.__name__},{self.undo_func.__name__},{self.args},{self.undo_args})'

    def __init__(self, *args):
        self._undo_stack = []
        self._redo_stack = []
        super().__init__(*args)

    def can_undo(self):
        return bool(self._undo_stack)

    def can_redo(self):
        return bool(self._redo_stack)

    def undo(self):
        UndoableMixin._apply_transaction(self._undo_stack, self._redo_stack, self.UndoableTransaction.revert)

    def redo(self):
        UndoableMixin._apply_transaction(self._redo_stack, self._undo_stack, self.UndoableTransaction.apply)

    @staticmethod
    def _apply_transaction(pop_stack, push_stack, action):
        if not pop_stack:
            return
        return_val = action(pop_stack[-1])
        push_stack.append(pop_stack.pop())
        return return_val


def undoable(undo_args_transform=lambda *args: args, undo_func=None):
    def decorator(method):
        undo_method = undo_func if undo_func else method

        def undoable_method(*args):
            self = args[0]
            undo_args = undo_args_transform(*args)
            transaction = UndoableMixin.UndoableTransaction(method, undo_method, args, undo_args)
            return_val = method(*args)
            self._undo_stack.append(transaction)
            self._redo_stack.clear()
            return return_val

        return undoable_method

    return decorator
