import sys
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.core.config_manager import ConfigManager
from src.core.simulation_manager import SimulationManager
from src.core.data_manager import DataManager
from src.gui.main_window import MainWindow


def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("main")

    # Load configuration
    config_manager = ConfigManager()

    # Initialize core managers
    simulation_manager = SimulationManager(config_manager)
    data_manager = DataManager(config_manager)

    # Start Qt application
    app = QApplication(sys.argv)
    app.setApplicationName(config_manager.get('application.name', 'Autonomous Vehicle Simulator'))
    app.setStyle('Fusion')

    # Create and show main window
    main_window = MainWindow(config_manager, simulation_manager, data_manager)
    main_window.show()

    logger.info("Autonomous Vehicle Simulator started successfully")
    
    # Run the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 