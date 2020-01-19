import ruamel.yaml
from janis_assistant.engines.cromwell.cromwellconfiguration import CromwellConfiguration
from janis_assistant.engines.cwltool.cwltoolconfiguation import CWLToolConfiguration
from janis_assistant.templates.base import (
    EnvironmentTemplate,
    SingularityEnvironmentTemplate,
)
from janis_assistant.engines.enginetypes import EngineType


class LocalTemplate(EnvironmentTemplate):
    def __init__(self):
        """
        """
        super().__init__()

    def cromwell(self):
        return CromwellConfiguration(
            system=CromwellConfiguration.System(file_hash_cache=True)
        )

    def cwltool(self):
        config = CWLToolConfiguration()

        return config

    def engine_config(self, engine: EngineType):

        if engine == EngineType.cromwell:
            return self.cromwell()

        elif engine == EngineType.cwltool:
            return self.cwltool()

        # Returning none will allow the engine to run with no config
        return None


class LocalSingularityTemplate(SingularityEnvironmentTemplate):
    def __init__(
        self,
        container_dir,
        singularityLoadInstructions=None,
        containerBuildInstructions=f"singularity pull $image docker://${{docker}}",
        mailProgram: str = None,
    ):
        """

        :param container_dir: Location where to save and execute containers from
        :param singularityLoadInstructions: Ensure singularity with this command executed in shell
        :param containerBuildInstructions: Instructions for building singularity, it's recommended to not touch this setting.
        :param mailProgram: Mail program to pipe email to, eg: 'sendmail -t'
        """
        super().__init__(
            mail_program=mailProgram,
            container_dir=container_dir,
            build_instructions=containerBuildInstructions,
            load_instructions=singularityLoadInstructions,
        )

    def cromwell(self):

        config = CromwellConfiguration(
            backend=CromwellConfiguration.Backend(
                providers={
                    "Local": CromwellConfiguration.Backend.Provider.singularity(
                        singularityloadinstructions=self.singularity_load_instructions,
                        buildinstructions=self.singularity_build_instructions,
                        singularitycontainerdir=self.singularity_container_dir,
                    )
                }
            ),
            system=CromwellConfiguration.System(file_hash_cache=True),
        )

        return config

    def cwltool(self):
        config = CWLToolConfiguration()
        config.singularity = True
        # config.tmpdir_prefix = self.executionDir + "/"

        return config

    def engine_config(self, engine: EngineType):

        if engine == EngineType.cromwell:
            return self.cromwell()

        elif engine == EngineType.cwltool:
            return self.cwltool()

        # Returning none will allow the engine to run with no config
        raise NotImplementedError(
            f"The {self.__class__.__name__} template does not have a configuration for {engine.value}"
        )

    def prejanis_hook(self):
        return "exit 4;"
