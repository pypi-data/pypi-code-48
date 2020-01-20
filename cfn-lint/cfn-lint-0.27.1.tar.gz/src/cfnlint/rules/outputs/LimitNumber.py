"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitNumber(CloudFormationLintRule):
    """Check if maximum Output limit is exceeded"""
    id = 'E6010'
    shortdesc = 'Output limit not exceeded'
    description = 'Check the number of Outputs in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['outputs', 'limits']

    def match(self, cfn):
        """Check CloudFormation Outputs"""

        matches = []

        # Check number of outputs against the defined limit
        outputs = cfn.template.get('Outputs', {})
        if len(outputs) > LIMITS['outputs']['number']:
            message = 'The number of outputs ({0}) exceeds the limit ({1})'
            matches.append(RuleMatch(['Outputs'], message.format(
                len(outputs), LIMITS['outputs']['number'])))

        return matches
