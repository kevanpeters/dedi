from  gameServer.baseServer import baseServer, serverArgs

class wreckfestServer():
    def __init__(self, name: str) -> None:
        self.name = name

        with open('./game_data/wreckfest/userdata.ps1', 'r') as file:
            user_data = file.read()
        user_data = f'<powershell>{user_data}</powershell>'

        # WreckfestServer
        wreckfestserverArgs = serverArgs(
            user_data=user_data,
            ingress_ports=[80, 3389, 443, 27037, 33542, 27037, 27015, 27016, 33540],
            ami="ami-0aec1cbfa00609468",
            instance_size='c5.large'
        )
        self.wreckfestserver = baseServer(self.name, wreckfestserverArgs)



if __name__ == "__main__":
    wreckfestServer("wreckfestServer")