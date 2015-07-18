import pytest

from django.template.loader import get_template, Context
from django.template import VariableDoesNotExist, loader


NATIVE_LOADER_SETTINGS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

COMPILED_LOADER_SETTINGS = (
    ('compiling_loader.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
)


def render(settings, template_name, context):
    loader.template_source_loaders = None
    original = get_template(template_name)
    original_raises = False
    original_result = None

    try:
        original_result = original.render(context)
    except VariableDoesNotExist:
        original_raises = True

    return original_raises, original_result


def render_native(settings, template_name, context):
    settings.TEMPLATE_LOADERS = NATIVE_LOADER_SETTINGS

    return render(settings, template_name, context)


def render_compiled(settings, template_name, context):
    settings.TEMPLATE_LOADERS = COMPILED_LOADER_SETTINGS

    return render(settings, template_name, context)


def assert_rendered_equally(settings, template_name, ctx_dict, expected=None):
    native_raises, native_result = render_native(
        settings, template_name, Context(ctx_dict))

    compiled_raises, compiled_result = render_compiled(
        settings, template_name, Context(ctx_dict))

    assert native_raises == compiled_raises
    assert native_result == compiled_result

    if expected is not None:
        assert native_result == expected


@pytest.mark.parametrize('template_name', [
    'empty.html',
    'simple.html',
    'var.html',
    'var_default.html',
    'var_default_var.html',
    'var_filters.html',
])
def test_no_context(settings, template_name):
    assert_rendered_equally(settings, template_name, {})


@pytest.mark.parametrize('template_name,ctx_dict', [
    ('var.html', {'var': ''}),
    ('var.html', {'var': 'test'}),
    ('var_default.html', {'var': ''}),
    ('var_default.html', {'var': 'test'}),
    ('var_default_var.html', {'var': ''}),
    ('var_default_var.html', {'var': '', 'other': ''}),
    ('var_default_var.html', {'var': '', 'other': 'other'}),
    ('var_default_var.html', {'var': 'test'}),
    ('var_default_var.html', {'var': 'test', 'other': ''}),
    ('var_default_var.html', {'var': 'test', 'other': 'other'}),
    ('var_filters.html', {'var': ''}),
    ('var_filters.html', {'var': 'test'}),
])
def test_var_filter_lookup(settings, template_name, ctx_dict):
    assert_rendered_equally(settings, template_name, ctx_dict)


@pytest.mark.parametrize('template_name,ctx_dict', [
    ('var.html', {'var': '<html>'}),
    ('var_default_html.html', {'var': '<html>'}),
    ('var_default_var.html', {'var': '<html>'}),
    ('var_filters.html', {'var': '<html>'}),
])
def test_var_escaping(settings, template_name, ctx_dict):
    assert_rendered_equally(settings, template_name, ctx_dict)


@pytest.mark.parametrize('template_name,ctx_dict', [
    ('var.html', {'var': [1, 2, 3]}),
    ('var_default.html', {'var': []}),
    ('var_filters.html', {'var': [1, 2, 3]}),
])
def test_other_types(settings, template_name, ctx_dict):
    assert_rendered_equally(settings, template_name, ctx_dict)


def test_fallback(settings):
    assert_rendered_equally(
        settings,
        'block_upper.html',
        {},
        expected='\nSOME UPPERCASED TEXT\n'
    )