from aws_cdk import (
    aws_ecr_assets,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_ecs_patterns as ecs_patterns,
    core,
)


class UnicornApiStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        container_image = aws_ecr_assets.DockerImageAsset(self, 'dockerImage',
                                                          directory='./unicorn_api_service'
                                                          )

        # noinspection PyTypeChecker
        unicorn_service = ecs_patterns.ApplicationLoadBalancedFargateService(self, 'unicornService',
                                                                             memory_limit_mib=1024,
                                                                             cpu=512,
                                                                             task_image_options={
                                                                                 'image': ecs.ContainerImage.from_docker_image_asset(
                                                                                     asset=container_image),
                                                                                 'container_port': 80,
                                                                                 'enable_logging': True,
                                                                                 'environment': {
                                                                                     'FLASK_DEBUG': '1',
                                                                                     'FLASK_ENV': 'development',
                                                                                     'FLASK_APP': '/app/app.py',
                                                                                     'PYTHONUNBUFFERED': '1'

                                                                                 }
                                                                             }
                                                                             )

        unicorn_service.task_definition.execution_role.add_managed_policy(
            iam.ManagedPolicy.from_managed_policy_arn(self, 'ecsExecutionRole',
                                                      managed_policy_arn='arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy')
        )

        unicorn_service.target_group.configure_health_check(
            path="/health"
        )

        unicorn_service.task_definition.task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore')
        )
        user_policy = iam.ManagedPolicy(self, 'userPolicy',
                                        document=iam.PolicyDocument(
                                            statements=[
                                                iam.PolicyStatement(
                                                    effect=iam.Effect.ALLOW,
                                                    actions=['ecs:UpdateService'],
                                                    resources=[
                                                        'arn:aws:ecs:*:*:service/*/cloud-debug-*',
                                                        unicorn_service.service.service_arn
                                                    ]
                                                ),
                                                iam.PolicyStatement(
                                                    effect=iam.Effect.ALLOW,
                                                    actions=[
                                                        'iam:GetRole',
                                                        'iam:ListRoles',
                                                        'iam:SimulatePrincipalPolicy'
                                                    ],
                                                    resources=['*']
                                                ),
                                                iam.PolicyStatement(
                                                    effect=iam.Effect.ALLOW,
                                                    actions=[
                                                        'iam:PassRole'
                                                    ],
                                                    resources=[
                                                        unicorn_service.task_definition.execution_role.role_arn,
                                                        unicorn_service.task_definition.task_role.role_arn
                                                    ],
                                                    conditions={
                                                        'StringEquals': {
                                                            "iam:PassedToService": "ecs-tasks.amazonaws.com"
                                                        }
                                                    }

                                                ),
                                                iam.PolicyStatement(
                                                    effect=iam.Effect.ALLOW,
                                                    actions=[
                                                        'iam:PassRole'
                                                    ],
                                                    resources=[
                                                        'arn:aws:iam::*:role/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS']
                                                ),
                                                iam.PolicyStatement(
                                                    effect=iam.Effect.ALLOW,
                                                    actions=[
                                                        's3:CreateBucket',
                                                        's3:GetObject',
                                                        's3:PutObject',
                                                        's3:DeleteObject',
                                                        's3:ListBucket'
                                                    ],
                                                    resources=['arn:aws:s3:::do-not-delete-cloud-debug-*']
                                                ),
                                                iam.PolicyStatement(
                                                    effect=iam.Effect.ALLOW,
                                                    actions=[
                                                        'ecs:ListClusters',
                                                        'ecs:ListServices',
                                                        'ecs:DescribeServices',
                                                        'ecs:ListTasks',
                                                        'ecs:DescribeTasks',
                                                        'ecs:DescribeTaskDefinition',
                                                        'elasticloadbalancing:DescribeListeners',
                                                        'elasticloadbalancing:DescribeRules',
                                                        'elasticloadbalancing:DescribeTargetGroups',
                                                        'ecr:GetAuthorizationToken',
                                                        'ecr:BatchCheckLayerAvailability',
                                                        'ecr:GetDownloadUrlForLayer',
                                                        'ecr:BatchGetImage'
                                                    ],
                                                    resources=['*']
                                                ),
                                                iam.PolicyStatement(
                                                    effect=iam.Effect.ALLOW,
                                                    actions=[
                                                        'logs:CreateLogGroup',
                                                        'logs:CreateLogStream'
                                                    ],
                                                    resources=['arn:aws:logs:*:*:cloud-debug*']
                                                ),
                                                iam.PolicyStatement(
                                                    effect=iam.Effect.ALLOW,
                                                    actions=[
                                                        'ecs:CreateService',
                                                        'ecs:DeleteService'
                                                    ],
                                                    resources=['arn:aws:ecs:*:*:service/*/cloud-debug*']
                                                ),
                                                iam.PolicyStatement(
                                                    effect=iam.Effect.ALLOW,
                                                    actions=[
                                                        'ecs:RegisterTaskDefinition'
                                                    ],
                                                    resources=['*']
                                                ),
                                                iam.PolicyStatement(
                                                    effect=iam.Effect.ALLOW,
                                                    actions=[
                                                        'elasticloadbalancing:ModifyListener',
                                                        'elasticloadbalancing:ModifyRule',
                                                        'elasticloadbalancing:ModifyTargetGroupAttributes'
                                                    ],
                                                    resources=['*']
                                                ),
                                                iam.PolicyStatement(
                                                    effect=iam.Effect.ALLOW,
                                                    actions=[
                                                        'elasticloadbalancing:CreateTargetGroup',
                                                        'elasticloadbalancing:DeleteTargetGroup'
                                                    ],
                                                    resources=[
                                                        'arn:aws:elasticloadbalancing:*:*:targetgroup/cloud-debug*']
                                                ),
                                                iam.PolicyStatement(
                                                    effect=iam.Effect.ALLOW,
                                                    actions=[
                                                        'ssm:StartSession',
                                                        'ssm:TerminateSession',
                                                        'ssm:ResumeSession',
                                                        'ssm:DescribeSessions',
                                                        'ssm:GetConnectionStatus'
                                                    ],
                                                    resources=['*']
                                                ),
                                                iam.PolicyStatement(
                                                    effect=iam.Effect.ALLOW,
                                                    actions=[
                                                        'application-autoscaling:RegisterScalableTarget',
                                                        'application-autoscaling:DeregisterScalableTarget',
                                                        'application-autoscaling:DescribeScalableTargets'
                                                    ],
                                                    resources=['*']
                                                ),

                                            ]))
