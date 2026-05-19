# Import necessary libraries
import yfinance as yf
import pandas as pd
import random
from datetime import datetime, timedelta

# Read a stock tickers from CSV files 
def read_stocks_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# List of NSE stock tickers 
nse_stock_list = read_stocks_from_file('nse_stocks.csv')


# Select 20 random stocks
stock_list = random.sample(nse_stock_list, min(20, len(nse_stock_list)))
print("\n stock_list :", stock_list)

print()
# Filter stocks with market cap above 500 million rupees
filtered_stocks = []
for ticker in stock_list:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        market_cap = info.get("marketCap", None)
        if market_cap and market_cap >= 500000000:
            filtered_stocks.append((ticker, market_cap))
    except:
        continue

print()
# Sort by market cap
filtered_stocks.sort(key=lambda x: x[1], reverse=True)
print("filtered_stocks : ", filtered_stocks)

print()
# Classify into Large / Mid / Small cap
classified_stocks = []
for ticker, mc in filtered_stocks:
    if mc >= 96500000000:
        cap = "Large"
    elif 32750000000 < mc < 96500000000:
        cap = "Medium"
    else:
        cap = "Small"
    classified_stocks.append((ticker, mc, cap))
print("classified_stocks : ", classified_stocks)

# Profitability check and Bi-Annual Return calculation
final_stocks = []
for ticker, mc, cap in classified_stocks:
    print("\n===============================================\n")
    print("ticker : ", ticker)
    try:
        end = datetime.now()
        start = end - timedelta(days=3*365)
        df = yf.download(ticker, start=start, end=end, interval='1mo')
        # print("df : ", df)
        df = df[['Close']]
        if len(df) < 24:
            continue
        close_prices = df["Close"].values.tolist()
        close_prices = [x[0] for x in close_prices]
        # print("\n close_prices : ", close_prices)

        # Parameters based on cap type
        if cap == "Large":
            window, threshold = 6, 0.6
        elif cap == "Mid":
            window, threshold = 4, 0.7
        else:
            window, threshold = 2, 0.8

        months = len(close_prices)
        indices = list(range(window - 1, months, window))

        comparisons = []
        for i in range(1, len(indices)):
            prev_val = close_prices[indices[i-1]]
            curr_val = close_prices[indices[i]]
            is_greater = curr_val > prev_val
            comparisons.append(is_greater)

        true_count = sum(comparisons)
        total_comparisons = len(comparisons)
        success_rate = true_count / total_comparisons

        print()
        # print("Indices compared:", indices)
        # print("Comparisons:", comparisons)
        print(f"True count: {true_count}/{total_comparisons}")
        print(f"Success rate: {success_rate:.2%}")

        # Calculate Average Bi-Annual Returns for past 3 years
        step_avg = 6  # Average every 12th element
        biannual_indices = [
            i for i, num in enumerate(close_prices) if (i + 1) % step_avg == 0
        ]  # [11, 23, 35]
        biannual_indices.insert(0, 0)
        # print("biannual_indices : ", biannual_indices)
        biannual_vals = [close_prices[i] for i in biannual_indices]
        # print("biannual_vals : ", biannual_vals)
        percentage = [
            ((biannual_vals[i + 1] * 100) / biannual_vals[i]) - 100
            for i, num in enumerate(biannual_vals)
            if i < len(biannual_vals) - 1
        ]
        print(percentage)

        avg_biannual_return = sum(percentage) / len(percentage)
        print(avg_biannual_return)

        if success_rate >= threshold:
            final_stocks.append((ticker, mc, cap, avg_biannual_return))

    except Exception as e:
        print("Error occurred : ", e)

print()
# Sort by highest return
final_stocks.sort(key=lambda x: x[3], reverse=True)
print("final_stocks : ", final_stocks)

# Export to CSV
df_final = pd.DataFrame(final_stocks, columns=["Ticker", "Market Capitalization", "Company Size", "Average Half Yearly Return (%)"])
df_final.to_csv("profitable_stocks.csv", index=False)

print("\n ✅ Process complete. Output saved to profitable_stocks.csv \n")
