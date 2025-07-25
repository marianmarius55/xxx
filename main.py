import os
import threading
import random
import time
import requests
import logging
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from keep_alive import keep_alive, add_log, update_stats
import select
import tty
import termios

keep_alive()

# File to store invite codes
INVITE_CODES_FILE = 'invite_codes.txt'

def load_invite_codes():
    """Load invite codes from file"""
    if os.path.exists(INVITE_CODES_FILE):
        with open(INVITE_CODES_FILE, 'r') as f:
            codes = [line.strip() for line in f if line.strip()]
            return codes
    return ["435591"]  # Default fallback

def save_invite_code(code):
    """Save a new invite code to file"""
    with open(INVITE_CODES_FILE, 'a') as f:
        f.write(f"{code}\n")

def get_random_invite_code():
    """Get a random invite code from file"""
    codes = load_invite_codes()
    return random.choice(codes)

# Setup detailed logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('registration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DebugLogger:
    def __init__(self):
        pass
    
    def add_log(self, level, message):
        # Send logs to web interface instead of storing locally
        add_log(level, message)
    
    def get_recent_logs(self, count=50):
        return []  # Not needed for web interface

debug_logger = DebugLogger()

class RoshopRegistration:
    def __init__(self):
        self.base_url = "https://roshop44.com"
        self.session = requests.Session()
        
        # Configure connection pool and retry strategy
        adapter = HTTPAdapter(
            pool_connections=50,
            pool_maxsize=100,
            max_retries=Retry(
                total=3,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        self.session.headers.update({
            "Cookie": "se9d04589=tdqulhaf8e21acmargvuguanur",
            "Sec-Ch-Ua-Platform": "\"Linux\"",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\"",
            "Content-Type": "application/json",
            "Sec-Ch-Ua-Mobile": "?0",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Origin": "https://roshop44.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://roshop44.com/2/",
            "Accept-Encoding": "gzip, deflate",
            "Priority": "u=1, i"
        })
        
    def generate_random_phone(self):
        """Generate a random Romanian phone number"""
        return f"075{random.randint(1000000, 9999999)}"
    
    def generate_random_password(self):
        """Generate a random password with 8 or more characters"""
        import string
        length = random.randint(8, 12)
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(length))
    
    def generate_random_username(self):
        """Generate a random username"""
        import string
        length = random.randint(5, 10)
        characters = string.ascii_lowercase + string.digits
        return "".join(random.choice(characters) for _ in range(length))
    
    def register_user(self):
        """Register a new user with random data"""
        phone = self.generate_random_phone()
        password = self.generate_random_password()
        username = self.generate_random_username()
        invite_code = get_random_invite_code()
        
        data = {
            "phone": phone,
            "password": password,
            "conpassword": password,
            "invitecode": invite_code,
            "username": username
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/apitwo/index/register",
                json=data
            )
            
            debug_logger.add_log("INFO", f"Registration response: {response.status_code} | {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    data = result.get("data", {})
                    debug_logger.add_log("SUCCESS", f"Registration successful: {phone} | Password: {password}")
                    return {
                        "phone": phone,
                        "password": password,
                        "userId": data.get("userId"),
                        "token": data.get("toKen"),
                        "inviteCode": data.get("inviteCode")
                    }, None
                else:
                    debug_logger.add_log("ERROR", f"Registration failed: {result}")
                    return None, f"Registration failed: {result}"
            else:
                debug_logger.add_log("ERROR", f"Registration HTTP error: {response.status_code}")
                return None, f"HTTP error: {response.status_code}"
                
        except Exception as e:
            debug_logger.add_log("ERROR", f"Registration exception: {e}")
            return None, f"Exception: {e}"
    
    def add_bank_card(self, user_data):
        """Add bank card information"""
        data = {
            'userid': int(user_data['userId']),
            'token': user_data['token'],
            'user': {
                'id': int(user_data['userId']),
                'phone': user_data['phone'],
                'level': 1,
                'group': 0,
                'invite_code': user_data['inviteCode'],
                'aisle': 2,
                'bank_name': 'x',
                'bank_type': None,
                'account_number': 'x',
                'branch_name': None,
                'ifsc': None,
                'holder_name': 'x',
                'balance': '10.00',
                'freeze': '0.00'
            }
        }
        
        debug_logger.add_log("INFO", f"Bank card request data: {data}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/apitwo/index/goToBindBank",
                json=data
            )
            
            debug_logger.add_log("INFO", f"Bank card response: {response.status_code} | {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                debug_logger.add_log("SUCCESS", f"Bank card added for user: {user_data['userId']}")
                return True
            else:
                debug_logger.add_log("ERROR", f"Bank card HTTP error: {response.status_code}")
                
        except Exception as e:
            debug_logger.add_log("ERROR", f"Bank card exception: {e}")
        
        return False
    
    def create_recharge_orders_parallel(self, user_data):
        """Create multiple recharge orders with parallel requests"""
        num_orders = random.randint(70, 100)
        successful_orders = 0
        
        debug_logger.add_log("INFO", f"Starting {num_orders} recharge orders for user {user_data['userId']}")
        
        def make_single_order():
            nonlocal successful_orders
            amount = str(random.randint(15, 500))
            aisle = random.choice([2, 15])
            
            try:
                data = {
                    'userid': int(user_data['userId']),
                    'token': user_data['token'],
                    'amount': amount,
                    'aisle': aisle
                }
                
                response = self.session.post(
                    f"{self.base_url}/apitwo/recharge/index",
                    json=data
                )
                
                debug_logger.add_log("INFO", f"Recharge response: {response.status_code} | {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 202:
                        order_data = result.get('data', {})
                        order_id = order_data.get('orderId')
                        
                        debug_logger.add_log("INFO", f"Order created: ID={order_id}, Amount={amount}")
                        
                        # Only complete half of the orders (50% chance)
                        if order_id and random.choice([True, False]):
                            update_data = {
                                'userid': int(user_data['userId']),
                                'token': user_data['token'],
                                'orderId': order_id
                            }
                            
                            update_response = self.session.post(
                                f"{self.base_url}/apitwo/recharge/goToUpdateOrder",
                                json=update_data
                            )
                            
                            debug_logger.add_log("INFO", f"Update order response: {update_response.status_code} | {update_response.text}")
                            
                            if update_response.status_code == 200:
                                update_result = update_response.json()
                                debug_logger.add_log("INFO", f"Order update result: {update_result}")
                            
                            debug_logger.add_log("SUCCESS", f"Recharge order completed: {amount} Lei")
                        else:
                            debug_logger.add_log("SUCCESS", f"Recharge order submitted (incomplete): {amount} Lei")
                        
                        successful_orders += 1
                    else:
                        debug_logger.add_log("ERROR", f"Recharge order failed: {result}")
                else:
                    debug_logger.add_log("ERROR", f"Recharge HTTP error: {response.status_code}")
                        
            except Exception as e:
                debug_logger.add_log("ERROR", f"Recharge order exception: {e}")
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_single_order) for _ in range(num_orders)]
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    debug_logger.add_log("ERROR", f"Future exception: {e}")
        
        debug_logger.add_log("INFO", f"Completed {successful_orders}/{num_orders} orders for user {user_data['userId']}")
        return successful_orders

class ContinuousRegistrationManager:
    def __init__(self, num_threads=200):
        self.num_threads = num_threads
        self.total_accounts_logged = 0
        self.total_orders_created = 0
        self.lock = threading.Lock()
        self.running = True
        
    def worker_task(self, worker_id):
        """Worker function that runs continuously"""
        registrar = RoshopRegistration()
        
        while self.running:
            try:
                user_data, reg_error = registrar.register_user()
                if not user_data:
                    continue
                
                with self.lock:
                    self.total_accounts_logged += 1
                    update_stats(accounts=self.total_accounts_logged)
                
                registrar.add_bank_card(user_data)
                
                orders_created = registrar.create_recharge_orders_parallel(user_data)
                
                with self.lock:
                    self.total_orders_created += orders_created
                    update_stats(orders=self.total_orders_created)
                
                save_invite_code(user_data['inviteCode'])
                        
            except Exception as e:
                debug_logger.add_log("ERROR", f"Worker exception: {e}")
    
    def run_continuous_registration(self):
        """Run registration continuously with multiple threads"""
        add_log("INFO", f"Starting registration bot with {self.num_threads} threads")
        add_log("INFO", "Visit http://localhost:8080/logs to view live logs")
        add_log("INFO", "Visit http://localhost:8080/success for success logs only")
        
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = [executor.submit(self.worker_task, i) for i in range(self.num_threads)]
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.running = False
                add_log("INFO", "Registration bot stopped")

def main():
    """Main function to run continuous registration"""
    manager = ContinuousRegistrationManager(num_threads=200)
    manager.run_continuous_registration()

if __name__ == "__main__":
    main()
