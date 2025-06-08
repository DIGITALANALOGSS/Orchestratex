import opentracing
import jaeger_client
from opentracing_instrumentation.client_hooks import install_all_patches
from opentracing_instrumentation.http_server import before_request, after_request
from opentracing_instrumentation.request_context import get_current_span
from opentracing_instrumentation.utils import get_current_span
import logging

logger = logging.getLogger(__name__)

class DistributedTracer:
    def __init__(self, service_name: str = 'orchestratex-service'):
        self.service_name = service_name
        self.tracer = self._initialize_tracer()
        install_all_patches()

    def _initialize_tracer(self) -> opentracing.Tracer:
        """Initialize Jaeger tracer."""
        config = jaeger_client.Config(
            config={
                'sampler': {
                    'type': 'const',
                    'param': 1,
                },
                'local_agent': {
                    'reporting_host': 'jaeger-agent',
                    'reporting_port': '6831',
                },
                'logging': True,
                'reporter_batch_size': 1,
            },
            service_name=self.service_name,
            validate=True,
        )
        return config.initialize_tracer()

    def start_span(self, operation_name: str, tags: dict = None) -> opentracing.Span:
        """Start a new span."""
        parent_span = get_current_span()
        return self.tracer.start_span(
            operation_name=operation_name,
            child_of=parent_span,
            tags=tags or {}
        )

    def trace_quantum_operation(self, operation_name: str, tags: dict = None):
        """Decorator for tracing quantum operations."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                with self.start_span(f'quantum.{operation_name}', tags):
                    return func(*args, **kwargs)
            return wrapper
        return decorator

    def trace_http_request(self, request, response):
        """Trace HTTP requests."""
        span = get_current_span()
        if span:
            span.set_tag('http.method', request.method)
            span.set_tag('http.url', request.url)
            span.set_tag('http.status_code', response.status_code)
            span.set_tag('http.duration', response.elapsed.total_seconds())

    def trace_database_operation(self, operation_name: str, query: str):
        """Trace database operations."""
        with self.start_span(f'database.{operation_name}'):
            span = get_current_span()
            if span:
                span.set_tag('sql.query', query)
                span.set_tag('sql.operation', operation_name)

    def trace_external_service(self, service_name: str, operation: str, tags: dict = None):
        """Trace external service calls."""
        with self.start_span(f'external.{service_name}.{operation}', tags):
            span = get_current_span()
            if span:
                span.set_tag('service.name', service_name)
                span.set_tag('operation.name', operation)

    def log_event(self, event_name: str, payload: dict = None):
        """Log an event in the current span."""
        span = get_current_span()
        if span:
            span.log_event(event_name, payload or {})

    def set_error(self, error: Exception):
        """Set error in the current span."""
        span = get_current_span()
        if span:
            span.set_tag('error', True)
            span.log_event('error', {
                'message': str(error),
                'type': type(error).__name__
            })

# Usage example
def setup_tracing():
    tracer = DistributedTracer()
    
    @tracer.trace_quantum_operation('circuit_execution')
    def execute_quantum_circuit(circuit):
        try:
            tracer.log_event('circuit_start')
            result = circuit.execute()
            tracer.log_event('circuit_complete', {'result': str(result)})
            return result
        except Exception as e:
            tracer.set_error(e)
            raise

    return tracer
