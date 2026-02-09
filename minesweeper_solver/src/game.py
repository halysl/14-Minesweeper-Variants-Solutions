
import logging
import time

logger = logging.getLogger(__name__)

class Game:
    def __init__(self, capturer, controller, solver):
        self.capturer = capturer
        self.controller = controller
        self.solver = solver
        self.running = True

    def run(self):
        logger.info("Game loop started.")
        while self.running:
            # 1. Capture Screen
            frame = self.capturer.capture()
            if frame is None:
                logger.warning("Failed to capture screen. Retrying...")
                time.sleep(1)
                continue

            # 2. Recognize Grid (TODO)
            # grid_state = self.recognizer.process(frame)

            # 3. Solve (TODO)
            # moves = self.solver.solve(grid_state)

            # 4. Execute Moves (TODO)
            # for move in moves:
            #     self.controller.execute(move)
            
            time.sleep(1) # Loop delay
