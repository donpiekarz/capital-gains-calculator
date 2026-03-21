
import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Final

from cgt_calc.const import TICKER_RENAMES
from cgt_calc.exceptions import ParsingError
from cgt_calc.model import ActionType, BrokerTransaction

class InteractiveBrokersTransaction(BrokerTransaction):
    """Represent single Trading 212 transaction."""

    def __init__(self, row):
        """Create transaction from CSV row."""

        self.transaction_id = row["TransactionID"]

        action_dict = {
            "BUY": ActionType.BUY,
            "SELL": ActionType.SELL,
        }

        date = datetime.strptime(row["TradeDate"], '%m/%d/%Y').date()
        action = action_dict[row["Buy/Sell"]]

        symbol = row["Symbol"]
        description = row["Description"]
        if row["AssetClass"] == "STK":
            quantity = abs(Decimal(row["Quantity"]))
        elif row["AssetClass"] == "OPT":
            quantity = 100 * abs(Decimal(row["Quantity"]))
        price = Decimal(row["TradePrice"])
        fees = abs(Decimal(row["IBCommission"]))
        amount = Decimal(row["Proceeds"]) - fees
        currency = row["CurrencyPrimary"]
        broker = "InteractiveBrokers"

        self.fxrate = Decimal(row["FXRateToBase"])

        super().__init__(
            date,
            action,
            symbol,
            description,
            quantity,
            price,
            fees,
            amount,
            currency,
            broker,
        )

    def __hash__(self) -> int:
        """Calculate hash."""
        return hash(self.transaction_id)

def read_interactivebrokers_transactions(transactions_folder: str) -> list[BrokerTransaction]:
    transactions = []
    for file in Path(transactions_folder).glob("*.csv"):
        with Path(file).open(encoding="utf-8") as csv_file:
            print(f"Parsing {file}")
            reader = csv.DictReader(csv_file)
            for row in reader:
                if (row["TransactionType"] == "ExchTrade" or row["TransactionType"] == "BookTrade" or row["TransactionType"] == "FracShare"):
                    if row["AssetClass"] == "STK" or row["AssetClass"] == "OPT":
                        transactions.append(InteractiveBrokersTransaction(row))
                    else:
                        print(f'Ignoring {row["TransactionType"]} {row["AssetClass"]}')
                else:
                    print(f'Ignoring {row["TransactionType"]} {row["AssetClass"]}')

    transactions = list(set(transactions))  # remove duplicates
    #transactions.sort(key=by_date_and_action)
    return transactions
