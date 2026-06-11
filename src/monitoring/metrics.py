"""Prometheus Metrics"""

from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
from functools import wraps

# Define metrics
prediction_counter = Counter(
    'predictions_total',
    'Total number of predictions',
    ['symbol', 'model']
)

prediction_latency = Histogram(
    'prediction_latency_seconds',
    'Prediction latency in seconds',
    ['symbol']
)

trade_counter = Counter(
    'trades_total',
    'Total trades executed',
    ['symbol', 'side']
)

model_accuracy = Gauge(
    'model_accuracy',
    'Model accuracy',
    ['symbol']
)

def track_prediction(symbol: str, model: str = "lgb"):
    """Decorator to track predictions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            
            prediction_counter.labels(symbol=symbol, model=model).inc()
            prediction_latency.labels(symbol=symbol).observe(duration)
            
            return result
        return wrapper
    return decorator

def start_metrics_server(port: int = 8001):
    """Start Prometheus metrics server"""
    start_http_server(port)
    print(f"✅ Metrics server started on port {port}")

