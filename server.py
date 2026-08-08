#!/usr/bin/env python3
"""
市场猎手 - 外部 API 服务
部署到外部服务器，提供 Polymarket 数据代理和分析服务
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import httpx
import json
from datetime import datetime

app = FastAPI(title="市场猎手 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"
http_client = httpx.AsyncClient(timeout=30.0)


class Market(BaseModel):
    condition_id: str
    question: str
    outcomes: List[str]
    outcome_prices: List[float]
    volume_24h: float
    liquidity: float
    end_date: str
    tokens: List[Dict] = []

class ArbitrageOpportunity(BaseModel):
    market: Market
    spread: float
    expected_profit: float
    risk_level: str
    action: str

class WalletTrade(BaseModel):
    tx_hash: str
    timestamp: str
    market: str
    side: str
    amount: float
    price: float
    outcome: str

class WalletAnalysis(BaseModel):
    address: str
    total_trades: int
    win_rate: float
    total_pnl: float
    strategy: str
    recent_trades: List[WalletTrade]


@app.get("/")
async def root():
    return {"service": "市场猎手 API", "version": "1.0.0", "status": "running"}


@app.get("/markets", response_model=List[Market])
async def get_markets(limit: int = Query(default=50, ge=1, le=200)):
    try:
        response = await http_client.get(
            f"{GAMMA_API}/markets",
            params={"limit": limit, "active": "true", "closed": "false", "order": "volume24hr", "ascending": "false"},
            headers={"User-Agent": "MarketHunter/1.0"}
        )
        response.raise_for_status()
        data = response.json()
        markets = []
        for item in data:
            outcomes, prices, tokens = [], [], []
            if item.get("
