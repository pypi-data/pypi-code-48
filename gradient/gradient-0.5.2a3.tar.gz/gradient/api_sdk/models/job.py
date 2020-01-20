import attr


@attr.s
class Job(object):
    id = attr.ib(type=str, default=None)
    name = attr.ib(type=str, default=None)
    state = attr.ib(type=str, default=None)
    workspace_url = attr.ib(type=str, default=None)
    working_directory = attr.ib(type=str, default=None)
    artifacts_directory = attr.ib(type=str, default=None)
    entrypoint = attr.ib(type=str, default=None)
    project_id = attr.ib(type=str, default=None)
    project = attr.ib(type=str, default=None)
    container = attr.ib(type=str, default=None)
    container_url = attr.ib(type=str, default=None)
    base_container = attr.ib(type=str, default=None)
    base_container_url = attr.ib(type=str, default=None)
    machine_type = attr.ib(type=str, default=None)
    cluster = attr.ib(type=str, default=None)
    cluster_id = attr.ib(type=str, default=None)
    usage_rate = attr.ib(type=str, default=None)
    started_by_user_id = attr.ib(type=str, default=None)
    parent_job_id = attr.ib(type=str, default=None)
    job_error = attr.ib(type=str, default=None)
    dt_created = attr.ib(type=str, default=None)
    dt_modified = attr.ib(type=str, default=None)
    dt_provisioning_started = attr.ib(type=str, default=None)
    dt_provisioning_finished = attr.ib(type=str, default=None)
    dt_started = attr.ib(type=str, default=None)
    dt_finished = attr.ib(type=str, default=None)
    dt_teardown_started = attr.ib(type=str, default=None)
    dt_teardown_finished = attr.ib(type=str, default=None)
    dt_deleted = attr.ib(type=str, default=None)
    exit_code = attr.ib(type=str, default=None)
    queue_position = attr.ib(type=str, default=None)
    seq_num = attr.ib(type=int, default=None)
    storage_region = attr.ib(type=str, default=None)
    cluster_machine = attr.ib(type=str, default=None)
    fqdn = attr.ib(type=str, default=None)
    ports = attr.ib(type=str, default=None)
    is_public = attr.ib(type=bool, default=None)
    container_user = attr.ib(type=str, default=None)
    has_code = attr.ib(type=bool, default=None)
    code_uploaded = attr.ib(type=bool, default=None)
    code_commit = attr.ib(type=str, default=None)
    run_till_cancelled = attr.ib(type=bool, default=None)
    push_on_completion = attr.ib(type=bool, default=None)
    new_image_name = attr.ib(type=str, default=None)
    cpu_hostname = attr.ib(type=str, default=None)
    cpu_count = attr.ib(type=int, default=None)
    cpu_model = attr.ib(type=str, default=None)
    cpu_flags = attr.ib(type=str, default=None)
    cpu_mem = attr.ib(type=str, default=None)
    gpu_name = attr.ib(type=str, default=None)
    gpu_serial = attr.ib(type=str, default=None)
    gpu_device = attr.ib(type=str, default=None)
    gpu_driver = attr.ib(type=str, default=None)
    gpu_count = attr.ib(type=int, default=None)
    gpu_mem = attr.ib(type=str, default=None)
    tpu_type = attr.ib(type=str, default=None)
    tpu_name = attr.ib(type=str, default=None)
    tpu_grpc_url = attr.ib(type=str, default=None)
    tpu_tf_version = attr.ib(type=str, default=None)
    tpu_dataset_dir = attr.ib(type=str, default=None)
    tpu_model_dir = attr.ib(type=str, default=None)
    target_node_attrs = attr.ib(type=dict, default=None)
    job_env = attr.ib(type=dict, default=None)
    shared_mem_mbytes = attr.ib(type=int, default=None)
    shutdown_timeout = attr.ib(type=int, default=None)
    is_preemptible = attr.ib(type=bool, default=None)
    metrics_url = attr.ib(type=str, default=None)
    custom_metrics = attr.ib(type=str, default=None)
    experiment_id = attr.ib(type=str, default=None)

    command = attr.ib(type=str, default=None)
    workspace = attr.ib(type=str, default=None)
    workspace_archive = attr.ib(type=str, default=None)
    workspace_file_name = attr.ib(type=str, default=None)
    use_dockerfile = attr.ib(type=str, default=None)
    rel_dockerfile_path = attr.ib(type=str, default=None)
    registry_username = attr.ib(type=str, default=None)
    registry_password = attr.ib(type=str, default=None)
    build_only = attr.ib(type=bool, default=None)
