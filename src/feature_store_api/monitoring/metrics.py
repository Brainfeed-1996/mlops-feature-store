"""
Monitoring and metrics for feature store.
"""

import time
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import numpy as np
from scipy import stats


@dataclass
class MetricsCollector:
    """Collect and export feature store metrics."""
    
    ingestion_count: int = 0
    ingestion_errors: int = 0
    materialization_count: int = 0
    materialization_duration: float = 0.0
    online_requests: int = 0
    online_latency_sum: float = 0.0
    drift_checks: int = 0
    quality_checks: int = 0
    
    def record_ingestion(self, success: bool = True):
        """Record an ingestion operation."""
        self.ingestion_count += 1
        if not success:
            self.ingestion_errors += 1
    
    def record_materialization(self, duration: float):
        """Record a materialization operation."""
        self.materialization_count += 1
        self.materialization_duration += duration
    
    def record_online_request(self, latency: float):
        """Record an online retrieval."""
        self.online_requests += 1
        self.online_latency_sum += latency
    
    def record_drift_check(self):
        """Record a drift check."""
        self.drift_checks += 1
    
    def record_quality_check(self):
        """Record a quality check."""
        self.quality_checks += 1
    
    def get_summary(self) -> Dict:
        """Get metrics summary."""
        avg_latency = (
            self.online_latency_sum / self.online_requests 
            if self.online_requests > 0 else 0
        )
        
        return {
            "ingestion": {
                "total": self.ingestion_count,
                "errors": self.ingestion_errors,
                "error_rate": (
                    self.ingestion_errors / self.ingestion_count 
                    if self.ingestion_count > 0 else 0
                )
            },
            "materialization": {
                "total": self.materialization_count,
                "total_duration_seconds": self.materialization_duration,
                "avg_duration_seconds": (
                    self.materialization_duration / self.materialization_count
                    if self.materialization_count > 0 else 0
                )
            },
            "online": {
                "total_requests": self.online_requests,
                "avg_latency_seconds": avg_latency
            },
            "monitoring": {
                "drift_checks": self.drift_checks,
                "quality_checks": self.quality_checks
            }
        }
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        summary = self.get_summary()
        
        lines = [
            "# HELP feature_store_ingestion_total Total number of feature ingestions",
            f"feature_store_ingestion_total {summary['ingestion']['total']}",
            f"feature_store_ingestion_errors {summary['ingestion']['errors']}",
            "",
            "# HELP feature_store_materialization_total Total number of materializations",
            f"feature_store_materialization_total {summary['materialization']['total']}",
            f"feature_store_materialization_duration_seconds {summary['materialization']['total_duration_seconds']}",
            "",
            "# HELP feature_store_online_requests_total Total online feature requests",
            f"feature_store_online_requests_total {summary['online']['total_requests']}",
            f"feature_store_online_latency_seconds {summary['online']['avg_latency_seconds']}",
            "",
            "# HELP feature_store_drift_checks_total Total drift checks performed",
            f"feature_store_drift_checks_total {summary['monitoring']['drift_checks']}",
            f"feature_store_quality_checks_total {summary['monitoring']['quality_checks']}",
        ]
        
        return "\n".join(lines)


class DriftDetector:
    """Statistical drift detection for features."""
    
    def __init__(self, method: str = "kl_divergence", threshold: float = 0.5):
        """
        Initialize drift detector.
        
        Args:
            method: Drift detection method ('kl_divergence', 'ks_test', 'wasserstein')
            threshold: Drift threshold (0.0 - 1.0)
        """
        self.method = method
        self.threshold = threshold
        self.reference_data: Dict[str, np.ndarray] = {}
    
    def set_reference(self, name: str, data: np.ndarray):
        """Set reference data for a feature."""
        self.reference_data[name] = data
    
    def detect(
        self,
        name: str,
        current_data: np.ndarray
    ) -> Dict:
        """
        Detect drift between current and reference data.
        
        Args:
            name: Feature name
            current_data: Current feature values
            
        Returns:
            Drift analysis result
        """
        if name not in self.reference_data:
            return {
                "name": name,
                "drift_detected": False,
                "score": 0.0,
                "message": "No reference data, cannot detect drift"
            }
        
        reference = self.reference_data[name]
        
        # Calculate drift score
        if self.method == "kl_divergence":
            score = self._kl_divergence(reference, current_data)
        elif self.method == "ks_test":
            score = self._ks_test(reference, current_data)
        elif self.method == "wasserstein":
            score = self._wasserstein(reference, current_data)
        else:
            score = 0.0
        
        drift_detected = score > self.threshold
        
        return {
            "name": name,
            "drift_detected": drift_detected,
            "score": round(score, 4),
            "method": self.method,
            "threshold": self.threshold,
            "reference_mean": float(np.mean(reference)),
            "current_mean": float(np.mean(current_data)),
            "reference_std": float(np.std(reference)),
            "current_std": float(np.std(current_data)),
            "severity": self._severity(score),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def detect_all(self, current_data: Dict[str, np.ndarray]) -> Dict:
        """
        Detect drift for all features.
        
        Args:
            current_data: Current feature values
            
        Returns:
            Dictionary of drift results
        """
        results = {}
        for name, data in current_data.items():
            results[name] = self.detect(name, data)
        
        # Summary
        drift_count = sum(1 for r in results.values() if r["drift_detected"])
        
        return {
            "features": results,
            "summary": {
                "total_features": len(results),
                "drift_detected_count": drift_count,
                "drift_rate": drift_count / len(results) if results else 0,
                "overall_drift_score": (
                    sum(r["score"] for r in results.values()) / len(results)
                    if results else 0
                )
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _kl_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """Calculate KL divergence."""
        # Histogram-based KL divergence
        bins = 50
        p_hist, _ = np.histogram(p, bins=bins, density=True)
        q_hist, _ = np.histogram(q, bins=bins, density=True)
        
        # Add small epsilon to avoid log(0)
        p_hist = p_hist + 1e-10
        q_hist = q_hist + 1e-10
        
        # Normalize
        p_hist = p_hist / p_hist.sum()
        q_hist = q_hist / q_hist.sum()
        
        return float(stats.entropy(p_hist, q_hist))
    
    def _ks_test(self, p: np.ndarray, q: np.ndarray) -> float:
        """Calculate Kolmogorov-Smirnov statistic."""
        statistic, _ = stats.ks_2samp(p, q)
        return float(statistic)
    
    def _wasserstein(self, p: np.ndarray, q: np.ndarray) -> float:
        """Calculate Wasserstein distance (Earth Mover's Distance)."""
        return float(stats.wasserstein_distance(p, q))
    
    def _severity(self, score: float) -> str:
        """Determine severity based on score."""
        if score < 0.1:
            return "NONE"
        elif score < 0.3:
            return "LOW"
        elif score < 0.5:
            return "MEDIUM"
        elif score < 0.7:
            return "HIGH"
        else:
            return "CRITICAL"


class FeatureMonitor:
    """Monitor feature statistics and health."""
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.drift_detector = DriftDetector()
        self.feature_stats: Dict[str, Dict] = defaultdict(dict)
    
    def update_stats(self, feature_name: str, values: np.ndarray):
        """Update statistics for a feature."""
        stats_dict = {
            "count": len(values),
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "median": float(np.median(values)),
            "q25": float(np.percentile(values, 25)),
            "q75": float(np.percentile(values, 75)),
            "missing_count": int(np.sum(np.isnan(values) if values.dtype.kind == 'f' else 0)),
            "updated_at": datetime.utcnow().isoformat()
        }
        self.feature_stats[feature_name] = stats_dict
    
    def get_feature_stats(self, feature_name: str) -> Dict:
        """Get statistics for a feature."""
        return self.feature_stats.get(feature_name, {})
    
    def get_all_stats(self) -> Dict:
        """Get statistics for all features."""
        return dict(self.feature_stats)
    
    def check_health(self) -> Dict:
        """Check overall feature store health."""
        issues = []
        
        # Check for high missing rates
        for name, stats in self.feature_stats.items():
            if "missing_count" in stats and "count" in stats:
                missing_rate = stats["missing_count"] / stats["count"] if stats["count"] > 0 else 0
                if missing_rate > 0.1:  # > 10% missing
                    issues.append({
                        "severity": "HIGH",
                        "issue": f"High missing rate for {name}",
                        "details": f"{missing_rate * 100:.1f}% missing values"
                    })
        
        # Check for null values
        for name, stats in self.feature_stats.items():
            if stats.get("count", 0) == 0:
                issues.append({
                    "severity": "CRITICAL",
                    "issue": f"No data for {name}",
                    "details": "Feature has no data"
                })
        
        return {
            "healthy": len(issues) == 0,
            "issues_count": len(issues),
            "issues": issues,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global monitor instance
monitor = FeatureMonitor()


if __name__ == "__main__":
    # Example usage
    import pandas as pd
    
    # Create sample data
    df = pd.DataFrame({
        "age": np.random.normal(30, 5, 1000),
        "purchases": np.random.exponential(3, 1000),
    })
    
    # Update stats
    for col in df.columns:
        monitor.update_stats(col, df[col].values)
    
    # Get stats
    print("Feature Statistics:")
    for name, stats in monitor.get_all_stats().items():
        print(f"\n{name}:")
        for k, v in stats.items():
            print(f"  {k}: {v}")
    
    # Check drift
    drift_detector = DriftDetector()
    drift_detector.set_reference("age", np.random.normal(30, 5, 100))
    drift_result = drift_detector.detect("age", np.random.normal(35, 8, 100))
    print(f"\nDrift Detection:")
    print(f"  Score: {drift_result['score']}")
    print(f"  Detected: {drift_result['drift_detected']}")
    
    # Health check
    health = monitor.check_health()
    print(f"\nHealth Check:")
    print(f"  Healthy: {health['healthy']}")
    print(f"  Issues: {health['issues_count']}")
    
    # Export Prometheus metrics
    print(f"\nPrometheus Metrics:")
    print(monitor.metrics.export_prometheus())
