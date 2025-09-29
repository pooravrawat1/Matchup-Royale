import requests
import time
from typing import List, Dict, Optional
from urllib.parse import quote
from config.settings import config

class RateLimiter:
    """Simple rate limiter to respect API limits"""
    def __init__(self, max_requests_per_second: int = 10):
        self.max_rps = max_requests_per_second
        self.requests = []
    
    def wait_if_needed(self):
        now = time.time()
        # Remove requests older than 1 second
        self.requests = [req_time for req_time in self.requests if now - req_time < 1]
        
        if len(self.requests) >= self.max_rps:
            sleep_time = 1 - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.requests.append(now)

class ClashRoyaleAPI:
    """Clash Royale API client with error handling and rate limiting"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter(max_requests_per_second=10)
        self.session = requests.Session()
        self.session.headers.update(config.API_HEADERS)
        
        # Statistics
        self.total_requests = 0
        self.failed_requests = 0
        self.rate_limit_hits = 0
    
    def _make_request(self, endpoint: str, max_retries: int = 3) -> Optional[Dict]:
        """Make API request with error handling and rate limiting"""
        
        for attempt in range(max_retries):
            try:
                # Rate limiting
                self.rate_limiter.wait_if_needed()
                
                # Make request
                url = f"{config.CLASH_ROYALE_BASE_URL}{endpoint}"
                response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
                
                self.total_requests += 1
                
                if response.status_code == 200:
                    return response.json()
                    
                elif response.status_code == 429:
                    # Rate limited
                    self.rate_limit_hits += 1
                    wait_time = int(response.headers.get('Retry-After', 60))
                    print(f"⚠️ Rate limited, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                    
                elif response.status_code == 404:
                    # Not found (player doesn't exist or is private)
                    return None
                    
                elif response.status_code == 503:
                    # Service unavailable (maintenance)
                    print("⚠️ API maintenance, waiting 5 minutes...")
                    time.sleep(300)
                    continue
                    
                else:
                    print(f"❌ API Error {response.status_code}: {response.text}")
                    self.failed_requests += 1
                    
            except requests.exceptions.Timeout:
                print(f"⚠️ Request timeout (attempt {attempt + 1})")
                time.sleep(5 * (attempt + 1))
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Request error (attempt {attempt + 1}): {e}")
                time.sleep(5 * (attempt + 1))
        
        # All retries failed
        self.failed_requests += 1
        return None
    
    def get_top_players(self, location: str = 'global', limit: int = 200) -> List[str]:
        """Get top players from leaderboard"""
        endpoint = f"/locations/{location}/rankings/players"
        if limit:
            endpoint += f"?limit={limit}"
        
        print(f"🔍 Getting top {limit} players from {location} leaderboard...")
        
        data = self._make_request(endpoint)
        if not data or 'items' not in data:
            print("❌ Failed to get top players")
            return []
        
        player_tags = [player['tag'] for player in data['items']]
        print(f"✅ Retrieved {len(player_tags)} top players")
        return player_tags
    
    def get_player_info(self, player_tag: str) -> Optional[Dict]:
        """Get player information"""
        # Clean and encode player tag
        clean_tag = player_tag.replace('#', '')
        encoded_tag = quote(f"#{clean_tag}", safe='')
        
        endpoint = f"/players/{encoded_tag}"
        
        data = self._make_request(endpoint)
        return data
    
    def get_player_battles(self, player_tag: str) -> List[Dict]:
        """Get battle log for a player"""
        # Clean and encode player tag
        clean_tag = player_tag.replace('#', '')
        encoded_tag = quote(f"#{clean_tag}", safe='')
        
        endpoint = f"/players/{encoded_tag}/battlelog"
        
        data = self._make_request(endpoint)
        if not data:
            return []
        
        # Return the battles list
        return data if isinstance(data, list) else []
    
    def get_cards(self) -> List[Dict]:
        """Get all available cards"""
        endpoint = "/cards"
        
        data = self._make_request(endpoint)
        if not data or 'items' not in data:
            return []
        
        return data['items']
    
    def get_api_stats(self) -> Dict:
        """Get API usage statistics"""
        return {
            'total_requests': self.total_requests,
            'failed_requests': self.failed_requests,
            'rate_limit_hits': self.rate_limit_hits,
            'success_rate': (self.total_requests - self.failed_requests) / max(self.total_requests, 1) * 100
        }
    
    def test_connection(self) -> bool:
        """Test API connection and authentication"""
        print("🧪 Testing API connection...")
        
        # Test with a simple request
        top_players = self.get_top_players(limit=5)
        
        if top_players:
            print(f"✅ API connection successful! Retrieved {len(top_players)} players")
            print(f"📊 API Stats: {self.get_api_stats()}")
            return True
        else:
            print("❌ API connection failed")
            print("🔍 Check your API token and IP address configuration")
            return False