import os
import sys
import pytest
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import IndigoDataLoader

def test_data_loader_db():
    loader = IndigoDataLoader()
    df = loader.load_from_db()
    
    assert not df.empty, "Loaded dataframe should not be empty."
    assert 'total_revenue_inr' in df.columns, "DataFrame must contain 'total_revenue_inr'."
    assert 'nps_category' in df.columns, "DataFrame must contain 'nps_category'."
    assert df['passenger_id'].nunique() == len(df), "All passenger_ids must be unique."

def test_feature_engineering():
    loader = IndigoDataLoader()
    df = loader.load_from_db()
    
    assert 'ancillary_ratio' in df.columns
    assert 'is_detractor' in df.columns
    assert df['ancillary_ratio'].between(0, 1).all()
