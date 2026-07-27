import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import IndigoDataLoader
from src.stat_analysis import StatisticalAnalyzer

@pytest.fixture(scope="module")
def sample_data():
    loader = IndigoDataLoader()
    return loader.load_from_db().head(1000)

def test_univariate_analysis(sample_data):
    analyzer = StatisticalAnalyzer(sample_data)
    univ_df = analyzer.univariate_analysis()
    
    assert 'total_revenue_inr' in univ_df.index
    assert 'skewness' in univ_df.columns
    assert 'kurtosis' in univ_df.columns

def test_bivariate_analysis(sample_data):
    analyzer = StatisticalAnalyzer(sample_data)
    biv_df = analyzer.bivariate_analysis()
    
    assert not biv_df.empty
    assert 'p_value' in biv_df.columns

def test_logistic_regression(sample_data):
    analyzer = StatisticalAnalyzer(sample_data)
    logit_res = analyzer.logistic_regression_model()
    
    assert 'auc_roc' in logit_res
    assert logit_res['auc_roc'] >= 0.5
