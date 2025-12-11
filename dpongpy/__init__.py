from dpongpy.model import Pong, Config, Direction
from dpongpy.log import logger, logging
from dpongpy.view import ShowNothingPongView
from dpongpy.controller.local import ActionMap
import pygame
from dataclasses import dataclass, field
from typing import Optional, Collection, Iterable

#Classe delle impostazioni di gioco
@dataclass
class Settings:
    config: Config = field(default_factory=Config)
    debug: bool = False
    size: tuple = (800, 600)
    fps: int = 60
    host: Optional[str] = None
    port: Optional[int] = None
    initial_paddles: Collection[Direction] = (Direction.LEFT, Direction.RIGHT)
    gui: bool = True

#Classe principale del gioco Pong
class PongGame:
    def __init__(self, settings: Settings = None):
        self.settings = settings or Settings() # Usa le impostazioni di default se non fornite
        self.pong = Pong(
            size=self.settings.size,
            config=self.settings.config,
            paddles=self.settings.initial_paddles
        ) # Crea l'oggetto principale (Pong)
        self.dt = None #tempo trascorso tra un frame e l'altro
        self.view = self.create_view() if self.settings.gui else ShowNothingPongView(self.pong) 
        self.clock = pygame.time.Clock() # Orologio per gestire il framerate
        self.running = True # Flag per il ciclo principale
        self.controller = self.create_controller(self.settings.initial_paddles)
        if self.settings.debug:
            logger.setLevel(logging.DEBUG)

    def create_view(self): # Crea la vista del gioco
        from dpongpy.view import ScreenPongView
        return ScreenPongView(self.pong, debug=self.settings.debug)

    # Crea il controller del gioco
    def create_controller(game, paddle_commands: dict[Direction, ActionMap] | Iterable[Direction]):
        from dpongpy.controller.local import PongLocalController

        class Controller(PongLocalController):
            def __init__(self, paddle_commands):
                super().__init__(game.pong, paddle_commands)

            def on_game_over(this, _):
                game.stop()

        return Controller(paddle_commands)

    def before_run(self):
        pygame.init()

    def after_run(self):
        pygame.quit()

    def at_each_run(self):
        if self.settings.gui:
            pygame.display.flip()
    
    # Ciclo principale del gioco (game loop)
    def run(self):
        try:
            self.dt = 0
            self.before_run()
            while self.running:
                self.controller.handle_inputs(self.dt)
                self.controller.handle_events()
                self.view.render()
                self.at_each_run()
                self.dt = self.clock.tick(self.settings.fps) / 1000
        finally:
            self.after_run()

    def stop(self):
        self.running = False

# Funzione principale per avviare il gioco Pong
def main(settings = None):
    if settings is None:
        settings = Settings()
    PongGame(settings).run()
