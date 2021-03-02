#!/usr/bin/env python3

from aws_cdk import core

from cdk.unicorn_api_stack import UnicornApiStack

app = core.App()
UnicornApiStack(app, "unicorn-api")

app.synth()
