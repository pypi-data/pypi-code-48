from azure.keyvault.secrets import SecretClient
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.compute import ComputeManagementClient

def get_secret_from_key_vault(key_vault_name: str, secret_name: str):
    key_vault_uri = "https://" + key_vault_name + ".vault.azure.net"
    credential = get_client_from_cli_profile(ComputeManagementClient).config.credentials
    client = SecretClient(key_vault_uri, credential)

    return client.get_secret(secret_name).value

def set_secret_in_key_vault(key_vault_name: str, secret_name: str, secret_value):
    key_vault_uri = "https://" + key_vault_name + ".vault.azure.net"
    credential = get_client_from_cli_profile(ComputeManagementClient).config.credentials
    client = SecretClient(key_vault_uri, credential)
    client.set_secret(secret_name, secret_value)
