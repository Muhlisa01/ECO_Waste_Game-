class GameStateManager:
    """O'yin ekranlarini boshqaruvchi asosiy tizim."""
    def __init__(self):
        self.state = "MENU"
        self.score = 0
        self.player_name = ""
        self.summary_info = {}
        self.player_profiles = {}  # Ismlar bo'yicha o'yinchilar profili
        self.player_coins = {}  # O'yinchi ismiga ko'ra tangalar
        
    def calculate_coins(self, score):
        """Balllardan tangalarni hisoblash - har 50 ball = 1 tanga"""
        return score // 50

    def save_player_profile(self, name, score):
        """O'yinchining profilini saqlash"""
        if name not in self.player_profiles:
            self.player_profiles[name] = {
                "scores": [],
                "total_coins": 0,
                "best_score": 0
            }
        
        coins_earned = self.calculate_coins(score)
        self.player_profiles[name]["scores"].append(score)
        self.player_profiles[name]["total_coins"] += coins_earned
        self.player_profiles[name]["best_score"] = max(self.player_profiles[name]["best_score"], score)
        
        # Tangalarni yangilash
        if name not in self.player_coins:
            self.player_coins[name] = 0
        
        self.player_coins[name] += coins_earned

    def set_state(self, new_state):
        self.state = new_state

    def reset(self):
        self.score = 0
        self.player_name = ""
        self.summary_info = {}
