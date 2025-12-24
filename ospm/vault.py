import pickle
from pathlib import Path
from nacl.secret import SecretBox
import nacl.utils
from argon2.low_level import hash_secret_raw, Type
from platformdirs import user_data_dir

data_dir = Path(user_data_dir("ospm"))


class Vault:
    def __init__(self, name: str):
        self.name = name
        self.filename = name + ".ospm"

    def get_bytes(self) -> bytes:
        return pickle.dumps(self)

    @classmethod
    def from_bytes(cls, data: bytes):
        return pickle.loads(data)

    def save_vault(self, master_password: str):
        with open(data_dir / self.filename, "wb") as f:
            f.write(encrypt(
                derive_key(master_password),
                self.get_bytes()
            ))


def encrypt(key: bytes, data: bytes) -> bytes:
    return SecretBox(key).encrypt(data, nacl.utils.random(SecretBox.NONCE_SIZE))


def decrypt(key: bytes, cipher: bytes) -> bytes:
    return SecretBox(key).decrypt(cipher)


def derive_key(master_password: str) -> bytes:
    return hash_secret_raw(
        secret=master_password.encode(),
        salt=bytes(0x52ab0ba42),
        time_cost=4,
        memory_cost=131072,
        parallelism=2,
        hash_len=32,
        type=Type.ID
    )


def initialise():
    pass  # TODO init process


def get_vault_file_data(vault_name: str) -> bytes:
    if not Path.is_dir(data_dir):
        data_dir.mkdir(parents=True)
        initialise()

    with open(data_dir / vault_name, "rb") as f:
        return f.read()


def get_vault(master_password: str, vault_name: str = "vault.ospm") -> Vault:
    return Vault.from_bytes(
        decrypt(
            derive_key(master_password),
            get_vault_file_data(vault_name)
        )
    )