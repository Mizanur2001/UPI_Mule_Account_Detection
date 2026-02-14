"""
Data loading utilities with validation and error handling.
Supports relative paths from workspace root.
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from backend.utils.logger import get_logger

logger = get_logger("data_loader")


def _resolve_path(path: str) -> Path:
    """Resolve path relative to workspace root and validate existence."""
    file_path = Path(path)
    
    # If relative path, resolve from workspace root
    if not file_path.is_absolute():
        # Try resolving from current directory
        if not file_path.exists():
            # Try from parent directories to handle different execution contexts
            alt_path = Path(__file__).parent.parent.parent / path
            if alt_path.exists():
                file_path = alt_path
    
    return file_path


def load_transactions(path: str = "backend/data/transactions.csv") -> pd.DataFrame:
    """
    Load transactions CSV with validation.
    
    Args:
        path: Path to transactions.csv file
        
    Returns:
        DataFrame with transactions
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file can't be parsed
    """
    file_path = _resolve_path(path)
    
    if not file_path.exists():
        logger.error(f"Transactions file not found: {file_path}")
        raise FileNotFoundError(f"Transactions file not found: {path}")
    
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} transactions from {path}")
        return df
    except Exception as e:
        logger.error(f"Failed to parse transactions CSV: {e}")
        raise ValueError(f"Failed to parse transactions CSV: {e}")


def load_accounts(path: str = "backend/data/accounts.csv") -> pd.DataFrame:
    """
    Load accounts CSV with validation.
    
    Args:
        path: Path to accounts.csv file
        
    Returns:
        DataFrame with account metadata
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file can't be parsed
    """
    file_path = _resolve_path(path)
    
    if not file_path.exists():
        logger.error(f"Accounts file not found: {file_path}")
        raise FileNotFoundError(f"Accounts file not found: {path}")
    
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} accounts from {path}")
        return df
    except Exception as e:
        logger.error(f"Failed to parse accounts CSV: {e}")
        raise ValueError(f"Failed to parse accounts CSV: {e}")


def load_devices(path: str = "backend/data/devices.csv") -> pd.DataFrame:
    """
    Load devices CSV with validation.
    
    Args:
        path: Path to devices.csv file
        
    Returns:
        DataFrame with device information
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file can't be parsed
    """
    file_path = _resolve_path(path)
    
    if not file_path.exists():
        logger.error(f"Devices file not found: {file_path}")
        raise FileNotFoundError(f"Devices file not found: {path}")
    
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} devices from {path}")
        return df
    except Exception as e:
        logger.error(f"Failed to parse devices CSV: {e}")
        raise ValueError(f"Failed to parse devices CSV: {e}")