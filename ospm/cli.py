from generate import generate_password
from clipboard import copy
import click

from ospm.apps import ListApp, DeleteApp
from vault import Vault, get_vault, verify_vault_initialised, is_vault_initialised
from getpass import getpass


@click.group()
def main():
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
    v.add_password(password=password, name=name, account=account)
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
@click.option("--length", "-l", default=16)
def generate(amount, length):
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
    #print("\n".join(f"{i}. {pass_entry.name} | {pass_entry.account} - {pass_entry.password}" for i, pass_entry in enumerate(get_vault(getpass("Master password: ")).passwords)))


@click.command("init")
def init():
    if is_vault_initialised():
        print("Your vault is already initialised!")
    else:
        Vault("vault").save_vault(getpass("Master password: "))
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


main.add_command(change_pass)
main.add_command(add)
main.add_command(delete)
main.add_command(generate)
main.add_command(init)
main.add_command(get_list)

if __name__ == "__main__":
    main()