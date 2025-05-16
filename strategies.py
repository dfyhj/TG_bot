def analyze_all_strategies(analysis):
    print("=== ANALYSIS RECEIVED ===")
    print("Summary:", analysis.summary)
    print("Indicators:", analysis.indicators)
def rsi_stochastic_strategy(indicators):
    rsi = indicators.get("RSI")
    stoch = indicators.get("Stochastic %K")
    stoch_signal = indicators.get("Stochastic %D")

    if rsi is None or stoch is None or stoch_signal is None:
        return False

    if rsi < 40 and stoch_k < 50 and stoch_d < 50:
        return True
    elif rsi > 70 and stoch > 80 and stoch < stoch_signal:
        return True
    return False

def macd_rsi_strategy(indicators):
    macd = indicators.get("MACD.macd")
    signal = indicators.get("MACD.signal")
    rsi = indicators.get("RSI")

    if macd is None or signal is None or rsi is None:
        return False

    if macd > signal and rsi < 70:
        return True
    elif macd < signal and rsi > 30:
        return True
    return False

def bollinger_price_action_strategy(indicators):
    close = indicators.get("close")
    bb_upper = indicators.get("BB.upper")
    bb_lower = indicators.get("BB.lower")

    if close is None or bb_upper is None or bb_lower is None:
        return False

    if close < bb_lower:
        return True
    elif close > bb_upper:
        return True
    return False

def sma_crossover_strategy(indicators):
    sma_10 = indicators.get("SMA10")
    sma_30 = indicators.get("SMA30")

    if sma_10 is None or sma_30 is None:
        return False

    if sma_10 > sma_30:
        return True
    elif sma_10 < sma_30:
        return True
    return False

def heiken_ashi_stochastic_strategy(indicators):
    heiken_ashi = indicators.get("Heikin Ashi")
    stoch = indicators.get("Stochastic %K")
    stoch_signal = indicators.get("Stochastic %D")

    if heiken_ashi is None or stoch is None or stoch_signal is None:
        return False

    if "green" in heiken_ashi and stoch < 20 and stoch > stoch_signal:
        return True
    elif "red" in heiken_ashi and stoch > 80 and stoch < stoch_signal:
        return True
    return False

def analyze_all_strategies(analysis):
    indicators = analysis.indicators if hasattr(analysis, "indicators") else {}

    strategies = {
        "RSI + Stochastic": rsi_stochastic_strategy(indicators),
        "MACD + RSI": macd_rsi_strategy(indicators),
        "Bollinger Bands + Price Action": bollinger_price_action_strategy(indicators),
        "SMA 10 + SMA 30": sma_crossover_strategy(indicators),
        "Heiken Ashi + Stochastic": heiken_ashi_stochastic_strategy(indicators)
    }

    passed = {name: result for name, result in strategies.items() if result}
    confidence = int((len(passed) / len(strategies)) * 100)

    direction = "buy" if "RSI + Stochastic" in passed or "MACD + RSI" in passed else "sell" if passed else "none"
print("Matches:", matches)
print("Details:", details)
    return direction, len(passed), ", ".join(passed.keys())
