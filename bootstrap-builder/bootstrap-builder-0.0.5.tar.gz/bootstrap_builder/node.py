import typing
import textwrap


class HTMLNode(object):

    def __init__(self, tag:str, children:typing.List[typing.Union[str, 'HTMLNode']]=None, *, attrs:dict=None):
        self.tag: str = tag
        if type(children) == str:
            children = [children]
        self.children: typing.List[typing.Union[str, 'HTMLNode']] = children or list()
        self.attrs = attrs or {}
        class_str = self.attrs.pop('class', '')
        try:
            classes = class_str.split(' ')
        except AttributeError:
            classes = class_str
        self['class'] = classes

    def __getitem__(self, key):
        """Gets a given item from the node"""

        v = self.attrs.get(key)
        if v is None:
            if key == "class":
                self.attrs[key] = []
                return self.attrs[key]
            self.attrs[key] = ''
            return ''
        return v

    def __setitem__(self, key, value):
        """Sets a given item for the node"""

        if key == "class":
            if type(value) != list:
                raise ValueError("The class attr in a Node object is a list")
        self.attrs[key] = value

    def get_all_children(self) -> list:
        """Gets all children from the object's children recursively"""

        to_return = [self]
        for child in self.children:
            if type(child) == str:
                to_return.append(child)
                continue
            to_return.extend(child.get_all_children())
        return to_return

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def copy(self) -> 'HTMLNode':
        """Retuns a copy of the current item"""

        return HTMLNode(self.tag, children=[i if type(i) == str else i.copy() for i in self.children], attrs=self.attrs.copy())

    def new_child(self, *args, **kwargs) -> 'HTMLNode':
        """Adds a new child to the object's content"""

        v = HTMLNode(*args, **kwargs)
        self.children.append(v)
        return v

    def add_child(self, child) -> 'HTMLNode':
        """Adds a new child to the object's content"""

        self.children.append(child)

    def __str__(self) -> str:
        return self.to_string()

    def to_string(self, indent:bool=True) -> str:
        """Converts the given object into an HTML string"""

        # Fix the node attrs
        non_list_attrs = {i: o if type(o) == str else ' '.join(o) for i, o in self.attrs.items()}
        fixed_attrs = {i.rstrip('_'): o.replace('"', '\\"') for i, o in non_list_attrs.items()}
        non_tagged = fixed_attrs.pop(None, "")
        attr_string = [f'{i}="{o}"' for i, o in fixed_attrs.items()]

        # Return HTML string
        TAB = "\t" if indent else ""
        ENDL = "\n" if indent else ""
        WRAP = textwrap.indent if indent else lambda string, _: string
        if len(self.children) == 1 and type(self.children[0]) == str:
            return (
                f"<{self.tag}"
                f"{' ' if len(attr_string) > 0 else ''}{' '.join(attr_string)}"
                f"{' ' if len(non_tagged) > 0 else ''}{non_tagged}"
                f">{self.children[0]}</{self.tag}>"
            )
        if len(self.children) > 0:
            return (
                f"<{self.tag}"
                f"{' ' if len(attr_string) > 0 else ''}{' '.join(attr_string)}"
                f"{' ' if len(non_tagged) > 0 else ''}{non_tagged}"
                f">{ENDL}"
                f"{ENDL.join([WRAP(i.to_string(indent=indent), TAB) for i in self.children])}"
                f"{ENDL}</{self.tag}>"
            )
        return (
            f"<{self.tag}"
            f"{' ' if len(attr_string) > 0 else ''}{' '.join(attr_string)}"
            f"{' ' if len(non_tagged) > 0 else ''}{non_tagged}"
            f" />"
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.tag} with {len(self.children)} children and {len(self.attrs)} attrs {id(self)}>"
