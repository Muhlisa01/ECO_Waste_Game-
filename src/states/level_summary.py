import pygame
from src.config import BG_GREEN, DARK_GREEN, LIGHT_GREEN, BLUE, WHITE, BLACK


class LevelSummary:
    """Daraja yakuni va ekologik faktlar paneli."""
    def __init__(self, manager):
        self.manager = manager
        self.font_title = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_body = pygame.font.SysFont("Arial", 22)
        self.font_small = pygame.font.SysFont("Arial", 18)
        self.font_btn = pygame.font.SysFont("Arial", 24, bold=True)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 400 <= x <= 620 and 480 <= y <= 540:
                    self.manager.set_state("LEADERBOARD")

    def draw(self, screen):
        screen.fill(BG_GREEN)

        pygame.draw.rect(screen, WHITE, (60, 120, 420, 320), border_radius=18)
        title_fact = self.font_title.render("Bilasizmi?", True, DARK_GREEN)
        screen.blit(title_fact, (90, 140))

        fact_1 = self.font_body.render("- Plastik idishlar yillar davomida qoladi.", True, BLACK)
        fact_2 = self.font_body.render("- Qog'ozni saralash daraxtlarni saqlaydi.", True, BLACK)
        fact_3 = self.font_body.render("- Organik chiqindilar kompost bo'lishi mumkin.", True, BLACK)
        screen.blit(fact_1, (90, 220))
        screen.blit(fact_2, (90, 270))
        screen.blit(fact_3, (90, 320))

        pygame.draw.rect(screen, LIGHT_GREEN, (90, 360, 360, 60), border_radius=12)
        msg = self.font_small.render("O'yin oxirida natijangizni ko'rishingiz mumkin.", True, BLACK)
        screen.blit(msg, (100, 380))

        pygame.draw.rect(screen, BLUE, (520, 160, 420, 310), border_radius=18)
        total_label = self.font_title.render(str(self.manager.summary_info.get("total_score", 0)), True, WHITE)
        screen.blit(total_label, (720 - total_label.get_width() // 2, 185))

        score_text = self.font_body.render("Umumiy ball:", True, WHITE)
        screen.blit(score_text, (560, 260))
        lvl_text = self.font_body.render(f"Daraja ball: {self.manager.summary_info.get('level_score', 0)}", True, WHITE)
        screen.blit(lvl_text, (560, 300))
        bonus_text = self.font_body.render(f"Bonus ball: {self.manager.summary_info.get('bonus', 0)}", True, WHITE)
        screen.blit(bonus_text, (560, 340))
        time_text = self.font_body.render(f"Vaqt: {self.manager.summary_info.get('time', 0)} soniya", True, WHITE)
        screen.blit(time_text, (560, 380))
        detail_text = self.font_small.render(f"To'g'ri: {self.manager.summary_info.get('correct', 0)}, noto'g'ri: {self.manager.summary_info.get('wrong', 0)}", True, WHITE)
        screen.blit(detail_text, (560, 420))

        pygame.draw.rect(screen, DARK_GREEN, (400, 480, 220, 60), border_radius=12)
        txt_next = self.font_btn.render("Reytingni ko'rish", True, WHITE)
        screen.blit(txt_next, (510 - txt_next.get_width() // 2, 496))

    def show_fallback_window(self):
        try:
            import tkinter as tk
            from tkinter import messagebox

            info = self.manager.summary_info
            text = (
                f"Umumiy ball: {info.get('total_score', 0)}\n"
                f"Daraja ball: {info.get('level_score', 0)}\n"
                f"Bonus: {info.get('bonus', 0)}\n"
                f"Vaqt: {info.get('time', 0)} soniya\n"
                f"To'g'ri: {info.get('correct', 0)}, noto'g'ri: {info.get('wrong', 0)}"
            )
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("O'yin natijalari", text)
            root.destroy()
        except Exception:
            pass
