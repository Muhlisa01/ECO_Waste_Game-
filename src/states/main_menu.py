import pygame
import sys
from src.config import WIDTH, BG_GREEN, DARK_GREEN, RED, WHITE, BLACK


class MainMenu:
    """Bosh menyu sahifasi."""
    def __init__(self, manager):
        self.manager = manager
        self.font_title = pygame.font.SysFont("Arial", 60, bold=True)
        self.font_btn = pygame.font.SysFont("Arial", 26, bold=True)
        self.font_text = pygame.font.SysFont("Arial", 20)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 400 <= x <= 600 and 280 <= y <= 340:
                    self.manager.set_state("GAMEPLAY")
                elif 400 <= x <= 600 and 370 <= y <= 430:
                    pygame.quit()
                    sys.exit()

    def draw(self, screen):
        screen.fill(BG_GREEN)

        title = self.font_title.render("Chiqindilarni Saralang", True, DARK_GREEN)
        subtitle = self.font_text.render("Chiqindini to'g'ri qutiga joylashtirish", True, BLACK)
        hint = self.font_text.render("Chiqindini ushlab kerakli bin ustiga sudrab qo'ying.", True, BLACK)

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 190))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 230))

        pygame.draw.rect(screen, DARK_GREEN, (400, 280, 200, 60), border_radius=12)
        txt_start = self.font_btn.render("O'yinni boshlash", True, WHITE)
        screen.blit(txt_start, (500 - txt_start.get_width() // 2, 295))

        pygame.draw.rect(screen, RED, (400, 370, 200, 60), border_radius=12)
        txt_exit = self.font_btn.render("Chiqish", True, WHITE)
        screen.blit(txt_exit, (500 - txt_exit.get_width() // 2, 385))
