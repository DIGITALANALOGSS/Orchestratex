from ydata_quality import DataQuality
import pandas as pd
import numpy as np
import pytest
from orchestratex.config import get_settings

class TestDataQuality:
    @classmethod
    def setup_class(cls):
        settings = get_settings()
        cls.df = pd.read_parquet(settings.DATA_PATH + '/training_data.parquet')
        cls.dq = DataQuality(cls.df)

    def test_missing_values(self):
        report = self.dq.missing_values()
        assert report["total_missing"] == 0, "Missing values detected"

    def test_data_drift(self):
        reference = pd.read_parquet(settings.DATA_PATH + '/reference_data.parquet')
        drift_report = self.dq.calculate_drift(reference)
        assert drift_report["drift_score"] < 0.1, "Significant data drift detected"

    def test_bias_detection(self):
        from algorithm_audit import HBAC
        hbac = HBAC(self.df, bias_score="loan_approval_rate")
        clusters = hbac.find_biased_clusters()
        assert len(clusters) == 0, "Potential bias clusters detected"

    def test_data_distribution(self):
        """Test data distribution across different dimensions"""
        # Test language distribution
        lang_dist = self.df['language'].value_counts(normalize=True)
        assert len(lang_dist) >= 12, "Not enough languages represented"
        assert all(v >= 0.05 for v in lang_dist.values), "Language imbalance detected"

        # Test emotion distribution
        emotion_dist = self.df['emotion'].value_counts(normalize=True)
        assert len(emotion_dist) >= 7, "Not enough emotions represented"
        assert all(v >= 0.05 for v in emotion_dist.values), "Emotion imbalance detected"

    def test_time_series_consistency(self):
        """Test temporal consistency of data"""
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        time_series = self.df.set_index('timestamp')
        
        # Check for gaps in time series
        time_diff = time_series.index.to_series().diff()
        assert time_diff.max() < pd.Timedelta('1 day'), "Large gaps in time series"

    def test_data_quality_metrics(self):
        """Test various data quality metrics"""
        # Test confidence scores
        assert self.df['confidence_score'].mean() > 0.8, "Low average confidence"
        assert self.df['confidence_score'].std() < 0.2, "High confidence variance"

        # Test text length distribution
        text_lengths = self.df['text'].str.len()
        assert text_lengths.mean() > 50, "Text too short"
        assert text_lengths.std() < 100, "Text length variance too high"

    def test_data_validation(self):
        """Test data validation rules"""
        # Test language format
        assert all(self.df['language'].str.match(r'^[a-z]{2}-[A-Z]{2}$'))

        # Test timestamp format
        assert all(self.df['timestamp'].apply(lambda x: isinstance(x, pd.Timestamp)))

        # Test emotion format
        valid_emotions = {
            'happiness', 'sadness', 'anger', 'surprise', 'fear', 'disgust', 'neutral'
        }
        assert all(self.df['emotion'].isin(valid_emotions))

    def test_data_correlation(self):
        """Test correlations between features"""
        numeric_df = self.df.select_dtypes(include=['number'])
        corr_matrix = numeric_df.corr()
        
        # Check for high correlations that might indicate redundancy
        assert not any(
            corr_matrix.abs().where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
            .stack()
            .reset_index()
            .rename(columns={0: 'correlation'})
            .query('correlation > 0.9')
            .empty
        ), "High correlation between features detected"

    def test_data_outliers(self):
        """Test for outliers in numeric features"""
        numeric_df = self.df.select_dtypes(include=['number'])
        for col in numeric_df.columns:
            q1 = numeric_df[col].quantile(0.25)
            q3 = numeric_df[col].quantile(0.75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = numeric_df[(numeric_df[col] < lower_bound) | (numeric_df[col] > upper_bound)]
            assert len(outliers) / len(numeric_df) < 0.05, f"Too many outliers in {col}"

if __name__ == "__main__":
    pytest.main()
