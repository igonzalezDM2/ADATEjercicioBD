class Deportista:
    def __init__(self):
        self.id = None
        self.nombre = None
        self.sex = None
        self.alt = None
        self.peso = None

    def setId(self, id):
        self.id = id
        return self

    def setNombre(self, nombre):
        self.nombre = nombre
        return self

    def setSex(self, sex):
        if sex and sex.upper() in ['S', 'M']:
            self.sex = sex.upper()
        return self

    def setAlt(self, alt):
        self.alt = alt
        return self

    def setPeso(self, peso):
        self.peso = peso
        return self

    def __str__(self):
        return f"{self.nombre}"

    def fromDict(dictDep):
        return (Deportista()
                .setId(dictDep["id"])
                .setNombre(dictDep["nombre"])
                .setSex(dictDep["sex"])
                .setAlt(dictDep["alt"])
                .setPeso(dictDep["peso"])
                )