import pygame
from src.config import BG_GREEN, DARK_GREEN, LIGHT_GREEN, WHITE, BLACK, GRAY, WIDTH, HEIGHT


class Medals:
    """Tangalarni ko'rish va tanlash sahifasi."""
    
    # Medal raqamlari va atamalari
    MEDAL_NAMES = {
        0: "🥉 Bronza",
        1: "🥈 Kumush",
        2: "🥇 Oltin",
        3: "⭐ Yulduz",
        4: "💎 Almaz"
    }
    
    MEDAL_COLORS = {
        0: (205, 127, 50),    # Bronza
        1: (192, 192, 192),   # Kumush
        2: (255, 215, 0),     # Oltin
        3: (255, 165, 0),     # Yulduz (apelsin)
        4: (0, 255, 255)      # Almaz (ko'k)
    }
    
    MEDAL_THRESHOLDS = {
        0: 100,
        1: 300,
        2: 600,
        3: 1000,
        4: 1500
    }
    
    def __init__(self, manager):
        self.manager = manager
        self.font_title = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_body = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.selected_medal = 0
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                # Reyting sahifasiga qaytish
                if 850 <= x <= 970 and 580 <= y <= 630:
                    self.manager.set_state("LEADERBOARD")
                
                # Medal tanla
                for idx, rect in enumerate(self.get_medal_rects()):
                    if rect.collidepoint(event.pos):
                        self.selected_medal = idx
                        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.manager.set_state("LEADERBOARD")
    
    def get_medal_rects(self):
        """Medal ko'rinish pozitsiyalarini berish"""
        rects = []
        start_y = 150
        for i in range(5):
            rect = pygame.Rect(100, start_y + i * 80, WIDTH - 200, 70)
            rects.append(rect)
        return rects
    
    def draw_medal_icon(self, surface, medal_type, x, y, size=50):
        """Tanga ikon chizish"""
        color = self.MEDAL_COLORS.get(medal_type, DARK_GREEN)
        pygame.draw.circle(surface, color, (x, y), size // 2)
        pygame.draw.circle(surface, WHITE, (x, y), size // 2 - 3, width=2)
        
        # Tanga ichiga raqam
        font = pygame.font.SysFont("Arial", 24, bold=True)
        num_text = font.render(str(medal_type + 1), True, WHITE)
        surface.blit(num_text, (x - num_text.get_width() // 2, y - num_text.get_height() // 2))
    
    def draw(self, screen):
        screen.fill(BG_GREEN)
        
        # Sarlavha
        title = self.font_title.render("Tangalar", True, DARK_GREEN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
        
        # O'yinchi ism va tangasini ko'rsatish
        player_medals = self.manager.medals.get(self.manager.player_name, [])
        profile_text = self.font_body.render(
            f"O'yinchi: {self.manager.player_name} | Tangalar: {len(player_medals)}",
            True, DARK_GREEN
        )
        screen.blit(profile_text, (50, 80))
        
        # Medallarni ko'rsatish
        for idx, rect in enumerate(self.get_medal_rects()):
            # Fon
            color = self.MEDAL_COLORS.get(idx, DARK_GREEN)
            
            # Tanlangan medalni to'q rang bilan
            if idx == self.selected_medal:
                pygame.draw.rect(screen, color, rect, border_radius=12, width=4)
                pygame.draw.rect(screen, (200, 200, 200), rect, border_radius=12)
            else:
                pygame.draw.rect(screen, WHITE, rect, border_radius=12)
                pygame.draw.rect(screen, GRAY, rect, border_radius=12, width=2)
            
            # Medal ikon
            self.draw_medal_icon(screen, idx, rect.x + 60, rect.centery, size=50)
            
            # Medalnomini
            medal_name = self.MEDAL_NAMES.get(idx, "")
            name_text = self.font_body.render(medal_name, True, BLACK)
            screen.blit(name_text, (rect.x + 130, rect.centery - 20))
            
            # Shartni
            threshold = self.MEDAL_THRESHOLDS.get(idx, 0)
            condition = f"Shart: {threshold}+ ball"
            cond_text = self.font_small.render(condition, True, GRAY)
            screen.blit(cond_text, (rect.x + 130, rect.centery + 15))
            
            # Erishgan yoki yo'q
            if idx < len(player_medals):
                status = "✓ Erishdingiz"
                status_color = DARK_GREEN
            else:
                status = "Erishmadinggiz"
                status_color = RED
            
            status_text = self.font_small.render(status, True, status_color)
            screen.blit(status_text, (WIDTH - 250, rect.centery - 10))
        
        # Reytingga qaytish tugmasi
        pygame.draw.rect(screen, DARK_GREEN, (850, 580, 120, 50), border_radius=10)
        back_text = self.font_small.render("Reytingga", True, WHITE)
        screen.blit(back_text, (910 - back_text.get_width() // 2, 595))
        
        # Tanlangan medalnomining batafsil
        detail_panel_y = HEIGHT - 100
        pygame.draw.rect(screen, LIGHT_GREEN, (50, detail_panel_y, WIDTH - 100, 80), border_radius=12)
        
        selected_medal_name = self.MEDAL_NAMES.get(self.selected_medal, "")
        selected_threshold = self.MEDAL_THRESHOLDS.get(self.selected_medal, 0)
        
        detail_text = self.font_body.render(
            f"{selected_medal_name} - {selected_threshold} balldan o'ng",
            True, DARK_GREEN
        )
        screen.blit(detail_text, (70, detail_panel_y + 15))
        
        hint_text = self.font_small.render(
            "Medalni tanlash uchun uning ustiga bosing. ESC yoki 'Reytingga' bosish bilan qaytish mumkin.",
            True, BLACK
        )
        screen.blit(hint_text, (70, detail_panel_y + 50))
