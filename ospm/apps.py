from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Label, Button
from vault import PasswordEntry
from textual.containers import Vertical
from textual.screen import ModalScreen

c = {
    "index": "#0a5c7a",
    "password": "#f5bc42",
    "name": "#42c5f5",
    "account": "#4275f5"
}


class ListApp(App):
    CSS = """
    
    """

    def __init__(self, items: list[PasswordEntry], func_on_click=None):
        super().__init__()

        self.func_on_click = func_on_click
        self.items = items

    def compose(self) -> ComposeResult:
        self.list_view = ListView()
        yield self.list_view

    def on_mount(self) -> None:
        self.refresh_list()

    def refresh_list(self) -> None:
        self.list_view.clear()
        for i, item in enumerate(self.items):
            self.list_view.append(ListItem(Label(f"[{c['index']}]{i}.[/{c['index']}] [{c['name']}]{item.name}[/{c['name']}] | [{c['account']}]{item.account}[/{c['account']}] - [{c['password']}]{item.password}[/{c['password']}]")))