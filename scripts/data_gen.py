import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import List, Dict, Tuple
import hashlib
import pytz
from collections import defaultdict

class TransactionDataGenerator:
    def __init__(self):
        # Expanded merchant categories and specific merchants
        self.merchant_data = {
            'Retail': {
                'physical': ['Walmart', 'Target', 'Best Buy', 'Home Depot', 'Costco', 'IKEA', 'Macy\'s', 'Nike Store'],
                'online': ['Amazon', 'eBay', 'Etsy', 'Wayfair', 'Shopify Store', 'AliExpress', 'Newegg']
            },
            'Grocery': {
                'physical': ['Whole Foods', 'Kroger', 'Safeway', 'Trader Joe\'s', 'Aldi', 'Publix', 'Food Lion'],
                'online': ['Instacart', 'Amazon Fresh', 'FreshDirect', 'Walmart Grocery']
            },
            'Restaurant': {
                'fast_food': ['McDonald\'s', 'Burger King', 'Wendy\'s', 'KFC', 'Taco Bell', 'Subway'],
                'casual': ['Applebee\'s', 'Chili\'s', 'Olive Garden', 'Red Lobster', 'TGI Fridays'],
                'premium': ['Ruth\'s Chris', 'Capital Grille', 'Nobu', 'Morton\'s']
            },
            'Travel': {
                'airlines': ['United Airlines', 'American Airlines', 'Delta', 'Southwest', 'JetBlue', 'Emirates'],
                'hotels': ['Marriott', 'Hilton', 'Hyatt', 'Holiday Inn', 'Sheraton', 'Westin'],
                'booking': ['Expedia', 'Booking.com', 'Airbnb', 'Hotels.com', 'Kayak'],
                'transport': ['Uber', 'Lyft', 'Careem', 'Enterprise Rent-A-Car', 'Hertz']
            },
            'Gas': {
                'major': ['Shell', 'BP', 'Exxon', 'Chevron', 'Texaco', 'Mobil'],
                'local': ['Local Gas Station', 'Highway Gas Stop', 'Truck Stop']
            },
            'Entertainment': {
                'streaming': ['Netflix', 'Disney+', 'Hulu', 'HBO Max', 'Amazon Prime', 'Spotify', 'Apple Music'],
                'gaming': ['Steam', 'PlayStation Store', 'Xbox Live', 'Nintendo eShop', 'Epic Games'],
                'events': ['Ticketmaster', 'StubHub', 'LiveNation', 'AMC Theaters', 'Regal Cinemas']
            },
            'Healthcare': {
                'pharmacy': ['CVS Pharmacy', 'Walgreens', 'Rite Aid', 'DuaneReade'],
                'medical': ['Local Hospital', 'Medical Center', 'Urgent Care', 'Lab Corp']
            },
            'Education': {
                'online': ['Coursera', 'Udemy', 'edX', 'Skillshare', 'MasterClass'],
                'supplies': ['Chegg', 'Barnes & Noble', 'University Bookstore']
            }
        }
        
        # Enhanced country and currency data with risk scores
        self.country_currency = {
            'USA': {'currency': 'USD', 'risk': 1.0, 'timezone': 'America/New_York'},
            'UK': {'currency': 'GBP', 'risk': 1.0, 'timezone': 'Europe/London'},
            'Canada': {'currency': 'CAD', 'risk': 1.0, 'timezone': 'America/Toronto'},
            'France': {'currency': 'EUR', 'risk': 1.0, 'timezone': 'Europe/Paris'},
            'Germany': {'currency': 'EUR', 'risk': 1.0, 'timezone': 'Europe/Berlin'},
            'Japan': {'currency': 'JPY', 'risk': 1.0, 'timezone': 'Asia/Tokyo'},
            'Australia': {'currency': 'AUD', 'risk': 1.0, 'timezone': 'Australia/Sydney'},
            'Singapore': {'currency': 'SGD', 'risk': 1.1, 'timezone': 'Asia/Singapore'},
            'Brazil': {'currency': 'BRL', 'risk': 1.3, 'timezone': 'America/Sao_Paulo'},
            'Mexico': {'currency': 'MXN', 'risk': 1.4, 'timezone': 'America/Mexico_City'},
            'Nigeria': {'currency': 'NGN', 'risk': 1.8, 'timezone': 'Africa/Lagos'},
            'Russia': {'currency': 'RUB', 'risk': 1.6, 'timezone': 'Europe/Moscow'}
        }
        
        # Expanded cities with population sizes affecting transaction probability
        self.cities = {
            'USA': [
                {'name': 'New York', 'size': 'large', 'risk': 1.2},
                {'name': 'Los Angeles', 'size': 'large', 'risk': 1.1},
                {'name': 'Chicago', 'size': 'large', 'risk': 1.2},
                {'name': 'Houston', 'size': 'large', 'risk': 1.1},
                {'name': 'Phoenix', 'size': 'medium', 'risk': 1.0},
                {'name': 'Philadelphia', 'size': 'medium', 'risk': 1.1},
                {'name': 'San Antonio', 'size': 'medium', 'risk': 1.0},
                {'name': 'San Diego', 'size': 'medium', 'risk': 1.0},
                {'name': 'Dallas', 'size': 'medium', 'risk': 1.1},
                {'name': 'San Jose', 'size': 'medium', 'risk': 1.2}
            ],
            # Add similar detailed city data for other countries...
        }
        
        # Enhanced card types with more detailed attributes
        self.card_types = {
            'Basic Credit': {
                'limit': (1000, 5000),
                'fraud_risk': 1.2,
                'foreign_transaction_fee': 0.03,
                'rewards_rate': 0.01,
                'annual_fee': 0
            },
            'Gold Credit': {
                'limit': (5000, 15000),
                'fraud_risk': 0.9,
                'foreign_transaction_fee': 0.02,
                'rewards_rate': 0.02,
                'annual_fee': 95
            },
            'Platinum Credit': {
                'limit': (15000, 50000),
                'fraud_risk': 0.7,
                'foreign_transaction_fee': 0.0,
                'rewards_rate': 0.03,
                'annual_fee': 495
            },
            'Basic Debit': {
                'limit': (500, 3000),
                'fraud_risk': 1.3,
                'foreign_transaction_fee': 0.03,
                'rewards_rate': 0.0,
                'annual_fee': 0
            },
            'Premium Debit': {
                'limit': (3000, 10000),
                'fraud_risk': 1.1,
                'foreign_transaction_fee': 0.02,
                'rewards_rate': 0.01,
                'annual_fee': 25
            }
        }
        
        # Device and channel information
        self.devices = {
            'web': ['Chrome', 'Firefox', 'Safari', 'Edge'],
            'mobile': ['iOS App', 'Android App'],
            'pos': ['Chip Reader', 'Magnetic Stripe', 'NFC Payment']
        }
        
        # Initialize transaction history for velocity checks
        self.transaction_history = defaultdict(list)
        
        # Currency conversion rates with slight randomization
        self.base_currency_rates = {
            'USD': 1.0,
            'GBP': 0.73,
            'EUR': 0.85,
            'CAD': 1.25,
            'JPY': 110.0,
            'AUD': 1.35,
            'SGD': 1.35,
            'BRL': 5.0,
            'MXN': 20.0,
            'NGN': 410.0,
            'RUB': 75.0
        }

    def get_currency_rate(self, currency: str) -> float:
        """Get currency rate with small random fluctuation."""
        base_rate = self.base_currency_rates[currency]
        fluctuation = random.uniform(-0.02, 0.02)  # ±2% random fluctuation
        return base_rate * (1 + fluctuation)

    def generate_customer_profile(self) -> Dict:
        """Generate a detailed customer profile with enhanced attributes."""
        account_age = random.randint(1, 3650)
        card_type = random.choice(list(self.card_types.keys()))
        card_info = self.card_types[card_type]
        home_country = random.choice(list(self.country_currency.keys()))
        
        # Generate consistent customer behavior patterns
        shopping_patterns = {
            'online_frequency': random.uniform(0.1, 0.9),
            'international_frequency': random.uniform(0.05, 0.3),
            'premium_merchant_frequency': random.uniform(0.1, 0.5),
            'night_shopping_frequency': random.uniform(0.05, 0.2)
        }
        
        # Calculate credit limit based on range and profile
        credit_score = round(random.uniform(300, 850), 0)
        credit_limit = random.randint(*card_info['limit'])
        
        # Generate device preferences
        preferred_devices = random.sample(
            self.devices['web'] + self.devices['mobile'],
            random.randint(1, 3)
        )
        
        return {
            'customer_id': f'CUST_{random.randint(10000, 99999)}',
            'account_age_days': account_age,
            'card_type': card_type,
            'card_number': self.generate_card_number(),
            'credit_limit': credit_limit,
            'credit_score': credit_score,
            'home_country': home_country,
            'home_city': random.choice([city['name'] for city in self.cities['USA']]),
            'shopping_patterns': shopping_patterns,
            'preferred_devices': preferred_devices,
            'typical_spending_range': (
                credit_limit * 0.1,
                credit_limit * 0.4
            ),
            'foreign_transaction_fee': card_info['foreign_transaction_fee'],
            'rewards_rate': card_info['rewards_rate'],
            'annual_fee': card_info['annual_fee'],
            'fraud_protection_enabled': random.choice([True, False]),
            'mobile_alerts_enabled': random.choice([True, False]),
            'last_address_change_days': random.randint(0, account_age),
            'phone_verified': random.choice([True, False]),
            'email_verified': random.choice([True, False]),
            'two_factor_auth': random.choice([True, False])
        }

    def generate_card_number(self) -> str:
        """Generate a valid-looking card number."""
        prefix = random.choice(['4', '5', '37', '6'])  # Different card networks
        length = 16 if prefix not in ['37'] else 15
        remaining_length = length - len(prefix)
        number = prefix + ''.join([str(random.randint(0, 9)) for _ in range(remaining_length-1)])
        
        # Add Luhn algorithm check digit
        total = 0
        for i, digit in enumerate(reversed(number)):
            digit = int(digit)
            if i % 2 == 0:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit
        check_digit = (10 - (total % 10)) % 10
        
        return number + str(check_digit)

    def calculate_transaction_velocity(self, customer_id: str, amount: float, 
                                    timestamp: datetime, window_minutes: int = 60) -> Dict:
        """Calculate transaction velocity metrics."""
        recent_transactions = [
            tx for tx in self.transaction_history[customer_id]
            if (timestamp - tx['timestamp']).total_seconds() <= window_minutes * 60
        ]
        
        return {
            'num_transactions': len(recent_transactions),
            'total_amount': sum(tx['amount'] for tx in recent_transactions) + amount,
            'unique_merchants': len(set(tx['merchant'] for tx in recent_transactions)),
            'unique_countries': len(set(tx['country'] for tx in recent_transactions)),
            'max_single_amount': max([tx['amount'] for tx in recent_transactions] + [amount])
        }

    def generate_transaction_amount(self, merchant_category: str, merchant_type: str,
                                  customer_profile: Dict, is_fraud: bool) -> float:
        """Generate realistic transaction amounts with enhanced patterns."""
        # Base amount ranges by merchant category and type
        base_ranges = {
            'Retail': {
                'physical': (10, 500),
                'online': (20, 1000)
            },
            'Grocery': {
                'physical': (20, 300),
                'online': (50, 400)
            },
            'Restaurant': {
                'fast_food': (5, 30),
                'casual': (20, 100),
                'premium': (100, 500)
            },
            'Travel': {
                'airlines': (200, 2000),
                'hotels': (100, 1000),
                'booking': (200, 3000),
                'transport': (10, 100)
            },
            'Entertainment': {
                'streaming': (5, 50),
                'gaming': (10, 200),
                'events': (50, 500)
            }
        }
        
        try:
            min_amount, max_amount = base_ranges[merchant_category][merchant_type]
        except KeyError:
            min_amount, max_amount = (10, 500)  # Default range
        
        # Adjust based on customer profile
        typical_min, typical_max = customer_profile['typical_spending_range']
        min_amount = max(min_amount, typical_min * 0.5)
        max_amount = min(max_amount, typical_max * 1.5)
        
        if is_fraud:
            if random.random() < 0.3:
                # Small test transaction
                amount = random.uniform(0.01, 5)
            else:
                # Unusually large transaction
                amount = random.uniform(max_amount, max_amount * 5)
        else:
            # Normal transaction with slight randomization
            amount = random.uniform(min_amount, max_amount)
            # Add common price patterns
            amount = round(amount * 0.99, 2)  # Prices often end in .99
        
        return round(amount, 2)

    def generate_transaction_time(self, customer_profile: Dict, is_fraud: bool) -> datetime:
        """Generate realistic transaction timestamps with enhanced patterns."""
        current_time = datetime.now(pytz.UTC)
        days_ago = random.randint(0, 30)
        
        shopping_patterns = customer_profile['shopping_patterns']
        
        if is_fraud:
            # Fraudulent transactions more likely during night hours
            hour = random.choices(
                range(24),
                weights=[4 if i in range(1, 5) else 1 for i in range(24)]
            )[0]
        else:
            # Normal transactions follow customer's patterns
            if random.random() < shopping_patterns['night_shopping_frequency']:
                # Night shopping (22:00 - 05:00)
                hour = random.randint(22, 23) if random.random() < 0.5 else random.randint(0, 5)
            else:
                # Regular hours with peak times
                hour = random.choices(
                    range(24),
                    weights=[
                        1, 1, 1, 1, 1, 2,  # 00-05: very low
                        3, 5, 7, 6, 5, 6,  # 06-11: morning rise
                        7, 6, 5, 5, 6, 7,  # 12-17: steady day
                        8, 7, 5, 3, 2, 1   # 18-23: evening decline
                    ]
                )[0]
        
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        transaction_time = current_time - timedelta(
            days=days_ago,
            hours=current_time.hour - hour,
            minutes=current_time.minute - minute,
            seconds=current_time.second - second
        )
        
        return transaction_time

    def generate_transaction_location(self, customer_profile: Dict, is_fraud: bool) -> Tuple[str, Dict]:
        """Generate transaction location with enhanced geographical patterns."""
        home_country = customer_profile['home_country']
        shopping_patterns = customer_profile['shopping_patterns']
        
        if is_fraud:
            # Fraudulent transactions more likely in high-risk countries
            high_risk_countries = [
                country for country, data in self.country_currency.items()
                if data['risk'] > 1.2
            ]
            if high_risk_countries and random.random() < 0.7:
                country = random.choice(high_risk_countries)
            else:
                country = random.choice(list(self.country_currency.keys()))
        else:
            if random.random() < shopping_patterns['international_frequency']:
                # International transaction
                possible_countries = list(set(self.country_currency.keys()) - {home_country})
                country = random.choice(possible_countries)
            else:
                # Domestic transaction
                country = home_country
        
        # Select city based on country
        if country in self.cities:
            city_data = random.choice(self.cities[country])
        else:
            # Default city data if country cities not defined
            city_data = {
                'name': 'Unknown City',
                'size': 'medium',
                'risk': 1.0
            }
        
        return country, city_data

    def generate_device_info(self, customer_profile: Dict, is_fraud: bool) -> Dict:
        """Generate device and channel information for the transaction."""
        preferred_devices = customer_profile['preferred_devices']
        
        if is_fraud:
            # Fraudulent transactions more likely from unusual devices
            all_devices = [
                device for devices in self.devices.values()
                for device in devices
            ]
            unusual_devices = list(set(all_devices) - set(preferred_devices))
            if unusual_devices:
                device = random.choice(unusual_devices)
            else:
                device = random.choice(all_devices)
                
            # Generate suspicious device fingerprint
            fingerprint = hashlib.md5(
                str(random.randint(1, 1000000)).encode()
            ).hexdigest()
        else:
            # Normal transactions use preferred devices
            device = random.choice(preferred_devices)
            # Generate consistent device fingerprint
            fingerprint = hashlib.md5(
                f"{customer_profile['customer_id']}_{device}".encode()
            ).hexdigest()
        
        return {
            'device': device,
            'device_fingerprint': fingerprint,
            'channel': next(
                channel for channel, devices in self.devices.items()
                if device in devices
            ),
            'ip_address': f"{random.randint(1, 255)}.{random.randint(0, 255)}."
                         f"{random.randint(0, 255)}.{random.randint(0, 255)}"
        }

    def generate_transaction(self, customer_profile: Dict, is_fraud: bool = False) -> Dict:
        """Generate a single transaction with all features."""
        # Select merchant category and type
        merchant_category = random.choice(list(self.merchant_data.keys()))
        merchant_type = random.choice(list(self.merchant_data[merchant_category].keys()))
        merchant = random.choice(self.merchant_data[merchant_category][merchant_type])
        
        # Generate timestamp
        timestamp = self.generate_transaction_time(customer_profile, is_fraud)
        
        # Generate location
        country, city_data = self.generate_transaction_location(customer_profile, is_fraud)
        
        # Generate amount
        amount = self.generate_transaction_amount(
            merchant_category, merchant_type, customer_profile, is_fraud
        )
        
        # Apply currency conversion if necessary
        currency = self.country_currency[country]['currency']
        if currency != 'USD':
            amount *= self.get_currency_rate(currency)
        
        # Generate device info
        device_info = self.generate_device_info(customer_profile, is_fraud)
        
        # Calculate velocity metrics
        velocity_metrics = self.calculate_transaction_velocity(
            customer_profile['customer_id'], amount, timestamp
        )
        
        transaction = {
            'transaction_id': f"TX_{hashlib.md5(str(timestamp).encode()).hexdigest()[:8]}",
            'customer_id': customer_profile['customer_id'],
            'card_number': customer_profile['card_number'],
            'timestamp': timestamp,
            'merchant_category': merchant_category,
            'merchant_type': merchant_type,
            'merchant': merchant,
            'amount': round(amount, 2),
            'currency': currency,
            'country': country,
            'city': city_data['name'],
            'city_size': city_data['size'],
            'card_type': customer_profile['card_type'],
            'card_present': device_info['channel'] == 'pos',
            'device': device_info['device'],
            'channel': device_info['channel'],
            'device_fingerprint': device_info['device_fingerprint'],
            'ip_address': device_info['ip_address'],
            'distance_from_home': 1 if country != customer_profile['home_country'] else 0,
            'high_risk_merchant': merchant_category in ['Travel', 'Entertainment'],
            'transaction_hour': timestamp.hour,
            'weekend_transaction': timestamp.weekday() >= 5,
            'velocity_last_hour': velocity_metrics,
            'is_fraud': is_fraud
        }
        
        # Add transaction to history
        self.transaction_history[customer_profile['customer_id']].append({
            'timestamp': timestamp,
            'amount': amount,
            'merchant': merchant,
            'country': country
        })
        
        return transaction

    def generate_dataset(self, num_customers: int, 
                        transactions_per_customer: Tuple[int, int]=(20, 50), # min 20 and max 50 transaction per customer
                        fraud_percentage: float=0.1) -> pd.DataFrame:
        """Generate complete dataset with specified parameters."""
        all_transactions = []
        
        for _ in range(num_customers):
            customer_profile = self.generate_customer_profile()
            num_transactions = random.randint(*transactions_per_customer)
            
            # Determine which transactions will be fraudulent
            num_fraud = int(num_transactions * fraud_percentage)
            fraud_indices = set(random.sample(range(num_transactions), num_fraud))
            
            for tx_index in range(num_transactions):
                is_fraud = tx_index in fraud_indices
                transaction = self.generate_transaction(customer_profile, is_fraud)
                all_transactions.append(transaction)
        
        # Convert to DataFrame and sort by timestamp
        df = pd.DataFrame(all_transactions)
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df

# Example usage
if __name__ == "__main__":
    generator = TransactionDataGenerator()
    df = generator.generate_dataset(
        num_customers=500,
        transactions_per_customer=(100, 200),
        fraud_percentage=0.1
    )
    print(f"Generated {len(df)} transactions")
    print(f"Fraud transactions: {df['is_fraud'].sum()}")
    print("\nSample transaction:")
    print(df.iloc[0].to_dict())
    
    # Save the generated dataset to a CSV file
    df.to_csv("synthetic_fraud_data.csv", index=False)
    print("Dataset saved to synthetic_fraud_data.csv")
