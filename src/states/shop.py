import pygame
from src.config import BG_GREEN, DARK_GREEN, LIGHT_GREEN, WHITE, BLACK, GRAY, WIDTH, HEIGHT, BLUE, RED


class PublicTransportShop:
    """Jamoat transportlari uchun chipta do'koni - tangalar bilan chipta sotib olish."""
    
    # Do'kon mahsulotlari - Jamoat transportlari chipta turlari
    PRODUCTS = [
        {"id": 1, "name": "Markaziy metro chipta", "cost": 30, "emoji": "🚇", "desc": "1 kunli"},
        {"id": 2, "name": "Avtobusga chipta", "cost": 20, "emoji": "🚌", "desc": "1 yoqab"},
        {"id": 3, "name": "Tram chipta", "cost": 25, "emoji": "🚊", "desc": "1 yoqab"},
        {"id": 4, "name": "Po'yezd", "cost": 100, "emoji": "🚄", "desc": "Barcha transportga 1 kunlik"},
        {"id": 5, "name": "Hafta chipta", "cost": 150, "emoji": "📅", "desc": "Barcha transportga 1 hafta"},
    ]
    
    EMOJI_FONT_FALLBACKS = [
        "Segoe UI Emoji",
        "Segoe UI Symbol",
        "Apple Color Emoji",
        "Noto Color Emoji",
        "EmojiOne Mozilla",
        "Arial Unicode MS",
        "Symbola"
    ]

    def __init__(self, manager):
        self.manager = manager
        self.font_title = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_body = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.emoji_font = self.get_emoji_font(32)
        self.emoji_title_font = self.get_emoji_font(36)
        self.selected_product = 0
        self.bought_items = {name: [] for name in manager.player_profiles.keys()}
        self.purchase_message = ""
        self.message_timer = 0
        
    def get_emoji_font(self, size):
        for name in self.EMOJI_FONT_FALLBACKS:
            font = pygame.font.SysFont(name, size)
            if font and font.get_linesize() > 0:
                return font
        return pygame.font.SysFont(None, size)

    def handle_events(self, events):
        current_coins = self.manager.player_coins.get(self.manager.player_name, 0)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                # Reytingga qaytish
                if 750 <= x <= 970 and 560 <= y <= 610:
                    self.manager.set_state("LEADERBOARD")
                
                # Mahsulotni tanla
                for idx, rect in enumerate(self.get_product_rects()):
                    if rect.collidepoint(event.pos):
                        self.selected_product = idx
                        
                        # Sotib olish
                        product = self.PRODUCTS[idx]
                        if current_coins >= product["cost"]:
                            self.manager.player_coins[self.manager.player_name] -= product["cost"]
                            if self.manager.player_name not in self.bought_items:
                                self.bought_items[self.manager.player_name] = []
                            self.bought_items[self.manager.player_name].append(product["name"])
                            self.purchase_message = f"✓ {product['name']} sotib oldingiz!"
                            self.message_timer = 180  # 3 sekund
                        else:
                            need = product["cost"] - current_coins
                            self.purchase_message = f"✗ {need} tanga yetishmaydi!"
                            self.message_timer = 180
                        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.manager.set_state("LEADERBOARD")
    
    def get_product_rects(self):
        """Mahsulot ko'rinish pozitsiyalarini berish"""
        rects = []
        start_y = 140
        for i in range(len(self.PRODUCTS)):
            rect = pygame.Rect(80, start_y + i * 75, WIDTH - 160, 70)
            rects.append(rect)
        return rects
    
    def draw(self, screen):
        screen.fill(BG_GREEN)
        
        # Sarlavha
        title = self.emoji_title_font.render("🚌 Jamoat transportlari chipta do'koni", True, DARK_GREEN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
        
        # O'yinchi ma'lumotlari
        current_coins = self.manager.player_coins.get(self.manager.player_name, 0)
        profile_text = self.font_body.render(
            f"O'yinchi: {self.manager.player_name}  |  Tangalarim: {current_coins} tanga",
            True, DARK_GREEN
        )
        screen.blit(profile_text, (50, 70))
        
        # Mahsulotlarni chizish
        for idx, rect in enumerate(self.get_product_rects()):
            product = self.PRODUCTS[idx]
            
            # Tanlangan mahsulotni to'q rang bilan
            if idx == self.selected_product:
                pygame.draw.rect(screen, BLUE, rect, border_radius=10, width=4)
                pygame.draw.rect(screen, (200, 220, 255), rect, border_radius=10)
            else:
                pygame.draw.rect(screen, WHITE, rect, border_radius=10)
                pygame.draw.rect(screen, GRAY, rect, border_radius=10, width=2)
            
            # Emoji
            emoji = self.emoji_font.render(product["emoji"], True, BLACK)
            screen.blit(emoji, (rect.x + 15, rect.centery - 16))
            
            # Mahsulot nomi va tavsifi
            name_text = self.font_body.render(product["name"], True, DARK_GREEN)
            screen.blit(name_text, (rect.x + 65, rect.centery - 18))
            
            desc_text = self.font_small.render(product["desc"], True, GRAY)
            screen.blit(desc_text, (rect.x + 65, rect.centery + 8))
            
            # Narxi
            can_afford = current_coins >= product["cost"]
            cost_color = DARK_GREEN if can_afford else RED
            
            cost_text = self.font_body.render(f"{product['cost']} tanga", True, cost_color)
            screen.blit(cost_text, (WIDTH - 150, rect.centery - 10))
            
            # Sotib olgan yoki yo'q
            if self.manager.player_name in self.bought_items and product["name"] in self.bought_items[self.manager.player_name]:
                bought_badge = self.font_small.render("✓ Sotib oldingiz", True, DARK_GREEN)
                screen.blit(bought_badge, (WIDTH - 150, rect.centery + 15))
        
        # Xaridor xabari
        if self.message_timer > 0:
            self.message_timer -= 1
            msg_color = DARK_GREEN if "✓" in self.purchase_message else RED
            msg_text = self.font_body.render(self.purchase_message, True, msg_color)
            pygame.draw.rect(screen, WHITE, (100, 500, WIDTH - 200, 50), border_radius=10)
            screen.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, 513))
        
        # Reytingga qaytish tugmasi
        pygame.draw.rect(screen, DARK_GREEN, (750, 560, 220, 50), border_radius=10)
        back_text = self.font_small.render("Reytingga qaytish", True, WHITE)
        screen.blit(back_text, (860 - back_text.get_width() // 2, 575))
        
        # Ko'rsatma
        hint_text = self.font_small.render("Chiptani tanlang va bosing. ESC yoki tugmani bosish bilan qaytish mumkin.", True, GRAY)
        screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, 625))
