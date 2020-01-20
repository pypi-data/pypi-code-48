import typing

from bootstrap_builder.node import HTMLNode


class BootstrapNode(HTMLNode):

    def _new_child_with_class(self, tag, class_name, children, attrs):
        attrs = attrs or {}
        v = self.new_child(tag, children=children, attrs=attrs)
        v['class'].append(class_name)
        return v

    def copy(self) -> 'BootstrapNode':
        """Retuns a copy of the current item"""

        return BootstrapNode(self.tag, children=[i if type(i) == str else i.copy() for i in self.children], attrs=self.attrs.copy())

    def new_child(self, *args, **kwargs) -> 'BootstrapNode':
        """Adds a new child to the object's content"""

        v = BootstrapNode(*args, **kwargs)
        self.children.append(v)
        return v

    def new_row(self, children:list=None, *, attrs:dict=None) -> 'BootstrapNode':
        return self._new_child_with_class("div", "row", children, attrs)

    def new_container(self, children:list=None, *, attrs:dict=None) -> 'BootstrapNode':
        return self._new_child_with_class("div", "container", children, attrs)

    def new_column(self, children:list=None, *, attrs:dict=None) -> 'BootstrapNode':
        return self._new_child_with_class("div", "col", children, attrs)

    def new_card_columns(self, children:list=None, *, attrs:dict=None) -> 'BootstrapNode':
        return self._new_child_with_class("div", "card-columns", children, attrs)

    def new_card_deck(self, children:list=None, *, attrs:dict=None) -> 'BootstrapNode':
        return self._new_child_with_class("div", "card-deck", children, attrs)

    def new_card_group(self, children:list=None, *, attrs:dict=None) -> 'BootstrapNode':
        return self._new_child_with_class("div", "card-group", children, attrs)

    def new_card(self, children:list=None, *, attrs:dict=None) -> 'BootstrapNode':
        return self._new_child_with_class("div", "card", children, attrs)

    def new_jumbotron(self, children:list=None, *, attrs:dict=None) -> 'BootstrapNode':
        return self._new_child_with_class("div", "jumbotron", children, attrs)

    def new_navbar(self, children:list=None, *, attrs:dict=None) -> 'BootstrapNode':
        return self._new_child_with_class("nav", "navbar", children, attrs)

    def new_navbar_nav(self, children:list=None, *, attrs:dict=None) -> 'BootstrapNode':
        return self._new_child_with_class("ul", "navbar-nav", children, attrs)

    def new_navbar_nav_item(self, children:list=None, *, attrs:dict=None) -> 'BootstrapNode':
        return self._new_child_with_class("li", "nav-item", children, attrs)
