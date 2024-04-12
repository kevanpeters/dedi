
import pulumi
from pulumi import ComponentResource, ResourceOptions, Output
from pulumi.output import Inputs
import pulumi_aws as aws


class serverArgs:
    def __init__(self, instance_size, user_data, ingress_ports, ami):
        self.instance_size = instance_size
        self.user_data = user_data
        self.ingress_ports = ingress_ports
        self.ami = ami

class baseServer(pulumi.ComponentResource):

    def __init__(self, name: str, args: serverArgs, opts: ResourceOptions = None):
        super().__init__('baseServer', name, {}, opts)
        self.sg_ingress = []
                #loop through ad add udp
        for port in args.ingress_ports:
            self.sg_ingress.append({
                'from_port': port,
                'to_port': port,    
                'protocol': 'udp',
                'cidr_blocks': ['0.0.0.0/0']
            })
            self.sg_ingress.append({
                'from_port': port,
                'to_port': port,
                'protocol': 'tcp',
                'cidr_blocks': ['0.0.0.0/0']
            })

        self.sg_egress = [{
                'from_port': 0,
                'to_port': 0,
                'protocol': '-1',
                'cidr_blocks': ['0.0.0.0/0']
        }]


        self.key_pair = aws.ec2.KeyPair('dedi-key-pair',
            public_key=open('./priv/pc2.pub').read(),
            opts=ResourceOptions(parent=self)
        )

        # Create an IAM role with the AmazonSSMManagedInstanceCore policy attached
        self.ssm_role = aws.iam.Role("ssmRole",
            assume_role_policy="""{
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
            }""",
            opts=ResourceOptions(parent=self)
        )

        # Attach the AmazonSSMManagedInstanceCore policy to the role
        self.ssm_role_policy_attachment = aws.iam.RolePolicyAttachment("ssmRolePolicyAttachment",
            role=self.ssm_role.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
            opts=ResourceOptions(parent=self)
        )

        # Create an IAM instance profile that can be associated with an EC2 instance
        self.ssm_instance_profile = aws.iam.InstanceProfile("ssmInstanceProfile",
            role=self.ssm_role.name,
            opts=ResourceOptions(parent=self)
        )

        # The ARN of the instance profile to assign it to an instance can be accessed with `ssm_instance_profile.arn`

        # Pull user data from ./wreckfest/userdata.ps1

        # Create a security group to allow incoming HTTP and RDP traffic
        self.security_group = aws.ec2.SecurityGroup('allow_web_rdp',
            description='Allow access to web and RDP',
            ingress=self.sg_ingress,
            egress=self.sg_egress,
            opts=ResourceOptions(parent=self)
        )

        # Create an EC2 instance with the specified AMI, instance size, and user data
        self.ec2_instance = aws.ec2.Instance('windows-instance',
            instance_type=args.instance_size,
            security_groups=[self.security_group.name],
            key_name=self.key_pair.key_name,
            ami=args.ami,
            user_data=args.user_data, 
            iam_instance_profile=self.ssm_instance_profile.name,
            opts=ResourceOptions(parent=self)
        )
        pulumi.export('instance_public_dns', self.ec2_instance.public_dns)
        self.register_outputs({})
