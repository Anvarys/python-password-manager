from .generate import generate_password
from clipboard import copy
import click

from .config import Config
from ospm.apps import ListApp, DeleteApp, ConfigApp, ModifyApp
from .vault import Vault, get_vault, verify_vault_initialised, is_vault_initialised
from getpass import getpass


@click.group()
@click.pass_context
def cli(ctx):
    pass


@click.command("add")
@click.argument("name")
@click.argument("account")
@click.option("--password", "-p")
@click.option("--note", "-n")
def add(name, account, password, note):
    verify_vault_initialised()

    if password is None:
        password = generate_password()
        print(f"Copied to clipboard generated password: {password}")
        copy(password)

    mp = getpass("Master password: ")
    v = get_vault(mp)
    v.add_password(password=password, name=name, account=account, note=note)
    v.save_vault(mp)
    del mp, v

    print(f"Added new password for \"{name}\", account \"{account}\"")


@click.command("delete")
@click.option("--pid", "-i")
def delete(pid):
    verify_vault_initialised()

    mp = getpass("Master password: ")
    v = get_vault(mp)

    if pid is None:
        DeleteApp(v.passwords).run()
    else:
        v.delete_password(int(pid))
        v.save_vault(mp)
        del mp, v


@click.command("gen")
@click.argument("amount", default=1)
@click.option("--length", "-l")
def generate(amount, length):
    if length is None:
        length = Config().default_password_length

    if amount == 1:
        password = generate_password(length)
        copy(password)
        print(password)
        print("Copied to clipboard!")
        del password
    else:
        for _ in range(amount):
            print(generate_password(length))


@click.command("list")
def get_list():
    verify_vault_initialised()
    listapp = ListApp(get_vault(getpass("Master password: ")).passwords)
    listapp.run()


@click.command("init")
def init():
    if is_vault_initialised():
        print("Your vault is already initialised!")
    else:
        mp = getpass("Master password: ")
        if not getpass("Confirm master password: ") == mp:
            print("\033[91mError: Master passwords doesn't match\033[0m")
            del mp
            return
        Vault("vault").save_vault(mp)
        print("Vault initialised!")


@click.command("changepass")
def change_pass():
    v = get_vault(getpass("Old master password: "))
    n_mp = getpass("New master password: ")
    if not getpass("Confirm new master password: ") == n_mp:
        print("\033[91mError: New master password doesn't match\033[0m")
        del v, n_mp
        return

    v.save_vault(n_mp)
    del v, n_mp
    print("Master password changed successfully!")


@click.command("config")
def config():
    configApp = ConfigApp()
    configApp.run()
    if configApp.result is None:
        return
    value = input(f"{configApp.result[0]}: ")
    cfg = Config()
    match configApp.result[0]:
        case "default_password_length":
            cfg.default_password_length = int(value)
    cfg.save()
    print("Successfully modified config!")


@click.command("modify")
@click.option("--pid", "-i")
@click.option("--change", "-c")
def modify(pid, change):
    verify_vault_initialised()

    mp = getpass("Master password: ")
    v = get_vault(mp)

    if pid is None:
        password_list_app = ModifyApp(v.passwords)
        password_list_app.run()
        pid = password_list_app.index

    if change is None:
        change = input(f"Modify it's [1] Password [2] Name [3] Account [4] Note: ")

    while change not in ["1", "2", "3", "4"]:
        print("\033[91mError: Please enter one of available options 1-4\033[0m")
        change = input(f"Modify it's [1] Password [2] Name [3] Account [4] Note: ")

    match change:
        case "1":
            new_password = input("Set your new password for this entry (Press Enter to generate): ")
            if new_password is "":
                new_password = generate_password(Config().default_password_length)

            v.passwords[int(pid)].password = new_password
        case "2":
            new_name = input("Set your new name of this entry (ex: example.com): ")
            v.passwords[int(pid)].name = new_name
        case "3":
            new_account = input("Set your new account name for this entry (ex: your.email@example.com): ")
            v.passwords[int(pid)].account = new_account
        case "4":
            new_note = input("Set your new note for this entry (ex: example.com): ")
            v.passwords[int(pid)].note = new_note

    v.save_vault(mp)

    del v, mp, password_list_app

    print("Successfully modified entry!")


cli.add_command(modify)
cli.add_command(change_pass)
cli.add_command(add)
cli.add_command(delete)
cli.add_command(generate)
cli.add_command(init)
cli.add_command(get_list)
cli.add_command(config)

if __name__ == "__main__":
    cli()