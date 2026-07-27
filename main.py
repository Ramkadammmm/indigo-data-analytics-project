import os
import sys

from generate_indigo_data import generate_dataset
from db.setup_db import setup_database
from src.data_loader import IndigoDataLoader
from src.stat_analysis import StatisticalAnalyzer
from src.nlp_analytics import NLPTextAnalytics
from src.excel_generator import IndigoExcelReportGenerator

def run_pipeline():
    print("=" * 70)
    print("INDIGO AIRLINES EXECUTIVE - DATA ANALYTICS PIPELINE")
    print("=" * 70)

    # 1. Dataset Generation & Ingestion Check
    csv_path = os.path.join(os.getcwd(), 'data', 'raw', 'indigo_flight_passenger_data.csv')
    if not os.path.exists(csv_path):
        print("\nStep 1: Generating 100,000 synthetic IndiGo flight & passenger records...")
        generate_dataset(num_records=100000)
    else:
        print("\nStep 1: Found raw dataset at data/raw/indigo_flight_passenger_data.csv.")

    # 2. Database Population & QA Audit
    print("\nStep 2: Initializing SQLite Relational Database & QA Governance Audits...")
    setup_database()

    # 3. Load Cleaned Dataset
    print("\nStep 3: Extracting merged dataset from database...")
    loader = IndigoDataLoader()
    df = loader.load_from_db()
    print(f"Loaded {len(df):,} passenger flight records for analysis.")

    # 4. Statistical Analysis & SPSS Modeling
    print("\nStep 4: Executing Univariate, Bivariate, Multivariate (PCA), & Regression Models...")
    stat_analyzer = StatisticalAnalyzer(df)
    univ_res = stat_analyzer.univariate_analysis()
    biv_res = stat_analyzer.bivariate_analysis()
    pca_res = stat_analyzer.multivariate_pca()
    logit_res = stat_analyzer.logistic_regression_model()

    print("\n--- Regression Insights ---")
    print(f"Detractor Prediction AUC-ROC Score: {logit_res['auc_roc']}")

    # 5. NLP Customer Text Feedback Mining
    print("\nStep 5: Running NLP Sentiment Analysis & TF-IDF Key Phrase Mining...")
    nlp_analyzer = NLPTextAnalytics(df)
    nlp_summary = nlp_analyzer.generate_nlp_summary()

    # 6. Executive Excel 365 Report Generation
    print("\nStep 6: Generating Executive Excel 365 Dashboard Report...")
    stat_summary = {
        'univariate': univ_res,
        'bivariate': biv_res
    }
    excel_gen = IndigoExcelReportGenerator(df, stat_summary, nlp_summary)
    report_path = excel_gen.generate_report()

    print("\n" + "=" * 70)
    print("SUCCESS: IndiGo Data Analytics Pipeline Execution Completed!")
    print(f"Excel Executive Dashboard saved to: {report_path}")
    print("To launch the Streamlit Web Dashboard, run:")
    print("  streamlit run dashboard/app.py")
    print("=" * 70)

if __name__ == '__main__':
    run_pipeline()
