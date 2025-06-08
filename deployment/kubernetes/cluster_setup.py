import logging
from kubernetes import client, config
from kubernetes.client import V1ServiceAccount, V1Role, V1RoleBinding
from kubernetes.client import V1Deployment, V1PodSpec, V1Container
from kubernetes.client import V1Service, V1Ingress

logger = logging.getLogger(__name__)

class KubernetesClusterSetup:
    def __init__(self, config):
        """Initialize Kubernetes cluster setup.
        
        Args:
            config: Cluster configuration dictionary
        """
        self.config = config
        self.k8s_client = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize Kubernetes client."""
        try:
            # Try in-cluster config first
            try:
                config.load_incluster_config()
            except:
                # Fallback to local config
                config.load_kube_config()
                
            self.k8s_client = client.CoreV1Api()
            logger.info("Kubernetes client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {str(e)}")
            raise
            
    def create_namespace(self, namespace: str):
        """Create Kubernetes namespace.
        
        Args:
            namespace: Namespace name
        """
        try:
            v1 = client.CoreV1Api()
            namespace_obj = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=namespace)
            )
            v1.create_namespace(namespace_obj)
            logger.info(f"Namespace {namespace} created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create namespace: {str(e)}")
            raise
            
    def create_service_account(self, namespace: str, name: str):
        """Create service account.
        
        Args:
            namespace: Namespace name
            name: Service account name
        """
        try:
            v1 = client.CoreV1Api()
            sa = V1ServiceAccount(
                metadata=client.V1ObjectMeta(name=name)
            )
            v1.create_namespaced_service_account(namespace, sa)
            logger.info(f"Service account {name} created in {namespace}")
            
        except Exception as e:
            logger.error(f"Failed to create service account: {str(e)}")
            raise
            
    def create_role_binding(self, namespace: str, sa_name: str, role_name: str):
        """Create role binding.
        
        Args:
            namespace: Namespace name
            sa_name: Service account name
            role_name: Role name
        """
        try:
            rbac = client.RbacAuthorizationV1Api()
            rb = V1RoleBinding(
                metadata=client.V1ObjectMeta(name=f"{sa_name}-binding"),
                subjects=[
                    client.V1Subject(
                        kind="ServiceAccount",
                        name=sa_name,
                        namespace=namespace
                    )
                ],
                role_ref=client.V1RoleRef(
                    kind="Role",
                    name=role_name,
                    api_group="rbac.authorization.k8s.io"
                )
            )
            rbac.create_namespaced_role_binding(namespace, rb)
            logger.info(f"Role binding created for {sa_name}")
            
        except Exception as e:
            logger.error(f"Failed to create role binding: {str(e)}")
            raise
            
    def create_deployment(self, deployment: V1Deployment):
        """Create deployment.
        
        Args:
            deployment: Deployment object
        """
        try:
            apps = client.AppsV1Api()
            apps.create_namespaced_deployment(
                body=deployment,
                namespace=deployment.metadata.namespace
            )
            logger.info(f"Deployment {deployment.metadata.name} created")
            
        except Exception as e:
            logger.error(f"Failed to create deployment: {str(e)}")
            raise
            
    def create_service(self, service: V1Service):
        """Create service.
        
        Args:
            service: Service object
        """
        try:
            v1 = client.CoreV1Api()
            v1.create_namespaced_service(
                body=service,
                namespace=service.metadata.namespace
            )
            logger.info(f"Service {service.metadata.name} created")
            
        except Exception as e:
            logger.error(f"Failed to create service: {str(e)}")
            raise
            
    def create_ingress(self, ingress: V1Ingress):
        """Create ingress.
        
        Args:
            ingress: Ingress object
        """
        try:
            networking = client.NetworkingV1Api()
            networking.create_namespaced_ingress(
                body=ingress,
                namespace=ingress.metadata.namespace
            )
            logger.info(f"Ingress {ingress.metadata.name} created")
            
        except Exception as e:
            logger.error(f"Failed to create ingress: {str(e)}")
            raise
