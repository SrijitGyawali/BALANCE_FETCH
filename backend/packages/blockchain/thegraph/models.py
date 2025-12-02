"""
Data models for The Graph API responses.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ChainInfo(BaseModel):
    """Chain information model."""

    chain_id: str = Field(..., description="Chain ID as string")
    name: str = Field(..., description="Chain name")
    native_symbol: str = Field(..., description="Native token symbol")
    network_name: str = Field(..., description="The Graph API network name")


class NativeBalance(BaseModel):
    """Native token balance model."""

    chain_id: str = Field(..., description="Chain ID")
    chain_name: str = Field(..., description="Chain name")
    balance: str = Field(..., description="Balance in smallest unit (wei)")
    symbol: str = Field(..., description="Token symbol")
    price_usd: Optional[str] = Field(default="0", description="Price in USD")


class TokenBalance(BaseModel):
    """ERC-20 token balance model."""

    token_address: str = Field(..., description="Token contract address")
    token_name: str = Field(..., description="Token name")
    token_symbol: str = Field(..., description="Token symbol")
    token_quantity: str = Field(..., description="Raw token quantity")
    token_divisor: str = Field(..., description="Token divisor (10^decimals)")
    token_price_usd: str = Field(default="0", description="Token price in USD")
    chain_id: Optional[str] = Field(default=None, description="Chain ID")
    chain_name: Optional[str] = Field(default=None, description="Chain name")


class TheGraphTokenBalance(BaseModel):
    """The Graph API token balance response model."""

    last_update: str
    last_update_block_num: int
    last_update_timestamp: int
    address: str
    contract: str
    amount: str
    value: Optional[float] = None
    name: str
    symbol: str
    decimals: int
    network: str


class TheGraphNativeBalance(BaseModel):
    """The Graph API native balance response model."""

    address: str
    amount: str = Field(..., description="Native balance amount (in wei)")  # API uses "amount" not "balance"
    balance: Optional[str] = Field(default=None, description="Legacy field, use amount instead")
    network: str
    contract: Optional[str] = Field(default=None, description="Contract address (0xeee... for native)")
    symbol: Optional[str] = Field(default=None, description="Token symbol")
    name: Optional[str] = Field(default=None, description="Token name")
    decimals: Optional[int] = Field(default=18, description="Token decimals")
    value: Optional[float] = Field(default=None, description="Balance value in native token")
    last_update: Optional[str] = Field(default=None, description="Last update timestamp")
    last_update_block_num: Optional[int] = Field(default=None, description="Last update block number")
    last_update_timestamp: Optional[int] = Field(default=None, description="Last update timestamp (unix)")


class TheGraphTokenResponse(BaseModel):
    """The Graph API token response wrapper."""

    data: list[TheGraphTokenBalance]


class TheGraphNativeResponse(BaseModel):
    """The Graph API native response wrapper."""

    data: list[TheGraphNativeBalance]



