class ServerBitrixErrors(Exception):
    def __init__(self, message="Произошла пользовательская ошибка"):
        self.message = message
        super().__init__(self.message)
