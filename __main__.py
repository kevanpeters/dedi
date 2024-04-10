"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws




# Create an IAM role with the AmazonSSMManagedInstanceCore policy attached
ssm_role = aws.iam.Role("ssmRole",
    assume_role_policy="""{
       "Version": "2012-10-17",
       "Statement": [{
           "Effect": "Allow",
           "Principal": {"Service": "ec2.amazonaws.com"},
           "Action": "sts:AssumeRole"
       }]
    }"""
)

# Attach the AmazonSSMManagedInstanceCore policy to the role
ssm_role_policy_attachment = aws.iam.RolePolicyAttachment("ssmRolePolicyAttachment",
    role=ssm_role.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
)

# Create an IAM instance profile that can be associated with an EC2 instance
ssm_instance_profile = aws.iam.InstanceProfile("ssmInstanceProfile",
    role=ssm_role.name
)

# The ARN of the instance profile to assign it to an instance can be accessed with `ssm_instance_profile.arn`
pulumi.export('ssm_instance_profile_arn', ssm_instance_profile.arn)


# Specify the desired size for your instance
instance_size = 'c5.large' #'t2.micro'

# Specify the existing key pair name you created in AWS for SSH access
# key_pair_name = 'pc2'

# Create Key pair based in the public key in the file in /priv

key_pair = aws.ec2.KeyPair('dedi-key-pair',
    public_key=open('./priv/pc2.pub').read()
)

windows_2022_ami = "ami-0aec1cbfa00609468" # us-west-2 windows 2022 core "ami-03ea14ccbeab7b2d5"

# Pull user data from ./wreckfest/userdata.ps1
with open('./game_data/wreckfest/userdata.ps1', 'r') as file:
    user_data = file.read()

# wrap userdata in <powershell> tags
user_data = f'<powershell>{user_data}</powershell>'

ingress_ports = [80, 3389, 443, 27037, 33542, 27037, 27015, 27016, 33540]

ingress_list = []
for port in ingress_ports:
    ingress_list.append({
        'from_port': port,
        'to_port': port,
        'protocol': 'tcp',
        'cidr_blocks': ['0.0.0.0/0']
    })


#loop through ad add udp
for port in ingress_ports:
    ingress_list.append({
        'from_port': port,
        'to_port': port,    
        'protocol': 'udp',
        'cidr_blocks': ['0.0.0.0/0']
    })
egress_list = [{
        'from_port': 0,
        'to_port': 0,
        'protocol': '-1',
        'cidr_blocks': ['0.0.0.0/0']
}]
# Create a security group to allow incoming HTTP and RDP traffic
security_group = aws.ec2.SecurityGroup('allow_web_rdp',
    description='Allow access to web and RDP',
    ingress= ingress_list,
    egress=egress_list)

# Create an EC2 instance with the specified AMI, instance size, and user data
ec2_instance = aws.ec2.Instance('windows-instance',
    instance_type=instance_size,
    security_groups=[security_group.name],
    key_name=key_pair.key_name,
    ami=windows_2022_ami,
    user_data=user_data,     # This will run the above script to install IIS and .NET 4.7
    iam_instance_profile=ssm_instance_profile.name
)

# Export the public DNS of the EC2 instance
pulumi.export('instance_public_dns', ec2_instance.public_dns)