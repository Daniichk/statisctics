import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from datetime import datetime, timedelta

class BlackSwanAgent:
    def __init__(self, target_ticker):
        self.target = target_ticker
        # Systemic Risk Assets
        self.macro_assets = {
            "S&P500": "^GSPC",    # Market Benchmark
            "Volatility": "^VIX", # Fear Index
            "Gold": "GC=F",       # Panic Hedge
            "USD_Index": "DX-Y.NYB", # Liquidity Drain (The Wrecking Ball)
            "Yield_10Y": "^TNX"   # Interest Rate Pressure
        }
        # Using Gradient Boosting for non-linear crash patterns
        self.model = GradientBoostingClassifier(n_estimators=500, learning_rate=0.05)

    def fetch_global_intelligence(self):
        print(f"📡 SCANNING SYSTEMIC RISK LAYERS FOR {self.target}...")
        end = datetime.now()
        start = end - timedelta(days=5000) # ~14 years to include 2008/2020/2022
        
        data_frames = {}
        for name, ticker in self.macro_assets.items():
            data_frames[name] = yf.download(ticker, start=start, end=end)['Close']
        
        target_data = yf.download(self.target, start=start, end=end)
        df = pd.DataFrame(data_frames)
        df['Target_Close'] = target_data['Close']
        return df.ffill().dropna()

    def detect_crash_patterns(self, df):
        """Learning from 1987, 2000, 2008, 2020 conditions"""
        # 1. VIX Velocity (Panic Speed)
        df['VIX_Acceleration'] = df['Volatility'].pct_change(periods=5)
        
        # 2. Yield Pressure (Is the 10Y climbing too fast?)
        df['Yield_Shock'] = df['Yield_10Y'].pct_change(periods=20)
        
        # 3. The Death Cross (Price vs Long Term Trend)
        df['SMA_200'] = ta.sma(df['Target_Close'], length=200)
        df['Dist_From_200'] = (df['Target_Close'] - df['SMA_200']) / df['SMA_200']
        
        # 4. Liquidity Squeeze (Rising Dollar + Falling Gold = Total Collapse)
        df['Liquidity_Stress'] = df['USD_Index'].pct_change() - df['Gold'].pct_change()

        # TARGET: CRASH DEFINITION
        # A 5% drop within 5 days is classified as a "Mini-Crash" (1)
        df['Next_5d_Ret'] = df['Target_Close'].shift(-5) / df['Target_Close'] - 1
        df['CRASH_ZONE'] = (df['Next_5d_Ret'] < -0.05).astype(int)
        
        return df.dropna()

    def train_on_history(self, df):
        features = ['VIX_Acceleration', 'Yield_Shock', 'Dist_From_200', 'Liquidity_Stress', 'USD_Index']
        X = df[features]
        y = df['CRASH_ZONE']
        
        self.model.fit(X, y)
        return features

    def final_verdict(self):
        raw_df = self.fetch_global_intelligence()
        data = self.detect_crash_patterns(raw_df)
        features = self.train_on_history(data)
        
        # Current State Analysis
        current = data[features].iloc[-1:]
        crash_prob = self.model.predict_proba(current)[0][1]
        
        # Immediate Triggers (Rules of Ruin)
        vix_now = data['Volatility'].iloc[-1]
        dist_200 = data['Dist_From_200'].iloc[-1]
        
        print("\n" + "="*50)
        print(f"🚨 HARDCORE RISK ASSESSMENT: {self.target}")
        print(f"Systemic Crash Probability: {crash_prob:.2%}")
        print(f"VIX Level: {vix_now:.2f} | Distance from 200MA: {dist_200:.2%}")
        print("="*50)

        # THE HARDCORE LOGIC
        if crash_prob > 0.75 or (vix_now > 35 and dist_200 < 0):
            return "💥 BLACK SWAN DETECTED: TERMINATE ALL POSITIONS. Market structure is failing. Total exit recommended."
        
        elif crash_prob > 0.45 or dist_200 < -0.05:
            return "⚠️ EXTREME CAUTION: Bear market confirmed. Sell into rallies. Do not hold through the weekend."
        
        elif dist_200 > 0.15 and vix_now < 15:
            return "🔥 BUBBLE WARNING: Market is overextended. Take 50% profits now. Do not wait for the top."
        
        else:
            return "🛡️ SECURE: Systemic indicators within normal limits. Maintain Stop-Losses."

# --- INITIALIZE PROTOCOL ---
if __name__ == "__main__":
    # Test on a highly liquid index or asset
    # Use "SPY" for S&P 500 ETF or "BTC-USD" for extreme volatility
    agent = BlackSwanAgent("SPY")
    print(agent.final_verdict())