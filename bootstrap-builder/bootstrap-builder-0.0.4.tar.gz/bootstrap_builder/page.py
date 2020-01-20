import typing

# from bootstrap.node import HTMLNode
from bootstrap_builder.bootstrap_node import BootstrapNode


class HTMLPage(BootstrapNode):

    defaults = {}

    def __init__(self, *, tag:str="body", title:str=None, favicon:str=None, stylesheets:typing.List[str]=None, javascript:typing.List[str]=None, priority_javascript:typing.List[str]=None, shortcuts:dict=None, **kwargs):
        super().__init__(tag, **kwargs)
        self.title = title or ""
        self.favicon = favicon or ""
        self.stylesheets = stylesheets or list()
        self.javascript = javascript or list()
        self.priority_javascript = priority_javascript or list()
        self.shortcuts = shortcuts or {}  # Set shortcuts to a given node

    def set_as_default(self, name:str) -> None:
        """Sets the current instance of the page as the default to be loaded"""

        self.defaults[name] = self.copy()

    @classmethod
    def load_from_default(cls, name:str) -> None:
        """Sets the current instance of the page as the default to be loaded"""

        return cls.defaults.get(name).copy()

    def copy(self) -> BootstrapNode:
        """Retuns a copy of the current item"""

        # Copy the current shortcuts
        reversed_shortcuts = {o: i for i, o in self.shortcuts.items()}
        new_shortcuts = {}
        new_children = []

        # Copy the children
        for child in self.children:
            new_children.append(child.copy())

        # Try and find new shortcut locations
        unique_children = []
        unique_copies = []
        for original, copy in zip(self.children, new_children):
            unique_children.extend(original.get_all_children())
            unique_copies.extend(copy.get_all_children())
        for original, copy in zip(unique_children, unique_copies):
            if original in reversed_shortcuts:
                new_shortcuts[reversed_shortcuts[original]] = copy

        # Return class
        return self.__class__(
            title=self.title,
            favicon=self.favicon,
            stylesheets=self.stylesheets.copy(),
            javascript=self.javascript.copy(),
            tag=self.tag,
            children=new_children,
            attrs=self.attrs.copy(),
            shortcuts=new_shortcuts,
        )

    def new_child(self, *args, **kwargs) -> 'HTMLNode':
        """Adds a new child to the object's content"""

        v = BootstrapNode(*args, **kwargs)
        self.children.append(v)
        return v

    def __str__(self) -> str:
        return self.to_string()

    def to_string(self, *, indent:bool=True) -> str:
        """Converts the page nicely into HTML"""

        # Add our bootstrap external libs as necessary
        stylesheets = self.stylesheets.copy()
        javascript = self.javascript.copy()
        stylesheets.append({
            "href": "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css",
            "integrity": "sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh",
            "crossorigin": "anonymous",
        })
        javascript.append({
            "src": "https://code.jquery.com/jquery-3.4.1.slim.min.js",
            "integrity": "sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n",
            "crossorigin": "anonymous",
        })
        javascript.append({
            "src": "https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js",
            "integrity": "sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo",
            "crossorigin": "anonymous",
        })
        javascript.append({
            "src": "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js",
            "integrity": "sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6",
            "crossorigin": "anonymous",
        })

        # Create the head
        html = BootstrapNode("html")
        with html.new_child("head") as head:
            head.new_child("meta", attrs={"charset": "utf-8"})
            head.new_child("meta", attrs={"name": "viewport", "content": "width=device-width, initial-scale=1"})
            if self.title:
                head.new_child("title", self.title)
            if self.favicon:
                head.new_child("link", attrs={"rel": "icon", "href": self.favicon, "type": "image/x-icon"})
            for sheet in stylesheets:
                if type(sheet) == dict:
                    head.new_child("link", attrs={"rel": "stylesheet", **sheet})
                else:
                    head.new_child("link", attrs={"rel": "stylesheet", "href": sheet})
            for script in self.priority_javascript:
                if type(script) == dict:
                    head.new_child("script", "", attrs={**script})
                else:
                    head.new_child("script", "", attrs={"src": script})

        # Throw our js onto the end of the body
        copy = super().copy()
        for script in javascript:
            if type(script) == dict:
                copy.new_child("script", "", attrs={**script})
            else:
                copy.new_child("script", "", attrs={"src": script})
        html.add_child(copy)

        # Return HTML
        if indent:
            return '<!DOCTYPE html>\n' + html.to_string(indent=indent) + '\n'
        return '<!DOCTYPE html>' + html.to_string(indent=indent) + '\n'
