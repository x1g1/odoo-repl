from __future__ import absolute_import
from __future__ import print_function

import pdb
import pprint
import sys
import types

import odoo_repl

from odoo_repl.imports import PY3, abc, odoo, t

__all__ = ("OPdb", "set_trace", "post_mortem", "pm")


class _ChainMap(abc.MutableMapping):
    def __init__(self, *mappings):
        # type: (t.Mapping) -> None
        self.mappings = mappings

    def __getitem__(self, key):
        # type: (object) -> object
        for mapping in self.mappings:
            if key in mapping:
                return mapping[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        # type: (object, object) -> None
        for mapping in self.mappings:
            if isinstance(mapping, abc.MutableMapping):
                mapping[key] = value
                return
        raise TypeError("No mutable mappings in ChainMap")

    def __delitem__(self, key):
        # type: (object) -> None
        for mapping in self.mappings:
            if key in mapping:
                if not isinstance(mapping, abc.MutableMapping):
                    raise TypeError("{!r} is immutable".format(mapping))
                del mapping[key]
                return
        raise KeyError(key)

    def _keys(self):
        # type: () -> t.Set[object]
        return {key for mapping in self.mappings for key in mapping}

    def __iter__(self):
        # type: () -> t.Iterator[object]
        return iter(self._keys())

    def __len__(self):
        # type: () -> int
        return len(self._keys())


class OPdb(pdb.Pdb, object):
    def __init__(
        self,
        completekey="tab",  # type: str
        stdin=None,  # type: t.Optional[t.IO[str]]
        stdout=None,  # type: t.Optional[t.IO[str]]
        skip=("odoo.api", "openerp.api"),  # type: t.Optional[t.Iterable[str]]
    ):
        # type: (...) -> None
        super(OPdb, self).__init__(
            completekey=completekey, stdin=stdin, stdout=stdout, skip=skip
        )
        self.repl_namespace = {}  # type: t.Dict[t.Text, t.Any]
        self._real_curframe_locals = None  # type: t.Optional[t.Mapping]
        self.env = None  # type: t.Optional[odoo.api.Environment]
        if not hasattr(self, "curframe_locals"):
            self.curframe_locals = {}

    def displayhook(self, obj):
        # type: (object) -> None
        if obj is not None:
            if PY3:
                self.message(odoo_repl.odoo_repr(obj))
            else:
                print(odoo_repl.odoo_repr(obj), file=self.stdout)

    def setup(self, f, tb):
        # type: (t.Optional[types.FrameType], t.Optional[types.TracebackType]) -> None
        super(OPdb, self).setup(f, tb)
        f_self = self.curframe_locals.get("self", None)
        f_cr = self.curframe_locals.get("cr", None)
        if hasattr(f_self, "env") and isinstance(f_self.env, odoo.api.Environment):
            self.env, ns = odoo_repl.create_namespace(f_self.env)
        elif isinstance(f_cr, odoo.sql_db.Cursor):
            self.env, ns = odoo_repl.create_namespace(f_cr)
        else:
            self.env, ns = odoo_repl.create_namespace(None)
        self.repl_namespace.update(ns)

    def _setup_framelocals(self):
        # type: () -> None
        # TODO: this only works in py2 because unittest2 adds ChainMap
        # stop depending on ChainMap? Use own implementation?
        if not isinstance(self.curframe_locals, _ChainMap):
            self._real_curframe_locals = self.curframe_locals
            self.curframe_locals = _ChainMap(self.curframe_locals, self.repl_namespace)

    def precmd(self, line):
        # type: (str) -> str
        self._setup_framelocals()
        return super(OPdb, self).precmd(line)

    def do_sql(self, arg):
        # type: (str) -> None
        if self.env is None:
            raise TypeError("Uninitialized debugger")
        try:
            with odoo_repl.savepoint(self.env.cr):
                self.env.cr.execute(arg)
                pprint.pprint(self.env.cr.fetchall())
        except Exception as err:
            # TODO: this might also be printed by the logging
            print(err)


def set_trace():
    # type: () -> None
    OPdb().set_trace(sys._getframe().f_back)


def post_mortem(traceback=None):
    # type: (t.Optional[types.TracebackType]) -> None
    if traceback is None:
        traceback = sys.exc_info()[2]
        if traceback is None:
            raise ValueError(
                "A valid traceback must be passed if no exception is being handled"
            )
    debugger = OPdb()
    debugger.reset()
    debugger.interaction(None, traceback)


def pm():
    # type: () -> None
    post_mortem(sys.last_traceback)
