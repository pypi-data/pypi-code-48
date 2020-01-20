from typing import List
from aws_cdk.aws_ec2 import Vpc, SecurityGroup, Subnet


class VPCParameters:
    def __init__(
            self,
            rotation_lambda_vpc: Vpc,
            rotation_lambda_security_groups: List[SecurityGroup],
            rotation_lambda_subnets: List[Subnet]
    ) -> None:
        """
        Constructor.

        :param rotation_lambda_vpc: A VPC in which a secrets rotation lambda will be deployed to.
        :param rotation_lambda_security_groups: Security groups to attach to a rotation lambda.
        :param rotation_lambda_subnets: Subnets in which a rotation lambda can operate.
        """
        self.rotation_lambda_vpc = rotation_lambda_vpc
        self.rotation_lambda_security_groups = rotation_lambda_security_groups
        self.rotation_lambda_subnets = rotation_lambda_subnets
