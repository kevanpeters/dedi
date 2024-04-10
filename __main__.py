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
instance_size = 't2.micro'

# Specify the existing key pair name you created in AWS for SSH access
key_pair_name = 'pc2'

# Define the AMI for Windows Server 2019
windows_2019_ami = aws.ec2.get_ami(
    most_recent=True,
    filters=[{"name": "name", "values": ["Windows_Server-2019-English-Full-Base-*"]}],
    owners=['amazon']
)

# Pull user data from ./wreckfest/userdata.ps1
with open('./wreckfest/userdata.ps1', 'r') as file:
    user_data = file.read()

# wrap userdata in <powershell> tags
user_data = f'<powershell>{user_data}</powershell>'

ingress_ports = [80, 3389, 443, 27037, 33542, 27037]
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

# Create a security group to allow incoming HTTP and RDP traffic
security_group = aws.ec2.SecurityGroup('allow_web_rdp',
    description='Allow access to web and RDP',
    ingress= ingress_list 
)

# Create an EC2 instance with the specified AMI, instance size, and user data
ec2_instance = aws.ec2.Instance('windows-instance',
    instance_type=instance_size,
    security_groups=[security_group.name],
    key_name=key_pair_name,
    ami=windows_2019_ami.id,
    user_data=user_data,     # This will run the above script to install IIS and .NET 4.7
    iam_instance_profile=ssm_instance_profile.name
)

# Export the public DNS of the EC2 instance
pulumi.export('instance_public_dns', ec2_instance.public_dns)