import collections
from importlib import import_module


def register_renderer(app, id, renderer, force=True):
    """Registers a renderer on the application.

    :param app: The :class:`~flask.Flask` application to register the renderer
                on
    :param id: Internal id-string for the renderer
    :param renderer: Renderer to register
    :param force: Whether or not to overwrite the renderer if a different one
                  is already registered for ``id``
    """
    renderers = app.extensions.setdefault('nav_renderers', {})

    if force:
        renderers[id] = renderer
    else:
        renderers.setdefault(id, renderer)


def get_renderer(app, id):
    """Retrieve a renderer.

    :param app: :class:`~flask.Flask` application to look ``id`` up on
    :param id: Internal renderer id-string to look up
    """
    renderer = app.extensions.get('nav_renderers', {})[id]

    if isinstance(renderer, tuple):
        mod_name, cls_name = renderer
        mod = import_module(mod_name)

        cls = mod
        for name in cls_name.split('.'):
            cls = getattr(cls, name)

        return cls

    return renderer


class ElementRegistry(collections.MutableMapping):
    def __init__(self):
        self._elems = {}

    def __getitem__(self, key):
        item = self._elems[key]

        if callable(item):
            return item()

        return item

    def __setitem__(self, key, value):
        self._elems[key] = value

    def __delitem__(self, key):
        del self._elems[key]

    def __iter__(self):
        for key in self._elems.keys():
            return self[key]

    def __len__(self):
        return len(self._elems)


class Nav(object):
    """The Flask-Nav extension.

    :param app: An optional :class:`~flask.Flask` app to initialize.
    """
    renderers = {}

    def __init__(self, app=None):
        self.elems = ElementRegistry()
        self.renderers = {}

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize an application.

        :param app: A :class:`~flask.Flask` app.
        """
        if not hasattr(app, 'extensions'):
            app.extensions = {}

        app.extensions['nav'] = self
        app.add_template_global(self.elems, 'nav')

        # register some renderers that ship with flask-nav
        simple = (__name__ + '.renderers', 'SimpleRenderer')
        register_renderer(app, 'simple', simple)
        register_renderer(app, None, simple, force=False)

    def register_element(self, id, elem):
        """Register navigational element.

        Registers the given navigational element, making it available using the
        id ``id``.

        This means that inside any template, the registered element will be
        available as ``nav.`` *id*.

        If ``elem`` is callable, any attempt to retrieve it inside the template
        will instead result in ``elem`` being called and the result being
        returned.

        :param id: Id to register element with
        :param elem: Element to register
        """
        self.elems[id] = elem
