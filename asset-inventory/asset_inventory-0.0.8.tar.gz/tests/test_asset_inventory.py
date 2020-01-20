from asset_inventory import AssetManager

import json
from collections import defaultdict

from pathlib import Path

username = 'muhaalghamdi'
psssword = '123321'
ssh_key = '/Users/muhannad/.ssh/ansible'
hosts = ['172.21.51.125']

tests_path = Path(__file__).parent.absolute()
resutls_path = tests_path / 'results'
resutls_path.mkdir(exist_ok=True)


def main():
    asset_manager = AssetManager(remote_user=username, password=psssword, ssh_key=ssh_key, connection='paramiko')
    asset_manager.fetch(hosts=hosts)
    results = defaultdict(list)
    for result in asset_manager.results():
        results[result.status].append({'host': result.host, 'message': result.message})
        if result.status is 'success':
            inventory = resutls_path / f'{result.host}_inventory.json'
            facts_path = resutls_path / f'{result.host}_facts.json'
            open(file=inventory, mode='w+').write(json.dumps(result.inventory.serialize(), indent=2))
            open(file=facts_path, mode='w+').write(json.dumps(result.facts, indent=2))

    print(results)


if __name__ == "__main__":
    main()
