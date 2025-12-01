#!/usr/bin/env python3
"""
ROBO - Crypto Robot Parameter Sweeper
Main executable for running parameter sweeps across multiple strategies and cryptocurrencies.
"""

import argparse
from robo.config import CRYPTOCURRENCIES, STRATEGY_PARAMS, BACKTEST_CONFIG
from robo.data_fetcher import DataFetcher
from robo.backtester import Backtester
from robo.parameter_sweeper import ParameterSweeper
from robo.visualization import (
    print_summary_report,
    save_results_to_csv,
    plot_strategy_comparison,
    plot_top_strategies
)


def main():
    """Main entry point for the parameter sweeper."""
    parser = argparse.ArgumentParser(
        description='Sweep through strategy parameters for crypto trading'
    )
    parser.add_argument(
        '--strategies',
        nargs='+',
        default=list(STRATEGY_PARAMS.keys()),
        choices=list(STRATEGY_PARAMS.keys()),
        help='Strategies to test'
    )
    parser.add_argument(
        '--cryptos',
        nargs='+',
        default=CRYPTOCURRENCIES,
        help='Cryptocurrencies to test'
    )
    parser.add_argument(
        '--period',
        default=BACKTEST_CONFIG['data_period'],
        help='Historical data period (e.g., 1y, 6mo)'
    )
    parser.add_argument(
        '--interval',
        default=BACKTEST_CONFIG['data_interval'],
        help='Data interval (e.g., 1d, 1h)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=BACKTEST_CONFIG['initial_capital'],
        help='Initial capital for backtesting'
    )
    parser.add_argument(
        '--commission',
        type=float,
        default=BACKTEST_CONFIG['commission'],
        help='Commission rate per trade'
    )
    parser.add_argument(
        '--output',
        default='results.csv',
        help='Output CSV filename'
    )
    parser.add_argument(
        '--no-plots',
        action='store_true',
        help='Skip generating plots'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("ROBO - Crypto Robot Parameter Sweeper")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Strategies: {', '.join(args.strategies)}")
    print(f"  Cryptocurrencies: {', '.join(args.cryptos)}")
    print(f"  Period: {args.period}")
    print(f"  Interval: {args.interval}")
    print(f"  Initial Capital: ${args.capital:,.2f}")
    print(f"  Commission: {args.commission*100:.2f}%")
    
    # Step 1: Fetch data
    print("\n" + "="*80)
    print("STEP 1: Fetching historical data")
    print("="*80)
    
    fetcher = DataFetcher()
    data_dict = fetcher.fetch_multiple(args.cryptos, args.period, args.interval)
    
    if not data_dict:
        print("\nError: No data could be fetched. Exiting.")
        return
    
    print(f"\nSuccessfully fetched data for {len(data_dict)} cryptocurrencies:")
    for symbol, data in data_dict.items():
        print(f"  {symbol}: {len(data)} data points from {data.index[0]} to {data.index[-1]}")
    
    # Step 2: Run parameter sweep
    print("\n" + "="*80)
    print("STEP 2: Running parameter sweep")
    print("="*80)
    
    backtester = Backtester(initial_capital=args.capital, commission=args.commission)
    sweeper = ParameterSweeper(backtester)
    
    for strategy_name in args.strategies:
        if strategy_name not in STRATEGY_PARAMS:
            print(f"\nWarning: Unknown strategy '{strategy_name}', skipping...")
            continue
        
        param_ranges = STRATEGY_PARAMS[strategy_name]
        sweeper.sweep(strategy_name, param_ranges, data_dict, verbose=True)
    
    # Step 3: Generate reports
    print("\n" + "="*80)
    print("STEP 3: Generating reports")
    print("="*80)
    
    # Print summary report
    print_summary_report(sweeper)
    
    # Save results to CSV
    save_results_to_csv(sweeper, args.output)
    
    # Generate plots
    if not args.no_plots:
        print("\nGenerating visualizations...")
        
        try:
            # Strategy comparison plot
            df = sweeper.results_to_dataframe()
            fig = plot_strategy_comparison(df)
            if fig:
                fig.savefig('strategy_comparison.png', dpi=150, bbox_inches='tight')
                print("  Saved: strategy_comparison.png")
            
            # Top strategies plot
            best_results = sweeper.get_best_results(n=15, metric='total_return')
            if best_results:
                plt = plot_top_strategies(best_results, n=15)
                plt.savefig('top_strategies.png', dpi=150, bbox_inches='tight')
                print("  Saved: top_strategies.png")
        
        except Exception as e:
            print(f"  Warning: Could not generate plots: {e}")
    
    print("\n" + "="*80)
    print("SWEEP COMPLETE!")
    print("="*80)


if __name__ == '__main__':
    main()
