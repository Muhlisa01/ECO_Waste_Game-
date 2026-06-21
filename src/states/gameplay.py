import os
import random
import pygame
from src.config import WIDTH, HEIGHT, BG_GREEN, DARK_GREEN, LIGHT_GREEN, WHITE, BLACK, RED
from src.waste_items import get_allowed_categories, get_random_waste, CATEGORY_NAMES, COLOR_MAP


class Gameplay:
    """Chiqindilarni sudrab saralash o'yini."""
    def __init__(self, manager):
        self.manager = manager
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_item = pygame.font.SysFont("Arial", 26, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 18)
        self.asset_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "images"))
        self.waste_images = {}
        self.image_map = self.prepare_image_map()
        self.active_waste_items = []
        self.current_drag_item = None
        self.main_menu_button = pygame.Rect(WIDTH - 160, HEIGHT - 200, 140, 40)
        self.reset_game()

    def normalize_name(self, text):
        normalized = "".join(ch.lower() if ch.isalnum() else "_" for ch in text)
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_")

    def prepare_image_map(self):
        image_map = {}
        if not os.path.isdir(self.asset_dir):
            return image_map
        for filename in os.listdir(self.asset_dir):
            path = os.path.join(self.asset_dir, filename)
            if not os.path.isfile(path):
                continue
            stem, ext = os.path.splitext(filename)
            if ext.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
                continue
            key = self.normalize_name(stem)
            image_map[key] = path
        return image_map

    CATEGORY_IMAGE_FALLBACK = {
        "Plastic": ["plastic", "plastik"],
        "Paper": ["paper", "qog_oz", "jurnal", "gazeta"],
        "Glass": ["glass", "shisha", "gloz"],
        "Food": ["food", "organik", "banan", "baliq"],
        "Garbage": ["garbage", "axlat", "quti"]
    }

    WASTE_IMAGE_ALIASES = {
        "Shokolad qog'ozi": ["paper", "shokolad", "qog_oz"],
        "Gazeta varaqasi": ["gazeta", "jurnal", "paper"],
        "Kitobdan parchasi": ["kitob", "book", "paper"],
        "Plastik suv shishasi": ["plastik", "shishasi", "bottle"],
        "Konserva bankasi": ["plastik", "konserva", "bankasi"],
        "Yog'li idish": ["idish", "plastik", "food"],
        "Shisha banka": ["shisha", "glass", "banka"],
        "Sharob shishasi": ["shisha", "glass", "sharob"],
        "Kosmetika shishasi": ["shisha", "glass", "kosmetika"],
        "Meva po'stlog'i": ["banan", "food", "organik"],
        "Choy qoldiqlari": ["food", "organik", "choy"],
        "Pitsa qutisi": ["quti", "food", "paper"],
        "Eskirgan mato": ["garbage", "axlat", "mato"],
        "Niqob qog'ozi": ["paper", "qog_oz", "niqob"],
        "Chiqindiga aylangan idish": ["idish", "garbage", "axlat"]
    }

    def make_waste_icon(self, item):
        size = 96
        icon = pygame.Surface((size, size), pygame.SRCALPHA)
        color = COLOR_MAP.get(item["category"], DARK_GREEN)
        pygame.draw.circle(icon, color, (size // 2, size // 2), size // 2 - 2)
        if item["category"] == "Plastic":
            pygame.draw.rect(icon, WHITE, (size // 2 - 10, size // 2 - 18, 20, 34), border_radius=6)
            pygame.draw.circle(icon, WHITE, (size // 2 + 4, size // 2 - 22), 6)
        elif item["category"] == "Paper":
            pygame.draw.polygon(icon, WHITE, [(size // 2 - 18, size // 2 + 16), (size // 2 + 18, size // 2 + 16), (size // 2 + 18, size // 2 - 16), (size // 2 - 18, size // 2 - 16)])
            pygame.draw.line(icon, color, (size // 2 - 12, size // 2 - 6), (size // 2 + 14, size // 2 - 6), 4)
        elif item["category"] == "Glass":
            pygame.draw.polygon(icon, WHITE, [(size // 2 - 16, size // 2 + 18), (size // 2 + 16, size // 2 + 18), (size // 2 + 12, size // 2 - 18), (size // 2 - 12, size // 2 - 18)])
            pygame.draw.line(icon, color, (size // 2 - 8, size // 2 - 8), (size // 2 + 8, size // 2 - 8), 4)
        elif item["category"] == "Food":
            pygame.draw.polygon(icon, WHITE, [(size // 2, size // 2 - 24), (size // 2 + 20, size // 2 + 12), (size // 2 - 20, size // 2 + 12)])
            pygame.draw.circle(icon, color, (size // 2, size // 2 + 18), 8)
        else:
            pygame.draw.rect(icon, WHITE, (size // 2 - 18, size // 2 - 10, 36, 32), border_radius=8)
            pygame.draw.line(icon, color, (size // 2 - 12, size // 2 - 4), (size // 2 + 12, size // 2 + 10), 5)
            pygame.draw.line(icon, color, (size // 2 + 12, size // 2 - 4), (size // 2 - 12, size // 2 + 10), 5)
        return icon

    def load_image(self, image_path):
        if not os.path.exists(image_path):
            return None

        try:
            image = pygame.image.load(image_path)
        except pygame.error:
            return None

        if pygame.display.get_surface() is not None:
            try:
                if image.get_alpha() is not None:
                    image = image.convert_alpha()
                else:
                    image = image.convert()
            except pygame.error:
                pass

        # Auto-detect simple solid backgrounds and make them transparent.
        if image.get_alpha() is None:
            bg_color = image.get_at((0, 0))
            if bg_color.a == 255:
                image.set_colorkey(bg_color)
                image = image.convert_alpha()

        return image

    def tokenize_name(self, text):
        return [word for word in self.normalize_name(text).split("_") if word and len(word) > 1]

    def get_waste_image(self, item):
        key = item["label"]
        if key in self.waste_images:
            return self.waste_images[key]

        normalized_label = self.normalize_name(item["label"])
        normalized_category = self.normalize_name(item["category"])

        # exact name or category match first
        for search_key in [normalized_label, normalized_category]:
            path = self.image_map.get(search_key)
            if path:
                image = self.load_image(path)
                if image:
                    self.waste_images[key] = image
                    return image

        label_tokens = self.tokenize_name(item["label"])
        fallback_keys = [self.normalize_name(x) for x in self.CATEGORY_IMAGE_FALLBACK.get(item["category"], [])]
        alias_tokens = [self.normalize_name(x) for x in self.WASTE_IMAGE_ALIASES.get(item["label"], [])]

        for alias_key in alias_tokens:
            path = self.image_map.get(alias_key)
            if path:
                image = self.load_image(path)
                if image:
                    self.waste_images[key] = image
                    return image

        best_match = None
        best_score = 0
        for image_key, path in self.image_map.items():
            score = 0
            if normalized_category in image_key:
                score += 2
            for token in label_tokens:
                if token in image_key:
                    score += 2
            for fallback in fallback_keys:
                if fallback in image_key:
                    score += 1
            for alias in alias_tokens:
                if alias in image_key:
                    score += 2
            if normalized_label in image_key or image_key in normalized_label:
                score += 3
            if score > best_score:
                best_score = score
                best_match = path

        if best_match and best_score > 0:
            image = self.load_image(best_match)
            if image:
                self.waste_images[key] = image
                return image

        self.waste_images[key] = None
        return None

    def draw_background(self, screen):
        top = pygame.Rect(0, 0, WIDTH, HEIGHT)
        for i in range(HEIGHT // 2):
            ratio = i / (HEIGHT // 2)
            sky_color = (175 + int(35 * ratio), 225 + int(20 * ratio), 235 + int(10 * ratio))
            pygame.draw.line(screen, sky_color, (0, i), (WIDTH, i))
        pygame.draw.rect(screen, (66, 179, 95), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
        hill_color = (106, 176, 102)
        pygame.draw.ellipse(screen, hill_color, (-120, HEIGHT // 2 - 40, WIDTH // 2 + 160, HEIGHT // 2 + 80))
        pygame.draw.ellipse(screen, hill_color, (WIDTH // 2 - 200, HEIGHT // 2 - 80, WIDTH // 2 + 240, HEIGHT // 2 + 120))
        pygame.draw.circle(screen, (255, 241, 118), (WIDTH - 100, 100), 48)

    def reset_game(self):
        self.score = 0
        self.correct = 0
        self.wrong = 0
        self.lives = 5
        self.level = 1
        self.rounds = 0
        self.start_time = pygame.time.get_ticks()
        self.notification = "O'yinni boshlash uchun chiqindini ushlang."
        self.notification_color = DARK_GREEN
        self.notification_timer = 0
        self.dragging = False
        self.waste_radius = 42
        self.waste_pos = [WIDTH // 2, 240]
        self.waste_item = None
        self.drag_offset = [0, 0]
        self.current_drag_item = None
        self.summary_saved = False
        # phases: 'collect' -> collect several wastes; 'sort' -> sort collected wastes
        self.phase = 'collect'
        self.collected_items = []
        self.sort_index = 0
        self.active_waste_items = []
        self.spawn_waste()

    def get_collect_target(self):
        if self.level == 1:
            return 3
        if self.level == 2:
            return 4
        return 5

    def spawn_waste(self):
        # If we are in the sorting phase, show the next collected item to sort
        if self.phase == 'sort' and 0 <= self.sort_index < len(self.collected_items):
            self.waste_item = self.collected_items[self.sort_index]
            self.waste_pos = [WIDTH // 2, 240]
            self.waste_offset = [0, 0]
            self.waste_image = self.get_waste_image(self.waste_item)
        else:
            self.waste_item = None
            self.waste_image = None
            self.current_drag_item = None
            self.spawn_collect_items()

    def create_collect_item(self):
        item = get_random_waste(self.level)
        image = self.get_waste_image(item)
        x = random.randint(100, WIDTH - 100)
        y = random.randint(140, HEIGHT - 220)
        return {
            "item": item,
            "pos": [x, y],
            "image": image,
            "radius": 42,
            "drag_offset": [0, 0]
        }

    def spawn_collect_items(self):
        target_count = max(self.get_collect_target() + 2, 5)
        while len(self.active_waste_items) < target_count:
            self.active_waste_items.append(self.create_collect_item())

    def ensure_collect_items(self):
        if self.phase != 'collect':
            return
        target_count = max(self.get_collect_target() + 2, 5)
        while len(self.active_waste_items) < target_count:
            self.active_waste_items.append(self.create_collect_item())

    def get_bin_layout(self):
        categories = get_allowed_categories(self.level)
        bin_width = 140
        gap = 20
        total = len(categories) * bin_width + (len(categories) - 1) * gap
        start_x = WIDTH // 2 - total // 2
        y = HEIGHT - 140
        bins = []
        for idx, name in enumerate(categories):
            rect = pygame.Rect(start_x + idx * (bin_width + gap), y, bin_width, 100)
            bins.append((name, rect))
        return bins

    def get_collect_rect(self):
        # fixed collect area on the left bottom
        return pygame.Rect(20, HEIGHT - 140, 140, 100)

    def set_notification(self, text, color, time_ms=1800):
        self.notification = text
        self.notification_color = color
        self.notification_timer = time_ms

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.phase == 'collect' and self.main_menu_button.collidepoint(event.pos):
                    self.manager.set_state("MENU")
                    return
                if self.phase == 'collect':
                    for item_data in reversed(self.active_waste_items):
                        dx = event.pos[0] - item_data['pos'][0]
                        dy = event.pos[1] - item_data['pos'][1]
                        if dx * dx + dy * dy <= item_data['radius'] * item_data['radius']:
                            self.current_drag_item = item_data
                            self.current_drag_item['drag_offset'] = [item_data['pos'][0] - event.pos[0], item_data['pos'][1] - event.pos[1]]
                            break
                else:
                    dx = event.pos[0] - self.waste_pos[0]
                    dy = event.pos[1] - self.waste_pos[1]
                    if dx * dx + dy * dy <= self.waste_radius * self.waste_radius:
                        self.dragging = True
                        self.drag_offset = [self.waste_pos[0] - event.pos[0], self.waste_pos[1] - event.pos[1]]

            elif event.type == pygame.MOUSEMOTION:
                if self.phase == 'collect' and self.current_drag_item is not None:
                    self.current_drag_item['pos'][0] = event.pos[0] + self.current_drag_item['drag_offset'][0]
                    self.current_drag_item['pos'][1] = event.pos[1] + self.current_drag_item['drag_offset'][1]
                elif self.dragging:
                    self.waste_pos[0] = event.pos[0] + self.drag_offset[0]
                    self.waste_pos[1] = event.pos[1] + self.drag_offset[1]

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.phase == 'collect' and self.current_drag_item is not None:
                    self.check_drop(event.pos, self.current_drag_item)
                    self.current_drag_item = None
                elif self.dragging:
                    self.dragging = False
                    self.check_drop(event.pos)

    def check_drop(self, pos, dragged_item=None):
        # If in collect phase, dropping on the collect area collects the waste
        if self.phase == 'collect' and dragged_item is not None:
            collect_rect = self.get_collect_rect()
            if collect_rect.collidepoint(pos):
                self.collected_items.append(dragged_item['item'])
                self.active_waste_items.remove(dragged_item)
                self.set_notification(f"To'plandi: {dragged_item['item']['label']}", LIGHT_GREEN, 1200)
                if len(self.collected_items) >= self.get_collect_target():
                    self.phase = 'sort'
                    self.sort_index = 0
                    self.set_notification('Saralash bosqichi boshlandi!', DARK_GREEN, 1800)
                    self.spawn_waste()
                else:
                    self.ensure_collect_items()
                return
            self.set_notification("Chiqindini to'plang — collect qutisiga tashlang!", (180, 90, 0), 1600)
            return

        # In sort phase, check bins
        for name, rect in self.get_bin_layout():
            if rect.collidepoint(pos):
                if name == self.waste_item["category"]:
                    self.mark_correct(name)
                else:
                    self.mark_incorrect(name)
                return
        self.set_notification("Chiqindini qutiga tashlang!", (180, 90, 0), 1600)

    def mark_correct(self, bin_name):
        self.score += 20
        # In sort phase we count correctness per item; only increment 'correct' and 'rounds' when sorting
        if self.phase == 'sort':
            self.correct += 1
            self.rounds += 1
        self.manager.score = self.score
        self.set_notification(f"To'g'ri! {CATEGORY_NAMES[bin_name]}ga +20 ball", DARK_GREEN)

        # advance to next collected item or spawn a new collect item
        if self.phase == 'sort':
            self.sort_index += 1
            if self.sort_index >= len(self.collected_items):
                # finished sorting this batch
                self.collected_items = []
                self.phase = 'collect'
                self.set_notification('Yana chiqindilar to‘plang!', LIGHT_GREEN, 1600)
                self.spawn_waste()
            else:
                self.spawn_waste()

        self.check_level_progression()
        self.check_game_over()

    def mark_incorrect(self, bin_name):
        # penalize
        if self.phase == 'sort':
            self.wrong += 1
            self.rounds += 1
        self.lives -= 1
        self.score = max(0, self.score - 5)
        self.manager.score = self.score
        self.set_notification(f"Noto'g'ri! {self.waste_item['label']} noto'g'ri binada. -5 ball", RED)

        # advance similarly to correct
        if self.phase == 'sort':
            self.sort_index += 1
            if self.sort_index >= len(self.collected_items):
                self.collected_items = []
                self.phase = 'collect'
                self.set_notification('Yana chiqindilar to‘plang!', LIGHT_GREEN, 1600)
                self.spawn_waste()
            else:
                self.spawn_waste()

        self.check_level_progression()
        self.check_game_over()

    def check_level_progression(self):
        if self.level == 1 and self.correct >= 5:
            self.level = 2
            self.set_notification("Daraja 2: organik chiqindilar qo'shildi!", LIGHT_GREEN, 2200)
        elif self.level == 2 and self.correct >= 10:
            self.level = 3
            self.set_notification("Daraja 3: murakkabroq chiqindilar. Diqqat!", LIGHT_GREEN, 2200)

    def check_game_over(self):
        if self.lives <= 0 or self.rounds >= 12:
            self.finish_level()

    def finish_level(self):
        if self.summary_saved:
            return
        elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        bonus = max(0, 100 - elapsed * 2) + self.lives * 5
        self.manager.summary_info = {
            "total_score": self.score,
            "level_score": self.score,
            "bonus": bonus,
            "time": elapsed,
            "correct": self.correct,
            "wrong": self.wrong,
            "level": self.level,
            "message": "Ajoyib!" if self.wrong == 0 else f"{self.wrong} noto'g'ri qutish bor.",
        }
        self.manager.score = self.score
        self.summary_saved = True
        self.manager.set_state("LEVEL_SUMMARY")

    def update(self):
        if self.notification_timer > 0:
            self.notification_timer -= 1000 // 60
            if self.notification_timer <= 0:
                self.notification_color = DARK_GREEN

    def draw(self, screen):
        self.draw_background(screen)

        pygame.draw.rect(screen, DARK_GREEN, (20, 20, 180, 40), border_radius=8)
        lbl_lvl = self.font.render(f"Daraja {self.level}", True, WHITE)
        screen.blit(lbl_lvl, (30, 26))

        lbl_score = self.font.render(f"Ball: {self.score}", True, BLACK)
        screen.blit(lbl_score, (WIDTH - 170, 26))

        lbl_lives = self.font.render(f"Hayot: {'❤️' * self.lives}", True, RED)
        screen.blit(lbl_lives, (WIDTH - 340, 26))

        pygame.draw.rect(screen, WHITE, (20, 80, WIDTH - 40, 40), border_radius=10)
        pygame.draw.rect(screen, self.notification_color, (22, 82, WIDTH - 44, 36), border_radius=8)
        txt_notify = self.font_small.render(self.notification, True, WHITE)
        screen.blit(txt_notify, (30, 90))

        if self.phase == 'sort' and self.waste_item is not None:
            shadow_rect = pygame.Rect(self.waste_pos[0] - 48, self.waste_pos[1] - 28, 96, 20)
            pygame.draw.ellipse(screen, (0, 0, 0, 40), shadow_rect)
            if self.waste_image:
                scaled = pygame.transform.smoothscale(self.waste_image, (96, 96))
                screen.blit(scaled, (self.waste_pos[0] - scaled.get_width() // 2, self.waste_pos[1] - scaled.get_height() // 2))
            else:
                icon = self.make_waste_icon(self.waste_item)
                screen.blit(icon, (self.waste_pos[0] - icon.get_width() // 2, self.waste_pos[1] - icon.get_height() // 2))

        if self.phase == 'collect':
            instruction = self.font_small.render("Chiqindilarni to'plang: suring va to'plang.", True, BLACK)
            screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 360))
            collect_rect = self.get_collect_rect()
            pygame.draw.rect(screen, WHITE, collect_rect, border_radius=8)
            pygame.draw.rect(screen, LIGHT_GREEN, collect_rect, width=4, border_radius=8)
            label = self.font.render("To'plang", True, BLACK)
            screen.blit(label, (collect_rect.centerx - label.get_width() // 2, collect_rect.y + 12))
            count_txt = self.font_small.render(f"{len(self.collected_items)}/{self.get_collect_target()}", True, BLACK)
            screen.blit(count_txt, (collect_rect.centerx - count_txt.get_width() // 2, collect_rect.y + 42))

            pygame.draw.rect(screen, WHITE, self.main_menu_button, border_radius=10)
            pygame.draw.rect(screen, BLACK, self.main_menu_button, width=2, border_radius=10)
            menu_label = self.font_small.render("Bosh sahifaga", True, BLACK)
            screen.blit(menu_label, (self.main_menu_button.centerx - menu_label.get_width() // 2, self.main_menu_button.centery - menu_label.get_height() // 2))

            for item_data in self.active_waste_items:
                shadow_rect = pygame.Rect(item_data['pos'][0] - 48, item_data['pos'][1] - 28, 96, 20)
                pygame.draw.ellipse(screen, (0, 0, 0, 40), shadow_rect)
                if item_data['image']:
                    scaled = pygame.transform.smoothscale(item_data['image'], (96, 96))
                    screen.blit(scaled, (item_data['pos'][0] - scaled.get_width() // 2, item_data['pos'][1] - scaled.get_height() // 2))
                else:
                    icon = self.make_waste_icon(item_data['item'])
                    screen.blit(icon, (item_data['pos'][0] - icon.get_width() // 2, item_data['pos'][1] - icon.get_height() // 2))
        else:
            instruction = self.font_small.render("Chiqindini mos qutiga torting.", True, BLACK)
            screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 360))

            for name, rect in self.get_bin_layout():
                pygame.draw.rect(screen, WHITE, rect, border_radius=8)
                pygame.draw.rect(screen, COLOR_MAP.get(name, BLACK), rect, width=4, border_radius=8)
                label = self.font.render(CATEGORY_NAMES[name], True, BLACK)
                screen.blit(label, (rect.centerx - label.get_width() // 2, rect.y + 16))
                subtitle = self.font_small.render("Bin", True, BLACK)
                screen.blit(subtitle, (rect.centerx - subtitle.get_width() // 2, rect.y + 42))

        if self.wrong > 0:
            error_text = self.font_small.render(f"So'nggi xato: {self.wrong} marta noto'g'ri qutildi.", True, RED)
            screen.blit(error_text, (20, HEIGHT - 170))
