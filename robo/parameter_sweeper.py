"""
Parameter sweeper for testing multiple strategy configurations.
"""

import itertools
import pandas as pd
from typing import Dict, List, Any
from .strategies import create_strategy
from .backtester import Backtester, BacktestResult


class ParameterSweeper:
    """Sweeps through strategy parameter combinations."""
    
    def __init__(self, backtester: Backtester):
        """
        Initialize parameter sweeper.
        
        Args:
            backtester: Backtester instance to use
        """
        self.backtester = backtester
        self.results = []
    
    def generate_param_combinations(self, param_ranges: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """
        Generate all combinations of parameters.
        
        Args:
            param_ranges: Dictionary mapping parameter names to lists of values
            
        Returns:
            List of parameter dictionaries
        """
        keys = list(param_ranges.keys())
        values = list(param_ranges.values())
        
        combinations = []
        for combo in itertools.product(*values):
            combinations.append(dict(zip(keys, combo)))
        
        return combinations
    
    def sweep(
        self,
        strategy_name: str,
        param_ranges: Dict[str, List[Any]],
        data_dict: Dict[str, pd.DataFrame],
        verbose: bool = True
    ) -> List[BacktestResult]:
        """
        Sweep through parameter combinations for a strategy across multiple assets.
        
        Args:
            strategy_name: Name of the strategy to test
            param_ranges: Dictionary of parameter ranges
            data_dict: Dictionary mapping symbols to price data
            verbose: Whether to print progress
            
        Returns:
            List of BacktestResults
        """
        param_combinations = self.generate_param_combinations(param_ranges)
        
        if verbose:
            print(f"\nSweeping {strategy_name} with {len(param_combinations)} parameter combinations "
                  f"across {len(data_dict)} cryptocurrencies...")
            print(f"Total tests: {len(param_combinations) * len(data_dict)}")
        
        results = []
        total_tests = len(param_combinations) * len(data_dict)
        test_count = 0
        
        for params in param_combinations:
            for symbol, data in data_dict.items():
                test_count += 1
                
                if verbose and test_count % 10 == 0:
                    print(f"Progress: {test_count}/{total_tests} tests completed...")
                
                try:
                    # Create strategy with parameters
                    strategy = create_strategy(strategy_name, params)
                    
                    # Run backtest
                    result = self.backtester.backtest(strategy, data, symbol)
                    results.append(result)
                    
                except Exception as e:
                    if verbose:
                        print(f"Error testing {strategy_name} with {params} on {symbol}: {e}")
        
        self.results.extend(results)
        
        if verbose:
            print(f"Completed {test_count} tests!")
        
        return results
    
    def get_best_results(self, n: int = 10, metric: str = 'total_return') -> List[BacktestResult]:
        """
        Get the top N best results based on a metric.
        
        Args:
            n: Number of results to return
            metric: Metric to sort by ('total_return', 'sharpe_ratio', etc.)
            
        Returns:
            List of top N BacktestResults
        """
        sorted_results = sorted(
            self.results,
            key=lambda x: getattr(x, metric),
            reverse=True
        )
        return sorted_results[:n]
    
    def results_to_dataframe(self) -> pd.DataFrame:
        """
        Convert all results to a pandas DataFrame.
        
        Returns:
            DataFrame with all backtest results
        """
        if not self.results:
            return pd.DataFrame()
        
        data = [result.to_dict() for result in self.results]
        return pd.DataFrame(data)
    
    def get_summary_by_strategy(self) -> pd.DataFrame:
        """
        Get summary statistics grouped by strategy.
        
        Returns:
            DataFrame with aggregated statistics per strategy
        """
        df = self.results_to_dataframe()
        
        if df.empty:
            return df
        
        summary = df.groupby('strategy').agg({
            'total_return': ['mean', 'std', 'max', 'min'],
            'sharpe_ratio': ['mean', 'max'],
            'win_rate': 'mean',
            'total_trades': 'mean',
        }).round(2)
        
        return summary
    
    def get_summary_by_symbol(self) -> pd.DataFrame:
        """
        Get summary statistics grouped by cryptocurrency.
        
        Returns:
            DataFrame with aggregated statistics per symbol
        """
        df = self.results_to_dataframe()
        
        if df.empty:
            return df
        
        summary = df.groupby('symbol').agg({
            'total_return': ['mean', 'std', 'max', 'min'],
            'sharpe_ratio': ['mean', 'max'],
            'win_rate': 'mean',
            'total_trades': 'mean',
        }).round(2)
        
        return summary
