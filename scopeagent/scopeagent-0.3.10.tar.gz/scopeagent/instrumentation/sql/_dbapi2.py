# Copyright (c) 2015-2017 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from __future__ import absolute_import

import opentracing
import wrapt
from opentracing.ext import tags as ext_tags

from .local_span import func_span, start_child_span

# Utils for instrumenting DB API v2 compatible drivers.
# PEP-249 - https://www.python.org/dev/peps/pep-0249/

_BEGIN = 'begin-trans'
_COMMIT = 'commit'
_ROLLBACK = 'rollback'
_TRANS_TAGS = [_BEGIN, _COMMIT, _ROLLBACK]

NO_ARG = object()


def db_span(sql_statement,
            module_name,
            sql_parameters=None,
            connect_params=None,
            cursor_params=None,
            tracer=None):
    tracer = tracer or opentracing.tracer
    span = tracer.active_span

    statement = sql_statement.strip()
    add_sql_tag = True
    if sql_statement in _TRANS_TAGS:
        operation = sql_statement
        add_sql_tag = False
    else:
        space_idx = statement.find(' ')
        if space_idx == -1:
            operation = ''  # unrecognized format of the query
        else:
            operation = statement[0:space_idx]

    tags = {
        ext_tags.DATABASE_TYPE: 'sql',
        ext_tags.SPAN_KIND: ext_tags.SPAN_KIND_RPC_CLIENT,
    }
    if add_sql_tag:
        tags[ext_tags.DATABASE_STATEMENT] = statement

    # Non-standard tags
    if sql_parameters:
        tags['db.params'] = sql_parameters
    if connect_params:
        tags['db.conn'] = connect_params
        # Extract standard tags
        kwargs = connect_params[1]
        tags[ext_tags.DATABASE_INSTANCE] = kwargs.get('database')
        tags[ext_tags.DATABASE_USER] = kwargs.get('user')
        tags[ext_tags.PEER_HOSTNAME] = kwargs.get('host')
        tags[ext_tags.PEER_PORT] = kwargs.get('port')
    if cursor_params:
        tags['db.cursor'] = cursor_params

    return start_child_span(
        operation_name='%s:%s' % (module_name, operation),
        parent=span, tags=tags, tracer=tracer
    )


class ConnectionFactory(object):
    """
    Wraps connect_func of the DB API v2 module by creating a wrapper object
    for the actual connection.
    """

    def __init__(self, connect_func, module_name, conn_wrapper_ctor=None, tracer=None):
        self._tracer = tracer
        self._connect_func = connect_func
        self._module_name = module_name
        if hasattr(connect_func, '__name__'):
            self._connect_func_name = '%s:%s' % (module_name,
                                                 connect_func.__name__)
        else:
            self._connect_func_name = '%s:%s' % (module_name, connect_func)
        self._wrapper_ctor = conn_wrapper_ctor \
            if conn_wrapper_ctor is not None else ConnectionWrapper

    def __call__(self, *args, **kwargs):
        safe_kwargs = kwargs
        if 'passwd' in kwargs or 'password' in kwargs or 'conv' in kwargs:
            safe_kwargs = dict(kwargs)
            if 'passwd' in safe_kwargs:
                del safe_kwargs['passwd']
            if 'password' in safe_kwargs:
                del safe_kwargs['password']
            if 'conv' in safe_kwargs:  # don't log conversion functions
                del safe_kwargs['conv']
        connect_params = (args, safe_kwargs) if args or safe_kwargs else None
        with func_span(self._connect_func_name, tracer=self._tracer):
            return self._wrapper_ctor(
                connection=self._connect_func(*args, **kwargs),
                module_name=self._module_name,
                connect_params=connect_params,
                tracer=self._tracer)


class ConnectionWrapper(wrapt.ObjectProxy):
    __slots__ = ('_module_name', '_connect_params', '_tracer')

    def __init__(self, connection, module_name, connect_params, tracer):
        super(ConnectionWrapper, self).__init__(wrapped=connection)
        self._module_name = module_name
        self._connect_params = connect_params
        self._tracer = tracer

    def cursor(self, *args, **kwargs):
        return CursorWrapper(
            cursor=self.__wrapped__.cursor(*args, **kwargs),
            module_name=self._module_name,
            connect_params=self._connect_params,
            cursor_params=(args, kwargs) if args or kwargs else None,
            tracer=self._tracer
        )

    def begin(self):
        with db_span(sql_statement=_BEGIN, module_name=self._module_name, tracer=self._tracer):
            return self.__wrapped__.begin()

    def commit(self):
        with db_span(sql_statement=_COMMIT, module_name=self._module_name, tracer=self._tracer):
            return self.__wrapped__.commit()

    def rollback(self):
        with db_span(sql_statement=_ROLLBACK, module_name=self._module_name, tracer=self._tracer):
            return self.__wrapped__.rollback()


class ContextManagerConnectionWrapper(ConnectionWrapper):
    """
    Extends ConnectionWrapper by implementing `__enter__` and `__exit__`
    methods of the context manager API, for connections that can be used
    in as context managers to control the transactions, e.g.

    .. code-block:: python

        with MySQLdb.connect(...) as cursor:
            cursor.execute(...)
    """

    def __init__(self, connection, module_name, connect_params, tracer):
        super(ContextManagerConnectionWrapper, self).__init__(
            connection=connection,
            module_name=module_name,
            connect_params=connect_params,
            tracer=tracer
        )

    def __getattr__(self, name):
        # Tip suggested here:
        # https://gist.github.com/mjallday/3d4c92e7e6805af1e024.
        if name == '_sqla_unwrap':
            return self.__wrapped__
        return super(ContextManagerConnectionWrapper, self).__getattr__(name)

    def __enter__(self):
        with func_span('%s:begin_transaction' % self._module_name, self._tracer):
            cursor = self.__wrapped__.__enter__()

        return CursorWrapper(cursor=cursor,
                             module_name=self._module_name,
                             connect_params=self._connect_params)

    def __exit__(self, exc, value, tb):
        outcome = _COMMIT if exc is None else _ROLLBACK
        with db_span(sql_statement=outcome, module_name=self._module_name, tracer=self._tracer):
            return self.__wrapped__.__exit__(exc, value, tb)


class CursorWrapper(wrapt.ObjectProxy):
    __slots__ = ('_module_name', '_connect_params', '_cursor_params', '_tracer')

    def __init__(self, cursor, module_name,
                 connect_params=None, cursor_params=None, tracer=None):
        super(CursorWrapper, self).__init__(wrapped=cursor)
        self._module_name = module_name
        self._connect_params = connect_params
        self._cursor_params = cursor_params
        self._tracer = tracer
        # We could also start a span now and then override close() to capture
        # the life time of the cursor

    def execute(self, sql, params=NO_ARG):
        with db_span(sql_statement=sql,
                     sql_parameters=params if params is not NO_ARG else None,
                     module_name=self._module_name,
                     connect_params=self._connect_params,
                     cursor_params=self._cursor_params,
                     tracer=self._tracer):
            if params is NO_ARG:
                return self.__wrapped__.execute(sql)
            else:
                return self.__wrapped__.execute(sql, params)

    def executemany(self, sql, seq_of_parameters):
        with db_span(sql_statement=sql, sql_parameters=seq_of_parameters,
                     module_name=self._module_name,
                     connect_params=self._connect_params,
                     cursor_params=self._cursor_params,
                     tracer=self._tracer):
            return self.__wrapped__.executemany(sql, seq_of_parameters)

    def callproc(self, proc_name, params=NO_ARG):
        with db_span(sql_statement='sproc:%s' % proc_name,
                     sql_parameters=params if params is not NO_ARG else None,
                     module_name=self._module_name,
                     connect_params=self._connect_params,
                     cursor_params=self._cursor_params,
                     tracer=self._tracer):
            if params is NO_ARG:
                return self.__wrapped__.callproc(proc_name)
            else:
                return self.__wrapped__.callproc(proc_name, params)
