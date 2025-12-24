from generate import generate_password
from clipboard import copy
import click


@click.group()
def main():
    pass


@click.command("add")
@click.argument("name")
@click.option("--password", "-p")
def add(name, password):
    print(name, password)


@click.command("delete")
@click.option("--id")
def delete(item_id):
    print(item_id)


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


main.add_command(add)
main.add_command(delete)
main.add_command(generate)

if __name__ == "__main__":
    main()