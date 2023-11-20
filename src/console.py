from rich.console import Console as BaseConsole

class Console(BaseConsole):
    def error(self, text: str):
        ERROR = "[bold red]ERROR[/bold red] | "
        self.log(f"{ERROR}{text}")
    
    def success(self, text: str):
        OK = "[bold green]OK[/bold green] | "
        self.log(f"{OK}{text}")
    
    def info(self, text: str):
        INFO = "[bold cyan]INFO[/bold cyan] | "
        self.log(f"{INFO}{text}")
