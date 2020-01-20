import attr

from .. import constants


@attr.s
class BaseExperiment(object):
    """
    Base experiment class. Single node and multi node experiments classes inherit from it.

    Experiments are intended to be used for intensive computational tasks like neural network training. Gradient
    supports single-node experiments as well as distributed training through multinode experiments.

    Experiments can be run from the Experiment Builder web interface, the GradientCI bot, or the CLI.

    :param str name: Name of new experiment
    :param str ports: Port to use in new experiment
    :param str workspace_url: Project git repository url
    :param str workspace_ref: Git commit hash, branch name or tag
    :param str workspace_username: Project git repository username
    :param str workspace_password: Project git repository password
    :param Dataset dataset
    :param str working_directory: Working directory for the experiment
    :param str artifact_directory: Artifacts directory
    :param str cluster_id: Cluster ID (handle)
    :param dict experiment_env: Environment variables in a JSON
    :param str project_id: Project ID
    :param str model_type: defines the type of model that is being generated by the experiment.
    :param str model_path: Model path
    :param bool is_preemptible: Is preemptible
    :param str id:
    :param int state: state of experiment can be one of::

            "created"
            "provisioned"
            "network setup"
            "running"
            "stopped"
            "error"
            "failed"
            "canceled"
            "network teardown"
            "pending"
            "provisioning"
            "network setting up"
            "network tearing down"
    """
    name = attr.ib(type=str, default=None)
    ports = attr.ib(type=str, default=None)
    workspace_url = attr.ib(type=str, default=None)
    workspace_ref = attr.ib(type=str, default=None)
    workspace_username = attr.ib(type=str, default=None)
    workspace_password = attr.ib(type=str, default=None)
    datasets = attr.ib(type=list, default=None)
    working_directory = attr.ib(type=str, default=None)
    artifact_directory = attr.ib(type=str, default=None)
    cluster_id = attr.ib(type=str, default=None)
    experiment_env = attr.ib(type=dict, default=dict)
    project_id = attr.ib(type=str, default=None)
    model_type = attr.ib(type=str, default=None)
    model_path = attr.ib(type=str, default=None)
    is_preemptible = attr.ib(type=bool, default=None)
    id = attr.ib(type=str, default=None)
    state = attr.ib(type=int, default=None)


@attr.s
class SingleNodeExperiment(BaseExperiment):
    """
    Single node experiment class. Inherits from ``BaseExperiment`` class

    In your your CLI command or ``config.yaml``, specify the experiment type as ``singlenode``

    :param str container: Container (dockerfile)
    :param str machine_type: Machine type
        Options::

        "Air"
        "Standard"
        "Pro"
        "Advanced"
        "GPU+"
        "P4000"
        "P5000"
        "P6000"
        "V100"
        "C1"
        "C2"
        "C3"
        "C4"
        "C5"
        "C6"
        "C7"
        "C8"
        "C9"
        "C10"
    :param str command: Container entrypoint command
    :param str container_user: Container user for running the specified command in the container. If no containerUser is specified, the user will default to 'root' in the container.
    :param str registry_username: Registry username for accessing private docker registry container if nessesary
    :param str registry_password: Registry password for accessing private docker registry container if nessesary
    :param int experiment_type_id: type of experiment
        Options::

            "single node"
            "GRPC multi node"
            "MPI multi node"
            "Hyperparameter tuning"
    """
    container = attr.ib(type=str, default=None)
    machine_type = attr.ib(type=str, default=None)
    command = attr.ib(type=str, default=None)
    container_user = attr.ib(type=str, default=None)
    registry_username = attr.ib(type=str, default=None)
    registry_password = attr.ib(type=str, default=None)
    registry_url = attr.ib(type=str, default=None)
    experiment_type_id = attr.ib(type=int, default=constants.ExperimentType.SINGLE_NODE)

    @experiment_type_id.validator
    def experiment_type_id_validator(self, attribute, value):
        if value is not constants.ExperimentType.SINGLE_NODE:
            raise ValueError("Single node experiment's type must equal {}".
                             format(constants.ExperimentType.SINGLE_NODE))


@attr.s
class MultiNodeExperiment(BaseExperiment):
    """
    Multi node experiment class. Inherits from ``BaseExperiment`` class

    Gradient supports both gRPC and MPI protocols for distributed TensorFlow model training. In your CLI command or
    ``config.yaml``, specify the experiment type as either ``multinode``.

    The two types are::

        type: "multi-grpc"

    or::

        type: "multi-mpi"

    :param int experiment_type_id: type of experiment
        Options::

            "single node"
            "GRPC multi node"
            "MPI multi node"
            "Hyperparameter tuning"
    :param str worker_container: Worker container (dockerfile)
    :param str worker_machine_type: Worker machine type
    :param str worker_command: Worker command
    :param int worker_count: Worker count
    :param str parameter_server_container: Parameter server container
    :param str parameter_server_command: Parameter server command
    :param int parameter_server_count: Parameter server count
    :param str worker_container_user: Worker container user
    :param str worker_registry_username: Registry username for accessing private docker registry container if nessesary
    :param str worker_registry_password: Registry password for accessing private docker registry container if nessesary
    :param str parameter_server_container_user: Parameter server container user
    :param str parameter_server_registry_username: Registry username for accessing private docker registry container if nessesary
    :param str parameter_server_registry_password: Registry password for accessing private docker registry container if nessesary
    """
    experiment_type_id = attr.ib(type=int, default=None)
    worker_container = attr.ib(type=str, default=None)
    worker_machine_type = attr.ib(type=str, default=None)
    worker_command = attr.ib(type=str, default=None)
    worker_count = attr.ib(type=int, default=None)
    parameter_server_container = attr.ib(type=str, default=None)
    parameter_server_machine_type = attr.ib(type=str, default=None)
    parameter_server_command = attr.ib(type=str, default=None)
    parameter_server_count = attr.ib(type=int, default=None)
    worker_container_user = attr.ib(type=str, default=None)
    worker_registry_username = attr.ib(type=str, default=None)
    worker_registry_password = attr.ib(type=str, default=None)
    worker_registry_url = attr.ib(type=str, default=None)
    parameter_server_container_user = attr.ib(type=str, default=None)
    parameter_server_registry_username = attr.ib(type=str, default=None)
    parameter_server_registry_password = attr.ib(type=str, default=None)
    parameter_server_registry_url = attr.ib(type=str, default=None)

    @experiment_type_id.validator
    def experiment_type_id_validator(self, attribute, value):
        if value not in (constants.ExperimentType.GRPC_MULTI_NODE,
                         constants.ExperimentType.MPI_MULTI_NODE):
            raise ValueError("Multi node experiment's type must equal {} or {}".
                             format(constants.ExperimentType.GRPC_MULTI_NODE,
                                    constants.ExperimentType.MPI_MULTI_NODE))


@attr.s
class MpiMultiNodeExperiment(BaseExperiment):
    experiment_type_id = attr.ib(type=int, default=None)
    worker_container = attr.ib(type=str, default=None)
    worker_machine_type = attr.ib(type=str, default=None)
    worker_command = attr.ib(type=str, default=None)
    worker_count = attr.ib(type=int, default=None)
    master_container = attr.ib(type=str, default=None)
    master_machine_type = attr.ib(type=str, default=None)
    master_command = attr.ib(type=str, default=None)
    master_count = attr.ib(type=str, default=None)
    worker_container_user = attr.ib(type=str, default=None)
    worker_registry_username = attr.ib(type=str, default=None)
    worker_registry_password = attr.ib(type=str, default=None)
    worker_registry_url = attr.ib(type=str, default=None)
    master_container_user = attr.ib(type=str, default=None)
    master_registry_username = attr.ib(type=str, default=None)
    master_registry_password = attr.ib(type=str, default=None)
    master_registry_url = attr.ib(type=str, default=None)
