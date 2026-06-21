import pygame
from src.config import BG_GREEN, DARK_GREEN, LIGHT_GREEN, WHITE, BLACK, GRAY, RED, WIDTH, HEIGHT


class Leaderboard:
    """Leaderlar jadvali, ism kiritish va tanga yechib olish sahifasi."""
    COIN_TO_SOM = 1000

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
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.emoji_title_font = self.get_emoji_font(28)
        self.emoji_font = self.get_emoji_font(40)
        self.input_active = True
        self.withdraw_amount = 0
        self.withdraw_state = None
        self.withdraw_card_number = ""
        self.withdraw_message = ""
        self.message_timer = 0
        
    def get_emoji_font(self, size):
        for name in self.EMOJI_FONT_FALLBACKS:
            font = pygame.font.SysFont(name, size)
            if font and font.get_linesize() > 0:
                return font
        return pygame.font.SysFont(None, size)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.input_active:
                    if event.key == pygame.K_BACKSPACE:
                        self.manager.player_name = self.manager.player_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.manager.player_name:
                            # O'yinchini saqlash
                            self.manager.save_player_profile(self.manager.player_name, self.manager.score)
                            self.input_active = False
                    else:
                        if len(self.manager.player_name) < 15:
                            self.manager.player_name += event.unicode
                elif self.withdraw_state == "enter_card":
                    if event.key == pygame.K_BACKSPACE:
                        self.withdraw_card_number = self.withdraw_card_number[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        self.withdraw_state = None
                        self.withdraw_message = "Kartaga yechib olish bekor qilindi."
                        self.message_timer = 180
                    elif event.key == pygame.K_RETURN:
                        if len(self.withdraw_card_number) >= 12:
                            current_coins = self.manager.player_coins.get(self.manager.player_name, 0)
                            if current_coins > 0:
                                self.withdraw_amount = current_coins
                                self.manager.player_coins[self.manager.player_name] = 0
                                self.withdraw_message = f"✓ {self.withdraw_amount} tanga kartaga yechib olindi!"
                                self.message_timer = 300
                            else:
                                self.withdraw_message = "Sizda yetarli tanga yo'q."
                                self.message_timer = 180
                            self.withdraw_state = None
                            self.withdraw_card_number = ""
                        else:
                            self.withdraw_message = "Iltimos kartaning to'liq raqamini kiriting."
                            self.message_timer = 180
                    else:
                        if event.unicode.isdigit() and len(self.withdraw_card_number) < 19:
                            self.withdraw_card_number += event.unicode
                else:
                    if event.key == pygame.K_RETURN:
                        self.manager.score = 0
                        self.manager.player_name = ""
                        self.input_active = True
                        self.manager.set_state("MENU")

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                if self.input_active:
                    # Reyting ismini kiritish ko'rinishida
                    pass
                else:
                    # Chipta do'koni
                    if 50 <= x <= 280 and 380 <= y <= 470:
                        self.manager.set_state("SHOP")
                    
                    # Kartaga yechib olish (Withdraw)
                    if 320 <= x <= 550 and 380 <= y <= 470:
                        current_coins = self.manager.player_coins.get(self.manager.player_name, 0)
                        if current_coins > 0:
                            self.withdraw_state = "enter_card"
                            self.withdraw_card_number = ""
                            self.withdraw_message = "Kartangiz raqamini kiriting."
                            self.message_timer = 0
                        else:
                            self.withdraw_message = "Sizda yetarli tanga yo'q."
                            self.message_timer = 180
                    
                    # Bosh sahifaga qaytish
                    if 590 <= x <= 800 and 380 <= y <= 470:
                        self.manager.score = 0
                        self.manager.player_name = ""
                        self.input_active = True
                        self.manager.set_state("MENU")

    def draw(self, screen):
        screen.fill(BG_GREEN)

        if self.input_active:
            # ISM KIRITISH SAHIFASI
            lbl_input = pygame.font.SysFont("Arial", 26, bold=True).render("Ismingizni kiriting:", True, DARK_GREEN)
            screen.blit(lbl_input, (60, 140))

            pygame.draw.rect(screen, WHITE, (60, 200, 320, 50), border_radius=8)
            pygame.draw.rect(screen, DARK_GREEN, (60, 200, 320, 50), width=3, border_radius=8)

            name_surface = self.font.render(self.manager.player_name if self.manager.player_name else "_", True, BLACK)
            screen.blit(name_surface, (75, 212))

            lbl_hint = pygame.font.SysFont("Arial", 16).render("Yozing va ENTER tugmasini bosing", True, GRAY)
            screen.blit(lbl_hint, (60, 265))

            pygame.draw.rect(screen, LIGHT_GREEN, (500, 80, 450, 520), border_radius=15)
            lbl_board = pygame.font.SysFont("Arial", 28, bold=True).render("Ballar reytingi", True, WHITE)
            screen.blit(lbl_board, (650 - lbl_board.get_width() // 2, 100))

            # Foydalanuvchilar reytingi
            leaderboard_data = []
            
            # Oldindan saqlangan o'yinchilar
            if self.manager.player_profiles:
                sorted_players = sorted(
                    self.manager.player_profiles.items(),
                    key=lambda x: x[1]["best_score"],
                    reverse=True
                )
                for idx, (name, data) in enumerate(sorted_players[:3]):
                    coins = self.manager.player_coins.get(name, 0)
                    best_score = data.get("best_score", 0)
                    leaderboard_data.append((f"{idx+1}. {name}", f"{best_score} | {coins} tanga"))

            # Joriy o'yinchi
            if self.manager.player_name:
                leaderboard_data.append((f"{len(leaderboard_data)+1}. {self.manager.player_name} (Siz)", f"{self.manager.score} ball"))
            
            # Agar veri bo'lmasa, namuna ma'lumotlar
            if not leaderboard_data:
                leaderboard_data = [
                    ("1. Sardor", "540 | 10 tanga"),
                    ("2. Shahlo", "410 | 8 tanga"),
                    ("3. Botir", "320 | 6 tanga")
                ]

            offset_y = 170
            for name, score in leaderboard_data[:3]:
                pygame.draw.rect(screen, WHITE, (520, offset_y, 410, 50), border_radius=8)
                screen.blit(self.font.render(name, True, BLACK), (540, offset_y + 12))
                screen.blit(self.font.render(score, True, DARK_GREEN), (800, offset_y + 12))
                offset_y += 70

        else:
            # NATIJALAR VA TANGALAR SAHIFASI
            lbl_result = self.font_title.render(f"Tabriklaymiz, {self.manager.player_name}!", True, DARK_GREEN)
            screen.blit(lbl_result, (50, 30))

            # Ball ko'rsatish
            pygame.draw.rect(screen, DARK_GREEN, (50, 100, 350, 160), border_radius=15)
            
            score_label = pygame.font.SysFont("Arial", 22, bold=True).render("Bu o'yinda:", True, WHITE)
            screen.blit(score_label, (70, 120))
            
            score_value = pygame.font.SysFont("Arial", 40, bold=True).render(str(self.manager.score), True, WHITE)
            screen.blit(score_value, (160 - score_value.get_width() // 2, 150))
            
            score_word = pygame.font.SysFont("Arial", 18).render("ball", True, WHITE)
            screen.blit(score_word, (160 - score_word.get_width() // 2, 195))

            # Tangalarni hisoblash
            coins_earned = self.manager.calculate_coins(self.manager.score)
            total_coins = self.manager.player_coins.get(self.manager.player_name, 0)
            total_som = total_coins * self.COIN_TO_SOM
            
            # Tangalar ko'rsatish
            pygame.draw.rect(screen, (220, 170, 30), (450, 100, 350, 160), border_radius=15)
            
            coin_label = pygame.font.SysFont("Arial", 22, bold=True).render("Bu o'yinda olgan:", True, BLACK)
            screen.blit(coin_label, (470, 120))
            
            coin_value = pygame.font.SysFont("Arial", 40, bold=True).render(f"{coins_earned}", True, BLACK)
            screen.blit(coin_value, (625 - coin_value.get_width() // 2, 150))
            
            coin_word = pygame.font.SysFont("Arial", 18).render("tanga", True, BLACK)
            screen.blit(coin_word, (625 - coin_word.get_width() // 2, 195))

            # Jami tangalar panel
            pygame.draw.rect(screen, LIGHT_GREEN, (50, 280, 750, 80), border_radius=15)
            
            total_label = self.font_title.render(f"Jami yig'ilgan tangalar: {total_coins}", True, DARK_GREEN)
            screen.blit(total_label, (70, 305))
            som_label = self.font.render(f"Somda: {total_som} so'm", True, DARK_GREEN)
            screen.blit(som_label, (70, 340))

            # Chipta do'koni tugmasi
            pygame.draw.rect(screen, (220, 170, 30), (50, 380, 230, 90), border_radius=15)
            pygame.draw.rect(screen, (180, 140, 0), (50, 380, 230, 90), width=3, border_radius=15)
            shop_emoji = self.emoji_font.render("🚌", True, BLACK)
            screen.blit(shop_emoji, (135 - shop_emoji.get_width() // 2, 385))
            
            shop_label = self.font_small.render("Chipta do'koni", True, BLACK)
            screen.blit(shop_label, (135 - shop_label.get_width() // 2, 440))

            # Kartaga yechib olish (Withdraw) tugmasi
            pygame.draw.rect(screen, (100, 200, 100), (320, 380, 230, 90), border_radius=15)
            pygame.draw.rect(screen, (50, 150, 50), (320, 380, 230, 90), width=3, border_radius=15)
            withdraw_emoji = self.emoji_font.render("💳", True, WHITE)
            screen.blit(withdraw_emoji, (405 - withdraw_emoji.get_width() // 2, 385))
            
            withdraw_label = self.font_small.render("Kartaga yechib olish", True, WHITE)
            screen.blit(withdraw_label, (405 - withdraw_label.get_width() // 2, 440))

            # Bosh sahifaga qaytish tugmasi
            pygame.draw.rect(screen, DARK_GREEN, (590, 380, 210, 90), border_radius=15)
            menu_emoji = self.emoji_font.render("🏠", True, WHITE)
            screen.blit(menu_emoji, (695 - menu_emoji.get_width() // 2, 385))
            
            menu_label = self.font_small.render("Bosh sahifaga", True, WHITE)
            screen.blit(menu_label, (695 - menu_label.get_width() // 2, 440))

            if self.withdraw_state == "enter_card":
                # show card input prompt
                prompt_box = pygame.Rect(180, 500, 500, 60)
                pygame.draw.rect(screen, WHITE, prompt_box, border_radius=12)
                pygame.draw.rect(screen, DARK_GREEN, prompt_box, width=3, border_radius=12)
                prompt_text = self.font_small.render("Kartangiz raqamini kiriting va ENTER bosing:", True, BLACK)
                screen.blit(prompt_text, (prompt_box.x + 14, prompt_box.y + 8))
                card_text = self.font.render(self.withdraw_card_number or "_", True, BLACK)
                screen.blit(card_text, (prompt_box.x + 14, prompt_box.y + 30))
            
            # Yechib olish xabari
            if self.withdraw_message:
                if self.message_timer > 0:
                    self.message_timer -= 1
                msg_text = self.font.render(self.withdraw_message, True, DARK_GREEN if "✓" in self.withdraw_message else RED)
                pygame.draw.rect(screen, WHITE, (100, 560, WIDTH - 200, 50), border_radius=10)
                screen.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, 573))
                if self.message_timer == 0 and self.withdraw_state is None and "Kartangiz" not in self.withdraw_message:
                    self.withdraw_message = ""

            if self.withdraw_amount > 0 and self.withdraw_state is None:
                # show confirmation once
                withdraw_msg = f"✓ {self.withdraw_amount} tanga kartaga yechib olindi!"
                msg_text = self.font.render(withdraw_msg, True, DARK_GREEN)
                pygame.draw.rect(screen, WHITE, (100, 500, WIDTH - 200, 50), border_radius=10)
                screen.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, 513))
                self.withdraw_amount = 0
