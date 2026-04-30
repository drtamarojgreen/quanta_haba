import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../src/p")))
from config_manager import ConfigManager
from util.fact_utils import read_facts

def config_manager_storage_card(facts):
    """
    @Card: python_config_manager_storage_verification
    @Is profile_storage_operational == true
    @Results python_config_manager_storage_operational == true
    """
    cm = ConfigManager()
    profile_name = "CDD_Python_Test"
    config_data = {"provider": "TestProvider", "client_id": "test_id"}

    cm.save_configuration(profile_name, config_data)
    loaded = cm.get_configuration(profile_name)

    saved_correctly = (loaded and loaded.get("provider") == "TestProvider")

    cm.delete_configuration(profile_name)
    deleted = cm.get_configuration(profile_name)

    deleted_correctly = (not deleted or "provider" not in deleted)

    operational = saved_correctly and deleted_correctly
    print(f"python_config_manager_storage_operational = {str(operational).lower()}")

if __name__ == "__main__":
    facts = read_facts("python_config_manager.facts")
    print("[CDD Card: python_config_manager_storage_verification]")
    config_manager_storage_card(facts)
