import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score

class StatisticalAnalyzer:
    def __init__(self, df):
        self.df = df.copy()

    def univariate_analysis(self, columns=None):
        """Univariate statistical distribution metrics: Mean, Std, Skewness, Kurtosis, Normality."""
        if columns is None:
            columns = ['total_revenue_inr', 'departure_delay_min', 'arrival_delay_min', 'overall_satisfaction', 'nps_score']
            
        results = {}
        for col in columns:
            series = self.df[col].dropna()
            stat, p_val = stats.shapiro(series.iloc[:5000])  # Sampled for performance
            results[col] = {
                'count': len(series),
                'mean': round(series.mean(), 2),
                'std': round(series.std(), 2),
                'median': round(series.median(), 2),
                'iqr': round(series.quantile(0.75) - series.quantile(0.25), 2),
                'skewness': round(series.skew(), 3),
                'kurtosis': round(series.kurtosis(), 3),
                'shapiro_stat': round(stat, 4),
                'shapiro_p_value': round(p_val, 5),
                'is_normal': p_val > 0.05
            }
        return pd.DataFrame(results).T

    def bivariate_analysis(self):
        """Bivariate Hypothesis Tests: T-Test, One-Way ANOVA, and Chi-Square."""
        bivariate_results = {}
        
        # 1. Independent T-Test: Satisfaction between Economy vs IndiGo Stretch
        econ_sat = self.df[self.df['cabin_class'] == 'Economy']['overall_satisfaction']
        stretch_sat = self.df[self.df['cabin_class'] == 'IndiGo Stretch (Business)']['overall_satisfaction']
        t_stat, t_pval = stats.ttest_ind(econ_sat, stretch_sat, equal_var=False)
        bivariate_results['T-Test (Cabin Class vs Satisfaction)'] = {
            'test_name': 'Welch Independent T-Test',
            'stat': round(t_stat, 4),
            'p_value': round(t_pval, 6),
            'significant': t_pval < 0.05
        }

        # 2. One-Way ANOVA: Arrival Delay across Fleet Types
        fleet_groups = [group['arrival_delay_min'].values for _, group in self.df.groupby('fleet_type')]
        f_stat, f_pval = stats.f_oneway(*fleet_groups)
        bivariate_results['ANOVA (Fleet Type vs Arrival Delay)'] = {
            'test_name': 'One-Way ANOVA',
            'stat': round(f_stat, 4),
            'p_value': round(f_pval, 6),
            'significant': f_pval < 0.05
        }

        # 3. Chi-Square Test: Cabin Class vs NPS Category
        contingency_tab = pd.crosstab(self.df['cabin_class'], self.df['nps_category'])
        chi2, chi_pval, dof, _ = stats.chi2_contingency(contingency_tab)
        bivariate_results['Chi-Square (Cabin Class vs NPS Category)'] = {
            'test_name': 'Chi-Square Test of Independence',
            'stat': round(chi2, 4),
            'p_value': round(chi_pval, 6),
            'dof': dof,
            'significant': chi_pval < 0.05
        }
        return pd.DataFrame(bivariate_results).T

    def multivariate_pca(self, n_components=2):
        """Multivariate Analysis: Principal Component Analysis (PCA) on survey dimensions."""
        rating_cols = ['checkin_rating', 'crew_rating', 'punctuality_rating', 'cleanliness_rating']
        X = self.df[rating_cols].dropna()
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        pca = PCA(n_components=n_components)
        components = pca.fit_transform(X_scaled)
        
        explained_var = pca.explained_variance_ratio_
        loadings = pd.DataFrame(pca.components_.T, columns=[f'PC{i+1}' for i in range(n_components)], index=rating_cols)
        
        return {
            'explained_variance_ratio': explained_var,
            'total_explained_variance': round(sum(explained_var) * 100, 2),
            'loadings': loadings
        }

    def multivariate_clustering(self, n_clusters=3):
        """K-Means Customer Segmentation based on spend and flight distance."""
        features = ['total_revenue_inr', 'distance_km', 'overall_satisfaction']
        X = self.df[features].dropna()
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        self.df['cluster'] = clusters
        cluster_summary = self.df.groupby('cluster')[features].mean().round(2)
        return cluster_summary

    def linear_regression_model(self):
        """OLS Linear Regression modeling arrival delay drivers."""
        model = smf.ols('arrival_delay_min ~ departure_delay_min + distance_km + C(fleet_type)', data=self.df).fit()
        return {
            'r_squared': round(model.rsquared, 4),
            'adj_r_squared': round(model.rsquared_adj, 4),
            'f_statistic': round(model.fvalue, 2),
            'f_pvalue': round(model.f_pvalue, 6),
            'summary_table': model.summary2().tables[1]
        }

    def logistic_regression_model(self):
        """Logistic Regression for predicting Detractor (Low NPS) Probability."""
        df_log = self.df.dropna(subset=['is_detractor', 'arrival_delay_min', 'checkin_rating', 'crew_rating', 'punctuality_rating'])
        
        features = ['arrival_delay_min', 'checkin_rating', 'crew_rating', 'punctuality_rating']
        X = df_log[features]
        y = df_log['is_detractor']
        
        X_const = sm.add_constant(X)
        logit_model = sm.Logit(y, X_const).fit(disp=False)
        
        # Calculate odds ratios
        params = logit_model.params
        conf = logit_model.conf_int()
        conf['Odds Ratio'] = params
        conf.columns = ['2.5%', '97.5%', 'Odds Ratio']
        odds_ratios = np.exp(conf)
        
        # Predictions & AUC
        preds = logit_model.predict(X_const)
        auc = roc_auc_score(y, preds)
        
        return {
            'auc_roc': round(auc, 4),
            'pseudo_r2': round(logit_model.prsquared, 4),
            'odds_ratios': odds_ratios.round(3),
            'summary_table': logit_model.summary2().tables[1]
        }

if __name__ == '__main__':
    from src.data_loader import IndigoDataLoader
    df = IndigoDataLoader().load_from_db()
    analyzer = StatisticalAnalyzer(df)
    print("\n=== UNIVARIATE ANALYSIS ===")
    print(analyzer.univariate_analysis())
    print("\n=== BIVARIATE ANALYSIS ===")
    print(analyzer.bivariate_analysis())
    print("\n=== LOGISTIC REGRESSION (DETRACTOR PREDICTION) ===")
    log_res = analyzer.logistic_regression_model()
    print(f"AUC-ROC: {log_res['auc_roc']}")
    print(log_res['odds_ratios'])
