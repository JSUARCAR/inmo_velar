class LiquidacionNoElegibleError(ValueError):
    def __init__(self, motivo: str):
        super().__init__(motivo)
        self.motivo = motivo

