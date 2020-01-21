"""Alternative implementation of pytest-bdd scenario and steps wrappers.
This decorators can wrap class methods.
"""
import inspect
import sys
import textwrap
from enum import Enum
from functools import partial

import pytest
from _pytest.fixtures import getfixturemarker
from _pytest.python import Class
from pytest_bdd import exceptions
from pytest_bdd.feature import Feature
from pytest_bdd.parsers import get_parser, StepParser, parse
from pytest_bdd.scenario import get_features_base_dir, get_strict_gherkin
from pytest_bdd.steps import get_caller_module

__metaclass__ = type  # pylint: disable=invalid-name,unused-argument
IS_PYTHON2 = sys.version.startswith('2.')


def get_args_spec(func):  # pragma: nocover
    """
    :type func: callable
    :rtype: list[str]
    """
    is_partial = hasattr(func, 'func') and hasattr(func, 'args')

    args = list()
    if IS_PYTHON2 and not is_partial:
        # pylint: disable=deprecated-method
        args.extend(inspect.getargspec(func).args)
    elif IS_PYTHON2 and is_partial:
        # pylint: disable=deprecated-method
        args.extend(inspect.getargspec(func.func).args[len(func.args):])
    else:
        args.extend(
            inspect.getfullargspec(func).args  # pylint: disable=no-member
        )
    return args


class StepMarkName(Enum):
    """Available BDD steps mark names.
    """
    GIVEN = "bdd_given"
    WHEN = "bdd_when"
    THEN = "bdd_then"

    @classmethod
    def is_bdd_marker(cls, marker):
        """
        :type marker: _pytest.mark.Mark
        :rtype: bool
        """
        try:
            return bool(StepMarkName(marker.name))
        except ValueError:
            return False


def fixture_name(fixture):
    """
    :param fixture: Callable
    :rtype: str | None
    """
    marker = getfixturemarker(fixture)
    return marker and (marker.name or fixture.__name__)


def _python2_fixtures(fixtures):  # pragma: nocover
    context = {"pytest": pytest}
    context.update(fixtures)

    class_definition = textwrap.dedent(
        """
        class Fixtures:
            pass
        """
    )
    fixture_definitions = [
        textwrap.dedent(
            """
            @pytest.fixture(name="{name}")
            def _get_fixture_{name}(self):
                return {name}
            """
        ).format(name=name).replace("\n", "\n    ")
        for name in fixtures
    ]

    code = class_definition + "\n".join(fixture_definitions)
    exec(code, context)  # pylint: disable=exec-used
    return context["Fixtures"]


def _python3_fixtures(fixtures):  # pragma: nocover
    return type(
        "Fixtures",
        (object,),
        {
            # pylint: disable=cell-var-from-loop
            k: pytest.fixture(name=k)(lambda: v)
            for k, v in fixtures.items()
        }
    )


def add_fixtures(request, **fixtures):
    """
    :type request: _pytest.fixtures.FixtureRequest
    :param fixtures: kwargs with fixtures to add to request fixture manager
    :type fixtures: dict
    """
    fixtures = (
        _python2_fixtures(fixtures)
        if IS_PYTHON2
        else _python3_fixtures(fixtures)
    )
    manager = getattr(request, "_fixturemanager")
    manager.pytest_plugin_registered(fixtures)


class Step:
    """
    Object representing pytest step function.
    """
    def __init__(self, pattern, parent, func, item_name):
        """
        :param pattern: step pattern
        :type pattern: StepParser | str
        :type item_name: str
        :rtype parent: object
        :rtype func: Callable
        """
        self._pattern = (
            pattern
            if isinstance(pattern, StepParser)
            else parse(pattern)
        )
        self._parser = get_parser(self._pattern)
        self._parent = parent
        self._callable = func
        self._item_name = item_name

    def is_matching(self, name):
        """
        :param name: name of step from bdd feature file
        :type name: str
        :rtype: bool
        """
        return self._parser.is_matching(name)

    def same_parent(self, parent):
        """
        Check if same object or StepDef.parent is class for passed parent
        :type parent: object | type
        :rtype: bool
        """
        is_instance_of_step_parent = (
            inspect.isclass(parent)
            and isinstance(self._parent, parent)
        )
        return is_instance_of_step_parent or parent == self._parent

    def to_callable(self, name, request, parent):
        """
        :param name: step from bdd feature file
        :type name: str
        :type request: _pytest.fixtures.FixtureRequest
        :type parent: _pytest.python.Instance
        :return: Callable
        """

        def call():
            add_fixtures(request, **self._parser.parse_arguments(name))

            func = (
                self._fixture_call(name, request)
                or self._method_call(parent, request)
                or self._callable
            )
            args = {
                arg: request.getfixturevalue(arg)
                for arg in get_args_spec(func)
            }
            return func(**args)

        return call

    def _fixture_call(self, name, request):
        """
        :param name: name of step from bdd feature file
        :type name: str
        :type request: _pytest.fixtures.FixtureRequest
        :rtype: Callable | None
        """
        name = fixture_name(self._callable)
        return name and (lambda: request.getfixturevalue(name))

    def _method_call(self, parent, request):
        """
        :type parent: _pytest.python.Instance
        :type request: _pytest.fixtures.FixtureRequest
        :rtype: Callable | None
        """
        if isinstance(parent, Class):
            return partial(self._callable, request.instance)
        return None


def parents_stack(parent):
    """
    :type parent: _pytest.python.Instance
    :rtype: list[_pytest.python.Instance]
    """
    if not hasattr(parent, "obj"):
        return []
    return [parent] + parents_stack(parent.parent)


class BDDListener:
    """
    pytest-bdd-wrappers hook listener
    """
    def __init__(self, config):
        """
        :type config: _pytest.config.Config
        """
        self.config = config
        self.scenarios = {}
        self.steps = []

    def pytest_pycollect_makeitem(self, collector, name, obj):
        """
        :type collector: _pytest.python.PyCollector
        :type name: str
        :type obj: object
        """
        pytestmark = getattr(obj, "pytestmark", [])
        if not isinstance(pytestmark, list):
            return
        markers = [m for m in pytestmark if StepMarkName.is_bdd_marker(m)]
        for mark in markers:
            self.steps.append(
                Step(mark.kwargs["name"], collector.obj, obj, name)
            )

    def pytest_pyfunc_call(self, pyfuncitem):
        """
        :type pyfuncitem: _pytest.python.Function
        """
        request = getattr(pyfuncitem, "_request")
        scenario_markers = [
            marker for marker in pyfuncitem.own_markers
            if marker.name == "scenario"
        ]
        if not scenario_markers:
            return
        tested_scenario = scenario_markers[0].kwargs["scenario"]

        for step in tested_scenario.steps:
            step_func = self._find_step(step.name, request, pyfuncitem.parent)
            if not step_func:
                raise exceptions.StepDefinitionNotFoundError(
                    "{} {}".format(step.type, step.name)
                )
            step_func()

    def _find_step(self, name, request, scenario_parent):
        """
        :param name: step from bdd feature file
        :type name: str
        :type request: _pytest.fixtures.FixtureRequest
        :type scenario_parent: _pytest.python.Instance
        :rtype: Callable | None
        """
        steps = [s for s in self.steps if s.is_matching(name)]
        parents = parents_stack(scenario_parent)
        mapped_distance = {
            parents.index(parent): step.to_callable(name, request, parent)
            for step in steps
            for parent in parents
            if step.same_parent(parent.obj)  # pylint: disable=no-member
        }
        _, func = min(
            list(mapped_distance.items()) + [(9999, None)],
            key=lambda e: e[0]
        )
        return func


def pytest_configure(config):
    """
    :type config: _pytest.config.Config
    """
    config.pluginmanager.register(BDDListener(config))


def _wrap_function_with_additional_arguments(func, arguments):
    """
    :param func: function to wrap with additional arguments
    :param arguments: arguments to add if they are not already received in func
    :type arguments: set[str]
    :rtype: callable
    """
    args = get_args_spec(func)
    additional_args = list(arguments - set(args))
    call_args = args + additional_args
    wrapper_body = textwrap.dedent(
        """
        def _call_wrapper_{name}({args}):
            return func({call_args})
        """.format(
            name=func.__name__,
            args=', '.join(call_args),
            call_args=', '.join('{0}={0}'.format(a) for a in args)
        )
    )
    context = {"func": func}
    exec(wrapper_body, context)  # pylint: disable=exec-used
    return context["_call_wrapper_{}".format(func.__name__)]


def scenario(
        feature_name,
        scenario_name,
        encoding="utf-8",
        features_base_dir=None,
        example_converters=None
):
    """
    Scenario decorator.

    :param str feature_name: Feature file name.
        Absolute or relative to the configured feature base path.
    :param str scenario_name: Scenario name.
    :param str encoding: Feature file encoding.
    :param str | None features_base_dir: path to directory with feature
    :param example_converters: Dict of example value converting functions
    :type example_converters: dict[ValueName, Callable[[Value], Converted]]
    """
    if features_base_dir is None:
        features_base_dir = get_features_base_dir(get_caller_module())
    feature = Feature.get_feature(
        features_base_dir,
        feature_name,
        encoding=encoding,
        strict_gherkin=get_strict_gherkin(),
    )

    if scenario_name not in feature.scenarios:
        msg = (
            u'Scenario "{scenario_name}" in feature "{feature_name}"'
            u" in {feature_filename} is not found."
        ).format(
            scenario_name=scenario_name,
            feature_name=feature.name or "[Empty]",
            feature_filename=feature.filename,
        )
        raise exceptions.ScenarioNotFound(msg)

    tested_scenario = feature.scenarios[scenario_name]
    tested_scenario.example_converters = example_converters
    tested_scenario.validate()

    def wrap(func):
        example_params = tested_scenario.get_example_params()

        if example_params:
            func = _wrap_function_with_additional_arguments(
                func, example_params,
            )

            for params in tested_scenario.get_params():
                if params:
                    pytest.mark.parametrize(*params)(func)

        pytest.mark.scenario(scenario=tested_scenario)(func)
        return func

    return wrap


def _step_mark(step_mark, name):
    """
    Decorator for bdd steps.

    :type step_mark: StepMarkName
    :param name: Name of step from feature file
    :type name: str
    :return: Wrapper for step function
    """

    def wrap(func):
        mark = getattr(pytest.mark, step_mark.value)
        return mark(name=name, step=step_mark)(func)

    return wrap


def given(name, fixture=None):
    """
    :param name: Name of step from feature file
    :type name: str
    :param fixture: alternative name for fixture
    :type fixture: str | None
    :return: Wrapper for given function
    """

    def wrap(func):
        if not hasattr(func, "_pytestfixturefunction"):
            func = pytest.fixture(name=fixture)(func)
        return _step_mark(StepMarkName.GIVEN, name)(func)

    return wrap


when = partial(_step_mark, StepMarkName.WHEN)  # pylint: disable=invalid-name
then = partial(_step_mark, StepMarkName.THEN)  # pylint: disable=invalid-name


__all__ = ["scenario", "given", "when", "then"]
