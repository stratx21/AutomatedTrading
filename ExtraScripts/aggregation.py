#inputs
amount = 25000
avg_percent_day = 5.0/5
trading_days = 260
years = 0
months = 12

years += months/12
trading_days *= years
avg_percent_day /= 100

day = 0

while(day < trading_days):
    amount=amount+avg_percent_day*amount
    day+=1
    

print("amount after timex1: ",amount)

day = 0

while(day < trading_days):
    amount=amount+avg_percent_day*amount
    day+=1
    
print("amount after timex2: ",amount)

day = 0

while(day < trading_days):
    amount=amount+avg_percent_day*amount
    day+=1
    
print("amount after timex3: ",amount)