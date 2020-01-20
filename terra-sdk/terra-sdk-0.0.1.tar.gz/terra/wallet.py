from typing import Tuple

from pywallet.utils.bip32 import Wallet as BIP32Wallet
from pywallet.utils.keys import PrivateKey, PublicKey

import bech32
import hashlib

from mnemonic import Mnemonic

from terra.core import Transaction

def make_hd_path(account: int = 0, index: int = 0) -> str:
    return f"44'/330'/{account}'/0/{index}"

def address_from_pubkey(pubkey: str) -> str:
    sha = hashlib.sha256()
    rip = hashlib.new("ripemd160")
    sha.update(bytes.fromhex(pubkey))
    rip.update(sha.digest())
    return rip.digest().hex()

def get_bech(prefix: str, payload: str) -> str:
    return bech32.bech32_encode(
        prefix, bech32.convertbits(bytes.fromhex(payload), 8, 5)
    )


class Wallet(object):

    def __init__(self, private_key: str):
        self._pk = PrivateKey.from_hex_key(private_key)
        self._initialize()
    
    def _initialize(self):
        self._private_key = self._pk.get_key().decode()
        pubkey = self._pk.get_public_key()
        pubkey.compressed = True
        self._public_key = pubkey.get_key().decode()
        self._address = address_from_pubkey(self._public_key)

    @classmethod
    def from_seed(cls, seed: bytes, account: int = 0, index: int = 0):
        _wallet = BIP32Wallet.from_master_secret(seed=seed, network='BTC')
        child = _wallet.get_child_for_path(make_hd_path(account, index))
        return cls(child.get_private_key_hex().decode())
    
    @classmethod
    def from_mnemonic(cls, mnemonic: str, account: int = 0, index: int = 0):
        seed = Mnemonic("english").to_seed(mnemonic)
        return cls.from_seed(seed, account, index)

    ##

    @property
    def private_key(self) -> str:
        return self._private_key
    
    @private_key.setter
    def private_key(self, pkey: str):
        self._pk = PrivateKey.from_hex_key(pkey)
        self._initialize()
    
    @property
    def public_key(self) -> str:
        return self._public_key
    
    @property
    def address(self) -> str:
        return get_bech("terra", self._address)
    
    @property
    def validator_address(self) -> str:
        return get_bech("terravaloper", self._address)
    
    ##

    def sign_tx(self, transaction: Transaction):
        pass
        

def generate_random_wallet() -> Tuple[str, Wallet]:
    mnemonic = Mnemonic("english").generate(256)
    wallet = Wallet.from_mnemonic(mnemonic)
    return (mnemonic, wallet)