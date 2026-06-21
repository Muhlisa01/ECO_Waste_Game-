# main.py
import pygame
import sys
from src.config import WIDTH, HEIGHT, FPS
from src.game_states import GameStateManager, MainMenu, Gameplay, LevelSummary, Leaderboard, PublicTransportShop

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption("EcoSort: Chiqindilarni Saralash")
    clock = pygame.time.Clock()

    # Holatlar menejerini yuklaymiz
    manager = GameStateManager()
    
    # Sahifalarni ro'yxatga olamiz
    states = {
        "MENU": MainMenu(manager),
        "GAMEPLAY": Gameplay(manager),
        "LEVEL_SUMMARY": LevelSummary(manager),
        "LEADERBOARD": Leaderboard(manager),
        "SHOP": PublicTransportShop(manager)
    }

    running = True
    while running:
        clock.tick(FPS)
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # Joriydagi aktiv sahifa nomini olamiz
        current_state = manager.state
        
        # Hodisalarni o'sha aktiv sahifaga yuboramiz
        states[current_state].handle_events(events)

        # Agar o'yin oynasida bo'lsak, fondagi harakatlar yangilanadi
        if current_state == "GAMEPLAY":
            states[current_state].update()
        # Agar reyting sahifasida o'yin qayta boshlansa o'yinni reset qilamiz
        elif current_state == "MENU" and isinstance(states["GAMEPLAY"], Gameplay) and states["GAMEPLAY"].score > 0:
            states["GAMEPLAY"].reset_game()

        # Sahifani chizish
        states[current_state].draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()