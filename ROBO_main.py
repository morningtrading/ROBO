#!/usr/bin/env python3
"""
ROBO Trading System - Main Entry Point
======================================
"""

import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.ROBO_logger import get_logger
from utils.ROBO_data_loader import ROBODataLoader
from utils.ROBO_validators import ConfigValidator
from ROBO_backtester import ROBOBacktester

logger = get_logger()


def load_config(config_path):
    """Load YAML configuration file"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config {config_path}: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description='ROBO Trading System')
    parser.add_argument('--strategy-config', 
                        default='config/ROBO_strategy_config.yaml',
                        help='Path to strategy configuration')
    parser.add_argument('--coins-config', 
                        default='config/ROBO_coins_config.yaml',
                        help='Path to coins configuration')
    parser.add_argument('--test', 
                        action='store_true',
                        help='Test mode - run on single coin only')
    args = parser.parse_args()
    
    # Display banner
    print("\n" + "="*80)
    print("ROBO TRADING SYSTEM".center(80))
    print("Advanced Algorithmic Trading Engine".center(80))
    print("="*80 + "\n")
    
    try:
        # Load configurations
        logger.info("Loading configurations...")
        strategy_config = load_config(args.strategy_config)
        coins_config = load_config(args.coins_config)
        
        # Validate configuration
        validator = ConfigValidator()
        if not validator.validate_strategy_config(strategy_config):
            logger.error("Configuration validation failed")
            return 1
        
        # Load market data
        data_loader = ROBODataLoader(coins_config['data_directory'])
        coins = coins_config['coins']
        
        if args.test:
            coins = [coins[0]]
            logger.info("TEST MODE - Running on single coin only")
        
        market_data = data_loader.load_all_coins(coins)
        
        if not market_data:
            logger.error("No market data loaded. Exiting.")
            return 1
        
        # Run backtests
        logger.info(f"Running backtests on {len(market_data)} coins...")
        backtester = ROBOBacktester(strategy_config)
        results = backtester.run_all(market_data)
        
        # Display results
        backtester.display_results(results)
        
        # Save results if configured
        if strategy_config['output']['save_results']:
            output_dir = Path(strategy_config['output']['results_dir'])
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = output_dir / f"ROBO_results_{timestamp}.csv"
            
            backtester.save_results(results, results_file)
            logger.info(f"Results saved to {results_file}")
        
        logger.info("ROBO Trading System completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
