
import sys
import logging
import argparse
from capture import WindowCapturer
from control import MouseController
from solver.basic import BasicSolver
from game import Game

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Minesweeper Solver")
    parser.add_argument("--variant", type=str, default="default", help="Game variant to solve")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.info(f"Starting Minesweeper Solver for variant: {args.variant}")

    try:
        # Initialize modules
        # TODO: Make window title configurable or auto-detect
        capture = WindowCapturer("14 Minesweeper Variants")
        controller = MouseController()
        logic = BasicSolver()
        game = Game(capture, controller, logic)
        
        # Run game loop
        # game.run() 
        logger.info("Project initialized. Run game.run() to start.")

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
