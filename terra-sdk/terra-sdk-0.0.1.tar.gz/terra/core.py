from typing import List
from terra.util import JsonSerializable

class Coin(JsonSerializable):
    def __init__(self, amount: str, denom: str) -> None:
        """Represent an amount of coin and its denomination."""
        self.denom = denom
        self.amount = amount

class Fee(JsonSerializable):
    def __init__(self, gas: str, amount: List[Coin]) -> None:
        """Represent a transaction fee."""
        self.gas = gas
        self.amount = sorted(amount, key=lambda o: o.denom)

class InOut(JsonSerializable):
    def __init__(self, address: str, coins: List[Coin]) -> None:
        """Represent a input or output of multisend."""
        self.address = address
        self.coins = sorted(coins, key=lambda o: o.denom)

class StdSignMsg(JsonSerializable):
    def __init__(
        self,
        signature: str,
        pub_key_value: str,
        pub_key_type: str = "tendermint/PubKeySecp256k1",
    ) -> None:
        """Values of a StdSignMsg message.

        Note: Abstract help with building the dictionnary by abstracting its
              construction through method parameters.
        """
        self.signature = signature
        self.pub_key = {"type": pub_key_type, "value": pub_key_value}

class StdTx(JsonSerializable):
    def __init__(
        self,
        fee: Fee,
        memo: str = "",
        msg: List[JsonSerializable] = [],
        signatures: List[StdSignMsg] = [],
    ) -> None:
        """Values of a StdTx message."""
        self.fee = fee
        self.memo = memo
        self.msg = msg or []
        self.signatures = signatures or []

Transaction = StdTx

class _SignPayload(JsonSerializable):
    def __init__(
    self,
    fee: Fee,
    memo: str,
    msgs: List[JsonSerializable],
    sequence: str,
    account_number: str,
    chain_id: str,
    ) -> None:
        """StdTx structured as a payload ready to be signed."""
        self.fee = fee
        self.memo = memo
        self.msgs = msgs
        self.sequence = sequence
        self.account_number = account_number
        self.chain_id = chain_id