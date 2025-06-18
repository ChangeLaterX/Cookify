"""
Application Startup Scripts.

This module handles the execution of startup scripts when FastAPI initializes.
It provides a centralized way to run data loading and caching operations.
"""

import logging
import asyncio
from typing import List, Callable, Awaitable

from .ingredient_file_manager import initialize_ingredient_file

logger = logging.getLogger(__name__)


class StartupScriptManager:
    """Manages the execution of startup scripts."""
    
    def __init__(self):
        self.scripts: List[Callable[[], Awaitable[bool]]] = []
        self.results: List[bool] = []
        
    def register_script(self, script: Callable[[], Awaitable[bool]]) -> None:
        """
        Register a startup script to be executed.
        
        Args:
            script: Async function that returns True if successful, False if failed
        """
        self.scripts.append(script)
        logger.info(f"Registered startup script: {script.__name__}")
    
    async def run_all_scripts(self) -> bool:
        """
        Execute all registered startup scripts.
        
        Returns:
            bool: True if all scripts succeeded, False if any failed
        """
        logger.info(f"Running {len(self.scripts)} startup scripts...")
        
        self.results = []
        all_successful = True
        
        for script in self.scripts:
            try:
                logger.info(f"Executing startup script: {script.__name__}")
                result = await script()
                self.results.append(result)
                
                if result:
                    logger.info(f"✅ Startup script {script.__name__} completed successfully")
                else:
                    logger.error(f"❌ Startup script {script.__name__} failed")
                    all_successful = False
                    
            except Exception as e:
                logger.error(f"❌ Startup script {script.__name__} raised exception: {str(e)}")
                self.results.append(False)
                all_successful = False
        
        if all_successful:
            logger.info("🎉 All startup scripts completed successfully")
        else:
            logger.warning("⚠️ Some startup scripts failed - check logs for details")
            
        return all_successful
    
    def get_script_results(self) -> List[bool]:
        """Get the results of the last script execution."""
        return self.results.copy()


# Global startup manager instance
startup_manager = StartupScriptManager()


def register_startup_scripts() -> None:
    """
    Register all startup scripts here.
    
    Add new scripts to this function as the application grows.
    """
    # Register ingredient file initialization
    startup_manager.register_script(initialize_ingredient_file)
    
    # TODO: Add more scripts here as needed
    # startup_manager.register_script(initialize_other_cache)
    # startup_manager.register_script(setup_background_tasks)


async def run_startup_scripts() -> bool:
    """
    Main function to execute all startup scripts.
    
    This should be called in the FastAPI startup event handler.
    
    Returns:
        bool: True if all scripts succeeded, False if any failed
    """
    try:
        # Register all scripts first
        register_startup_scripts()
        
        # Execute all registered scripts
        success = await startup_manager.run_all_scripts()
        
        logger.info("Startup scripts execution completed")
        return success
        
    except Exception as e:
        logger.error(f"Error during startup scripts execution: {str(e)}")
        return False


def get_startup_results() -> List[bool]:
    """
    Get the results of the startup scripts for monitoring.
    
    Returns:
        List[bool]: Results of each startup script execution
    """
    return startup_manager.get_script_results()


# Export public functions
__all__ = [
    "run_startup_scripts",
    "get_startup_results",
    "register_startup_scripts",
    "startup_manager"
]
