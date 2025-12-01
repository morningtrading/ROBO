"""
Visualization and reporting utilities.
"""

import pandas as pd
import matplotlib.pyplot as plt
from typing import List
from .backtester import BacktestResult


def plot_top_strategies(results: List[BacktestResult], n: int = 10, metric: str = 'total_return'):
    """
    Plot top N strategies by a given metric.
    
    Args:
        results: List of BacktestResults
        n: Number of top strategies to plot
        metric: Metric to plot ('total_return', 'sharpe_ratio', etc.)
    """
    # Sort results
    sorted_results = sorted(results, key=lambda x: getattr(x, metric), reverse=True)[:n]
    
    # Prepare data
    labels = [f"{r.strategy_name}\n{r.symbol}\n{r.params}" for r in sorted_results]
    values = [getattr(r, metric) for r in sorted_results]
    
    # Create plot
    plt.figure(figsize=(12, 8))
    plt.barh(range(len(labels)), values)
    plt.yticks(range(len(labels)), labels, fontsize=8)
    plt.xlabel(metric.replace('_', ' ').title())
    plt.title(f'Top {n} Strategy Configurations by {metric.replace("_", " ").title()}')
    plt.tight_layout()
    
    return plt


def plot_strategy_comparison(df: pd.DataFrame):
    """
    Plot comparison of strategies across different metrics.
    
    Args:
        df: DataFrame with backtest results
    """
    if df.empty:
        print("No results to plot")
        return None
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot 1: Average return by strategy
    strategy_returns = df.groupby('strategy')['total_return'].mean().sort_values()
    axes[0, 0].barh(strategy_returns.index, strategy_returns.values)
    axes[0, 0].set_xlabel('Average Return (%)')
    axes[0, 0].set_title('Average Return by Strategy')
    
    # Plot 2: Average Sharpe ratio by strategy
    strategy_sharpe = df.groupby('strategy')['sharpe_ratio'].mean().sort_values()
    axes[0, 1].barh(strategy_sharpe.index, strategy_sharpe.values)
    axes[0, 1].set_xlabel('Average Sharpe Ratio')
    axes[0, 1].set_title('Average Sharpe Ratio by Strategy')
    
    # Plot 3: Win rate by strategy
    strategy_winrate = df.groupby('strategy')['win_rate'].mean().sort_values()
    axes[1, 0].barh(strategy_winrate.index, strategy_winrate.values)
    axes[1, 0].set_xlabel('Win Rate (%)')
    axes[1, 0].set_title('Average Win Rate by Strategy')
    
    # Plot 4: Performance by cryptocurrency
    symbol_returns = df.groupby('symbol')['total_return'].mean().sort_values()
    axes[1, 1].barh(symbol_returns.index, symbol_returns.values)
    axes[1, 1].set_xlabel('Average Return (%)')
    axes[1, 1].set_title('Average Return by Cryptocurrency')
    
    plt.tight_layout()
    return fig


def print_summary_report(sweeper):
    """
    Print a comprehensive summary report.
    
    Args:
        sweeper: ParameterSweeper instance with results
    """
    print("\n" + "="*80)
    print("PARAMETER SWEEP SUMMARY REPORT")
    print("="*80)
    
    if not sweeper.results:
        print("No results available.")
        return
    
    print(f"\nTotal tests performed: {len(sweeper.results)}")
    
    # Overall best results
    print("\n" + "-"*80)
    print("TOP 10 BEST PERFORMING CONFIGURATIONS (by Total Return)")
    print("-"*80)
    
    best_results = sweeper.get_best_results(n=10, metric='total_return')
    for i, result in enumerate(best_results, 1):
        print(f"\n{i}. {result}")
        print(f"   Parameters: {result.params}")
        print(f"   Win Rate: {(result.winning_trades/result.total_trades*100) if result.total_trades > 0 else 0:.2f}%")
        print(f"   Max Drawdown: {result.max_drawdown:.2f}%")
    
    # Best by Sharpe ratio
    print("\n" + "-"*80)
    print("TOP 5 BEST PERFORMING CONFIGURATIONS (by Sharpe Ratio)")
    print("-"*80)
    
    best_sharpe = sweeper.get_best_results(n=5, metric='sharpe_ratio')
    for i, result in enumerate(best_sharpe, 1):
        print(f"{i}. {result}")
        print(f"   Parameters: {result.params}")
    
    # Strategy summary
    print("\n" + "-"*80)
    print("PERFORMANCE BY STRATEGY")
    print("-"*80)
    print(sweeper.get_summary_by_strategy())
    
    # Symbol summary
    print("\n" + "-"*80)
    print("PERFORMANCE BY CRYPTOCURRENCY")
    print("-"*80)
    print(sweeper.get_summary_by_symbol())
    
    print("\n" + "="*80)


def save_results_to_csv(sweeper, filename: str = "results.csv"):
    """
    Save all results to a CSV file.
    
    Args:
        sweeper: ParameterSweeper instance
        filename: Output filename
    """
    df = sweeper.results_to_dataframe()
    df.to_csv(filename, index=False)
    print(f"\nResults saved to {filename}")
