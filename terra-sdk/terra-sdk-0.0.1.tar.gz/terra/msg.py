from terra.util import JsonSerializable
from terra.core import *

from hashlib import sha256

class MsgSend(JsonSerializable):
    def __init__(
        self, amount: List[Coin], from_address: str, to_address: str
    ) -> None:
        """Represent the top level of a MsgSend message."""
        self.type = "bank/MsgSend"
        self.value = MsgSendValue(amount, from_address, to_address)


class MsgSendValue(JsonSerializable):
    def __init__(
        self, amount: List[Coin], from_address: str, to_address: str
    ) -> None:
        """Values of a MsgSend message."""
        self.amount = sorted(amount, key=lambda o: o.denom)
        self.from_address = from_address
        self.to_address = to_address


class MsgMultiSend(JsonSerializable):
    def __init__(self, inputs: List[InOut], outputs: List[InOut]) -> None:
        """Represent the top level of a MsgMultiSend message."""
        self.type = "bank/MsgMultiSend"
        self.value = MsgMultiSendValue(inputs, outputs)


class MsgMultiSendValue(JsonSerializable):
    def __init__(self, inputs: List[InOut], outputs: List[InOut]) -> None:
        """Values of a MsgMultiSend message."""
        self.inputs = inputs
        self.outputs = outputs

class MsgSetWithdrawAddress(JsonSerializable):
    def __init__(self, delegator_address: str, withdraw_address: str) -> None:
        """Represent the top level of a MsgSetWithdrawAddress message."""
        self.type = "distribution/MsgSetWithdrawAddress"
        self.value = MsgSetWithdrawAddressValue(
            delegator_address, withdraw_address
        )

class MsgSetWithdrawAddressValue(JsonSerializable):
    def __init__(self, delegator_address: str, withdraw_address: str) -> None:
        """Values of a MsgSetWithdrawAddress message."""
        self.delegator_address = delegator_address
        self.withdraw_address = withdraw_address

class MsgWithdrawDelegatorReward(JsonSerializable):
    def __init__(self, delegator_address: str, validator_address: str) -> None:
        """Represent the top level of a MsgWithdrawDelegatorReward message."""
        self.type = "distribution/MsgWithdrawDelegatorReward"
        self.value = MsgWithdrawDelegatorRewardValue(
            delegator_address, validator_address
        )

class MsgWithdrawDelegatorRewardValue(JsonSerializable):
    def __init__(self, delegator_address: str, validator_address: str) -> None:
        """Values of a MsgWithdrawDelegatorReward message."""
        self.delegator_address = delegator_address
        self.validator_address = validator_address

class MsgSwap(JsonSerializable):
    def __init__(self, trader: str, offer_coin: Coin, ask_denom: str) -> None:
        """Represent the top level of a MsgSwap message."""
        self.type = "market/MsgSwap"
        self.value = MsgSwapValue(trader, offer_coin, ask_denom)

class MsgSwapValue(JsonSerializable):
    def __init__(self, trader: str, offer_coin: Coin, ask_denom: str) -> None:
        """Values of a MsgSwap message."""
        self.trader = trader
        self.offer_coin = offer_coin
        self.ask_denom = ask_denom

class MsgExchangeRateVote(JsonSerializable):
    def __init__(
        self,
        exchangerate: str,
        salt: str,
        denom: str,
        feeder: str,
        validator: str,
    ) -> None:
        """Represent the top level of a MsgExchangeRateVote message."""
        self.type = "oracle/MsgExchangeRateVote"
        self.value = MsgExchangeRateVoteValue(
            exchangerate, salt, denom, feeder, validator
        )

class MsgExchangeRateVoteValue(JsonSerializable):
    def __init__(
        self,
        exchangerate: str,
        salt: str,
        denom: str,
        feeder: str,
        validator: str,
    ) -> None:
        """Values of a MsgExchangeRateVote message."""
        self.exchangerate = exchangerate
        self.salt = salt
        self.denom = denom
        self.feeder = feeder
        self.validator = validator

class MsgExchangeRatePrevote(JsonSerializable):
    def __init__(
        self,
        exchangerate: str,
        salt: str,
        denom: str,
        feeder: str,
        validator: str,
    ) -> None:
        """Represent the top level of a MsgExchangeRatePrevote message."""
        self.type = "oracle/MsgExchangeRatePrevote"
        self.value = MsgExchangeRatePrevoteValue(
            self._metadata_to_hash(exchangerate, salt, denom, validator),
            denom,
            feeder,
            validator,
        )

    def _metadata_to_hash(
        self, exchangerate: str, salt: str, denom: str, validator: str
    ) -> str:
        """Build the vote hash from metadata.
        The vote hash is the 20 first SHA256 bytes of:
        `salt:exchangerate:denom:voter`
        https://docs.terra.money/specifications/oracle
        """
        sha_hash = sha256(
            f"{salt}:{exchangerate}:{denom}:{validator}".encode()
        )
        return sha_hash.hexdigest()[:40]


class MsgExchangeRatePrevoteValue(JsonSerializable):
    def __init__(
        self,
        hash_: str,  # trailing underscore as `hash` is reserved
        denom: str,
        feeder: str,
        validator: str,
    ) -> None:
        """Values of a MsgExchangeRatePrevote message."""
        self.hash = hash_
        self.denom = denom
        self.feeder = feeder
        self.validator = validator

class MsgExchangeRateVote(JsonSerializable):
    def __init__(
        self,
        exchangerate: str,
        salt: str,
        denom: str,
        feeder: str,
        validator: str,
    ) -> None:
        """Represent the top level of a MsgExchangeRateVote message."""
        self.type = "oracle/MsgExchangeRateVote"
        self.value = MsgExchangeRateVoteValue(
            exchangerate, salt, denom, feeder, validator
        )

class MsgExchangeRateVoteValue(JsonSerializable):
    def __init__(
        self,
        exchangerate: str,
        salt: str,
        denom: str,
        feeder: str,
        validator: str,
    ) -> None:
        """Values of a MsgExchangeRateVote message."""
        self.exchangerate = exchangerate
        self.salt = salt
        self.denom = denom
        self.feeder = feeder
        self.validator = validator

class MsgBeginRedelegate(JsonSerializable):
    def __init__(
        self,
        delegator_address: str,
        validator_src_address: str,
        validator_dst_address: str,
        amount: Coin,
    ) -> None:
        """Represent the top level of a MsgBeginRedelegate message."""
        self.type = "staking/MsgBeginRedelegate"
        self.value = MsgBeginRedelegateValue(
            delegator_address,
            validator_src_address,
            validator_dst_address,
            amount,
        )

class MsgBeginRedelegateValue(JsonSerializable):
    def __init__(
        self,
        delegator_address: str,
        validator_src_address: str,
        validator_dst_address: str,
        amount: Coin,
    ) -> None:
        """Values of a MsgBeginRedelegate message."""
        self.delegator_address = delegator_address
        self.validator_src_address = validator_src_address
        self.validator_dst_address = validator_dst_address
        self.amount = amount

class MsgDelegate(JsonSerializable):
    def __init__(
        self, delegator_address: str, validator_address: str, amount: Coin
    ) -> None:
        """Represent the top level of a MsgDelegate message."""
        self.type = "staking/MsgDelegate"
        self.value = MsgDelegateValue(
            delegator_address, validator_address, amount
        )


class MsgDelegateValue(JsonSerializable):
    def __init__(
        self, delegator_address: str, validator_address: str, amount: Coin
    ) -> None:
        """Values of a MsgDelegate message."""
        self.delegator_address = delegator_address
        self.validator_address = validator_address
        self.amount = amount

class MsgUndelegate(JsonSerializable):
    def __init__(
        self, delegator_address: str, validator_address: str, amount: Coin
    ) -> None:
        """Represent the top level of a MsgUndelegate message."""
        self.type = "staking/MsgUndelegate"
        self.value = MsgUndelegateValue(
            delegator_address, validator_address, amount
        )

class MsgUndelegateValue(JsonSerializable):
    def __init__(
        self, delegator_address: str, validator_address: str, amount: Coin
    ) -> None:
        """Values of a MsgUndelegate message."""
        self.delegator_address = delegator_address
        self.validator_address = validator_address
        self.amount = amount