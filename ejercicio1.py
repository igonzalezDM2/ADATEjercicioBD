import enum
import os.path
from enum import Enum
from tokenize import Number

import csv
import sqlite3
import mysql.connector

from deportista import Deportista


class BaseDeDatos:

    csvAtletas = "csv/athlete_events.csv"
    sqlOlimpiadas = "sql/olimpiadas.sql"
    sqliteOlimpiadas = "sql/olimpiadas.sqlite"
    dbOlimpiadas = "db/olimpiadas.db"
    meds = enum.Enum('Medalla', ('Gold', 'Silver', ('Bronze')))

    def __init__(self):
        self.con = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root"
        )

        menu = """
        Elija una opción:
            1. Crear BBDD MySQL
            2. Crear BBDD SQLite
            3. Listado de deportistas en diferentes deportes
            4. Listado de deportistas participantes
            5. Modificar medalla deportista
            6. Añadir deportista/participación
            7. Eliminar participación
            0. Salir
        """

        opcion = None
        while opcion != "0":
            opcion = input(menu)
            if opcion == "1":
                self.__ejercicio1()
            elif opcion == "2":
                self.__ejercicio2()
            elif opcion == "3":
                self.__ejercicio3()
            elif opcion == "4":
                self.__ejercicio4()
            elif opcion == "5":
                self.__ejercicio5()
            elif opcion == "6":
                self.__ejercicio6()
            elif opcion == "7":
                self.__ejercicio7()
        self.con.close()

    def __ejercicio1(self):
        self.__comprobarExistencia()
        self.con.database = "OLIMPIADAS"
        if os.path.exists(self.csvAtletas) and os.path.isfile(self.csvAtletas):
            try:
                self.__volcarCsv(None)
                print("Los datos fueron introducidos con éxito")
            except IOError as e:
                print(f"Error de carga:\n{e}")
        else:
            print("El fichero csv de atletas no fue encontrado")



    def __comprobarExistencia(self):
        cur = self.con.cursor()
        sqlExiste = """
        SELECT SCHEMA_NAME
        FROM INFORMATION_SCHEMA.SCHEMATA
        WHERE SCHEMA_NAME = 'OLIMPIADAS'
        """

        cur.execute(sqlExiste)
        bdExiste = cur.fetchone()
        if bdExiste:
            cur.execute("DROP DATABASE `OLIMPIADAS`")
            self.con.commit()
        cur.close()
        with open(self.sqlOlimpiadas) as sqlFile:
            try:
                cur = self.con.cursor()
                for _ in cur.execute(sqlFile.read(), multi=True):
                    pass
            except RuntimeError as re:
                if "StopIteration" in re.__str__():
                    self.con.commit()
            except Exception as e:
                print(f"Error: {e}")
            finally:
                cur.close()

    def __volcarCsv(self, conl):
        with open(self.csvAtletas) as csvFile:
            reader = csv.DictReader(csvFile)
            conexion = conl if conl else self.con
            cur = conexion.cursor(dictionary=True) if not conl else conexion.cursor()
            campo = "?" if conl else "%s"
            sentencias = []
            for ath in reader:
                idAth = BaseDeDatos.__noneIfNA(ath["ID"])
                nomAtleta = BaseDeDatos.__noneIfNA(ath["Name"])
                sexAtleta = BaseDeDatos.__noneIfNA(ath["Sex"])
                altAtleta = BaseDeDatos.__noneIfNA(ath["Height"])
                pesoAtleta = BaseDeDatos.__noneIfNA(ath["Weight"])

                deporte = BaseDeDatos.__noneIfNA(ath["Sport"])

                nocEquipo = BaseDeDatos.__noneIfNA(ath["NOC"])
                nombreEquipo = BaseDeDatos.__noneIfNA(ath["Team"])

                nombreEvento = BaseDeDatos.__noneIfNA(ath["Event"])

                juegos = BaseDeDatos.__noneIfNA(ath["Games"])
                anoJuegos = BaseDeDatos.__noneIfNA(ath["Year"])
                temporadaJuegos = BaseDeDatos.__noneIfNA(ath["Season"])
                ciudadJuegos = BaseDeDatos.__noneIfNA(ath["City"])

                edadParticipacion = BaseDeDatos.__noneIfNA(ath["Age"])
                medallaParticipacion = BaseDeDatos.__noneIfNA(ath["Medal"])

                idAtleta = None
                idDeporte = None
                idEquipo = None
                idOlimpiada = None
                idEvento = None

                # TABLA ATLETA
                cur.execute(f"SELECT * FROM atleta WHERE id = {campo}", (idAth,))
                result = cur.fetchone()

                if not result:
                    cur.execute(f"INSERT INTO atleta(id, nombre, sex, alt, peso) values ({campo}, {campo}, {campo}, {campo}, {campo})",
                                (idAth, nomAtleta, sexAtleta, altAtleta, pesoAtleta))
                    idAtleta = cur.lastrowid
                else:
                    idAtleta = result["id"]

                # TABLA DEPORTE
                cur.execute(f"SELECT * FROM deporte WHERE nombre = {campo}", (deporte,))
                result = cur.fetchone()

                if not result:
                    cur.execute(f"INSERT INTO deporte(nombre) values ({campo})",
                                (deporte,))
                    idDeporte = cur.lastrowid
                else:
                    idDeporte = result["id"]

                # TABLA EQUIPO
                cur.execute(f"SELECT * FROM equipo WHERE noc = {campo}", (nocEquipo,))
                result = cur.fetchone()
                if not result:
                    cur.execute(f"INSERT INTO equipo(noc, nombre) VALUES ({campo}, {campo})", (nocEquipo, nombreEquipo))
                    idEquipo = cur.lastrowid
                else:
                    idEquipo = result["id"]

                # TABLA OLIMPIADA
                cur.execute(f"SELECT * FROM olimpiada WHERE games = {campo}", (juegos,))
                result = cur.fetchone()
                if not result:
                    cur.execute(f"INSERT INTO olimpiada(games, year, season, city) VALUES ({campo}, {campo}, {campo}, {campo})", (juegos, anoJuegos, temporadaJuegos, ciudadJuegos))
                    idOlimpiada = cur.lastrowid
                else:
                    idOlimpiada = result["id"]

                # TABLA EVENTO
                cur.execute(f"SELECT * FROM evento WHERE deporte = {campo} AND nombre = {campo} AND olimpiada = {campo}", (idDeporte, nombreEvento, idOlimpiada))
                result = cur.fetchone()
                if not result:
                    cur.execute(f"INSERT INTO evento(nombre, deporte, olimpiada) VALUES ({campo}, {campo}, {campo})", (nombreEvento, idDeporte, idOlimpiada))
                    idEvento = cur.lastrowid
                else:
                    idEvento = result["id"]

                # RELACIÓN PARTICIPACIÓN
                cur.execute(f"SELECT * FROM participacion WHERE atleta = {campo} AND evento = {campo}", (idAtleta, idEvento))
                result = cur.fetchone()
                if not result:
                    cur.execute(f"INSERT INTO participacion(atleta, evento, equipo, edad, medalla) VALUES ({campo}, {campo}, {campo}, {campo}, {campo})", (idAtleta, idEvento, idEquipo, edadParticipacion, medallaParticipacion))


                print(f"ID ATLETA: {idAtleta}; ID DEPORTE: {idDeporte}; ID EQUIPO: {idEquipo}; ID EVENTO: {idEvento}; ID OLIMPIADA: {idOlimpiada}")

            conexion.commit()
            cur.close()

    def __ejercicio2(self):
        if os.path.exists(self.dbOlimpiadas):
            os.remove(self.dbOlimpiadas)

        if os.path.exists(self.sqliteOlimpiadas):
            conl = sqlite3.connect(self.dbOlimpiadas)
            conl.row_factory = sqlite3.Row
            cur = conl.cursor()
            with open(self.sqliteOlimpiadas) as sql:
                cur.executescript(sql.read())
                self.__volcarCsv(conl)
            conl.commit()
            cur.close()
            conl.close()



    def __ejercicio3(self):
        self.con.database = "OLIMPIADAS"
        opcion = input("""
        ¿Dónde desea realizar la búsqueda?
            1. MariaDB
            2. SQLite
        """)
        if opcion == "1":
            self.__buscarMariaDB()
        elif opcion == "2":
            self.__buscarSqlite()
        else:
            print("Opción inválida")


    def __buscar(self, conl):
        query = """
        SELECT
        atleta.id as id,
        atleta.nombre as nombre,
        atleta.sex as sex,
        atleta.alt as alt,
        atleta.peso as peso,
        deporte.nombre as deporte,
        participacion.edad as edad,
        evento.nombre as evento,
        equipo.nombre as equipo,
        olimpiada.games as olimpiada,
        participacion.medalla as medalla
        FROM deporte
        INNER JOIN evento on deporte.id = evento.deporte
        INNER JOIN participacion ON participacion.evento = evento.id
        INNER JOIN atleta ON atleta.id = participacion.atleta
        INNER JOIN equipo ON participacion.equipo = equipo.id
        INNER JOIN olimpiada on evento.olimpiada = olimpiada.id
        WHERE atleta.id IN
                (SELECT atleta.id
                FROM atleta
                INNER JOIN participacion
                ON atleta.id = participacion.atleta
                INNER JOIN evento ON participacion.evento = evento.id
                GROUP BY atleta.id
                HAVING count(evento.deporte) > 1
                )
        ORDER BY id
        """
        conexion = conl if conl else self.con
        if conl:
            conl.row_factory = sqlite3.Row
        cur = conexion.cursor(dictionary=True) if not conl else conexion.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        idatl = None
        for row in rows:
            idactual = row['id']
            if idatl != idactual:
                idatl = idactual
                datosAtleta = f""" 
                INFO ATLETA: nombre: {row['nombre']}, sexo: {row['sex']}, altura: {row['alt']}, peso: {row['peso']}
                """
                print(datosAtleta)
            datosPart = f"""                    PARTICIPACIÓN:
                        deporte: {row['deporte']}
                        edad: {row['edad']}
                        evento: {row['evento']}
                        equipo: {row['equipo']}
                        juegos: {row['olimpiada']}
                        medalla: {row['medalla']}
            """
            print(datosPart)

        cur.close()
    def __buscarMariaDB(self):
        self.__buscar(None)

    def __buscarSqlite(self):
        conl = sqlite3.connect(self.dbOlimpiadas)
        self.__buscar(conl)
        conl.close()


    def __ejercicio4(self):
        self.con.database = "OLIMPIADAS"
        bbdd  = input("""
        ¿Dónde desea realizar la búsqueda?
            1. MariaDB
            2. SQLite
        """)
        temporada = input("""
               Temporada:
                   S. Verano
                   W. Invierno
               """)
        temporada = temporada.lower() if temporada is not None else None
        if not (bbdd == "1" or bbdd == "2") or not temporada:
            print("No ha seleccionado datos válidos")
            return

        if bbdd == "1":
            self.__ejercicio4Maria(temporada)
        else:
            self.__ejercicio4Lite(temporada)

    def __ejercicio4Comun(self, conl, temporada):

        campo = "?" if conl else "%s"
        if conl:
            conl.row_factory = sqlite3.Row

        sqlListadoOlimpiadas = f"SELECT * FROM olimpiada WHERE LOWER(season) LIKE '{temporada}%' ORDER BY year"
        conexion = conl if conl else self.con
        cur = conexion.cursor(dictionary=True) if not conl else conexion.cursor()
        cur.execute(sqlListadoOlimpiadas)
        olimpiadasSeleccionadas = cur.fetchall()
        if not olimpiadasSeleccionadas or len(olimpiadasSeleccionadas) < 1:
            print("No hay resultados")
            cur.close()
            return

        # OLIMPIADA
        print("Seleccione una de las siguientes ediciones olímpicas:")
        for idx, olimpiada in enumerate(olimpiadasSeleccionadas, start=1):
            print(f"\t{idx}.\t{olimpiada['city']} {olimpiada['year']}")
        idxOl = BaseDeDatos.__str2int(input("Elija el número de olimpiada: "))
        if not idxOl or not olimpiadasSeleccionadas[idxOl - 1]:
            print("Olimpiada incorrecta")
            cur.close()
            return
        olimpiada = olimpiadasSeleccionadas[idxOl - 1]

        # DEPORTE
        sqlDeportesPorOlimpiada = f"SELECT deporte.* FROM evento INNER JOIN deporte ON evento.deporte = deporte.id WHERE evento.olimpiada = {campo} GROUP BY deporte"
        cur.execute(sqlDeportesPorOlimpiada, (olimpiada['id'],))
        deportes = cur.fetchall()
        if len(deportes) < 1:
            print("No hay resultados")
            cur.close()
            return
        print("Seleccione uno de los siguientes deportes:")
        for idx, deporte in enumerate(deportes, start=1):
            print(f"{idx}.\t{deporte['nombre']}")
        idxDep = BaseDeDatos.__str2int(input("Elija el número del deporte: "))
        if not idxDep or not deportes[idxDep - 1]:
            print("Deporte incorrecto")
            cur.close()
            return
        deporte = deportes[idxDep - 1]

        #EVENTO
        sqlEventosPorDeporte = f"SELECT evento.* FROM evento WHERE deporte = {campo} AND olimpiada = {campo}"
        cur.execute(sqlEventosPorDeporte, (deporte['id'], olimpiada['id']))
        eventos = cur.fetchall()
        if len(eventos) < 1:
            print("No hay resultados")
            cur.close()
            return
        print("Seleccione uno de los siguientes eventos:")
        for idx, evento in enumerate(eventos, start=1):
            print(f"{idx}.\t{evento['nombre']}")
        idxEv = BaseDeDatos.__str2int(input("Elija el número del deporte: "))
        if not idxEv or not eventos[idxEv - 1]:
            print("Evento incorrecto")
            cur.close()
            return
        evento = eventos[idxEv - 1]

        sqlParticipantes = f"""
        SELECT atleta.*, participacion.edad as edad
        FROM atleta
        INNER JOIN participacion ON atleta.id = participacion.atleta
        INNER JOIN evento ON participacion.evento = evento.id
        WHERE evento.id = {campo}
        ORDER BY atleta.nombre
        """
        cur.execute(sqlParticipantes, (evento['id'],))
        print(f"Temporada: {olimpiada['season']}, Edición: {olimpiada['games']}, Deporte: {deporte['nombre']}, Evento: {evento['nombre']}")
        for atleta in cur.fetchall():
            print(f"""
                Nombre: {atleta['nombre']}
                Sexo: {atleta['sex']}
                Altura: {atleta['alt']}
                Peso: {atleta['peso']}
                Edad: {atleta['edad']}
            """)
        cur.close()

    def __ejercicio4Maria(self, temporada):
        self.__ejercicio4Comun(None, temporada)
    def __ejercicio4Lite(self, temporada):
        conl = sqlite3.connect(self.dbOlimpiadas)
        self.__ejercicio4Comun(conl, temporada)
        conl.close()


    def __ejercicio5(self):
        self.con.database = "OLIMPIADAS"
        dic = self.__ejercicio5Mysql()
        print(dic)
        self.__ejercicio5Lite(dic["atleta"], dic["evento"], dic["medalla"])


    def __ejercicio5Comun(self, conl, athlete, event, med):
        conexion = conl if conl else self.con
        campo = "%s"
        if conl:
            conexion.row_factory = sqlite3.Row
            campo = "?"
        cur = conexion.cursor(dictionary=True) if not conl else conexion.cursor()

        if not athlete and not event:
            sqlDeportistas = f"SELECT * FROM atleta WHERE LOWER(nombre) LIKE LOWER({campo}) ORDER BY nombre"
            cur.execute(sqlDeportistas, (f"%{input('Introduzca el nombre del deportista: ')}%",))
            deportistas = cur.fetchall()
            for idx, deportista in enumerate(deportistas, start=1):
                print(f"\t{idx}.\t {deportista['nombre']}")
            idxDep = BaseDeDatos.__str2int(input("Seleccione el número del deportista: "))
            if not idxDep or not deportistas[idxDep - 1]:
                print("No ha seleccionado un deportista válido")
                cur.close()
                return
            deportista = deportistas[idxDep - 1]

            #EVENTO
            sqlEventos = f"""
            SELECT evento.*, participacion.medalla
            FROM evento
            INNER JOIN participacion ON participacion.evento = evento.id
            WHERE participacion.atleta = {campo}
            ORDER BY nombre"""
            cur.execute(sqlEventos, (deportista['id'],))
            eventos = cur.fetchall()
            for idx, evento in enumerate(eventos, start=1):
                print(f"\t{idx}.\t {evento['nombre']}")
            idxEv = BaseDeDatos.__str2int(input("Seleccione el número del evento: "))
            if not idxEv or not eventos[idxEv - 1]:
                print("No ha seleccionado un evento válido")
                cur.close()
                return
            evento = eventos[idxEv - 1]
            medalla = evento['medalla']

            print(f"El deportista {deportista['nombre']} {'no obtuvo medalla' if not medalla else f' obtuvo {medalla}'} en la prueba {evento['nombre']}")
            resp = input("¿Desea modificarlo? S/N")
            if resp and resp.lower() == "s":
                menuMedallas = """
                    Elija la medalla:
                        1. Oro
                        2. Plata
                        3. Bronce
                        4. Ninguna
                """
                selec = BaseDeDatos.__str2int(input(menuMedallas))

                med = None
                if selec > 0 and selec < 4:
                    med = self.meds(selec).name
                elif selec > 4:
                    print("No ha seleccionado una medalla válida")
                    cur.close()
                    return

        #SIENTO LA CHAPUZA PARA ADAPTAR LO DE MYSQL A SQLITE :(
        idEv = evento['id'] if not event else event;
        idAt = deportista['id'] if not athlete else athlete;


        sqlUpdateMedalla = f"UPDATE participacion SET medalla = {campo} WHERE evento = {campo} AND atleta = {campo}"
        try:
            cur.execute(sqlUpdateMedalla, (med, idEv, idAt))
            conexion.commit()
            print("La medalla se actualizó con éxito")
        except Exception as e:
            print(f"No se pudo actualizar la medalla: {e}")

        cur.close()
        if not athlete and not event:
            return {"atleta": deportista["id"], "evento": evento["id"], "medalla": med}

    def __ejercicio5Mysql(self):
        return self.__ejercicio5Comun(None, None, None, None)

    def __ejercicio5Lite(self, atleta, evento, medalla):
        conl = sqlite3.connect(self.dbOlimpiadas)
        self.__ejercicio5Comun(conl, atleta, evento, medalla)
        conl.close()




    def __ejercicio6(self):
        self.con.database = "OLIMPIADAS"
        cur = self.con.cursor(dictionary=True)
        try:
            deportista = self.__ejercicio6BuscarDeportista(False)
            temp = Enum('temporada', ['Summer', 'Winter'])
            tempSel = input(f"Seleccione una temporada {temp.Summer.name}/{temp.Winter.name}: ")
            temporada = None
            if tempSel and tempSel.lower() in temp.Summer.name.lower():
                temporada = temp.Summer.name.__str__()
            elif tempSel and tempSel.lower() in temp.Winter.name.lower():
                temporada = temp.Winter.name.__str__()
            else:
                print("No ha seleccionado una temporada correcta")
                return

            cur.execute("SELECT * FROM olimpiada WHERE season = %s GROUP BY year", (temporada,))
            ediciones = cur.fetchall()

            print("Ediciones: ")
            for idx, ed in enumerate(ediciones):
                print(f"\t{idx + 1} - {ed['city']} {ed['year']}")
            numEd = int(input("Elija el número de la edición:"))
            edicion = ediciones[numEd - 1]
            if not edicion or not edicion['id']:
                print("No ha elegido una edición válida")
                return

            cur.execute("SELECT deporte.* FROM deporte INNER JOIN evento ON deporte.id = evento.deporte WHERE evento.olimpiada = %s GROUP BY deporte.id ORDER BY deporte.nombre", (edicion['id'],))
            deportes = cur.fetchall()
            print("Deportes: ")
            for idx, dp in enumerate(deportes):
                print(f"\t{idx + 1} - {dp['nombre']}")
            numDep = int(input("Elija el número del deporte:"))
            deporte = deportes[numDep - 1]
            if not deporte or not deporte['id']:
                print("No ha elegido un deporte válido")
                return

            cur.execute("SELECT * FROM evento WHERE deporte = %s", (deporte['id'],))
            eventos = cur.fetchall()
            print("Eventos: ")
            for idx, dp in enumerate(eventos):
                print(f"\t{idx + 1} - {dp['nombre']}")
            numEv = int(input("Elija el número del evento:"))
            evento = eventos[numEv - 1]
            if not evento or not evento['id']:
                print("No ha elegido un evento válido")
                return

            self.__anadirEdicion(deportista, evento['id'])


        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            cur.close()

    def __anadirEdicion(self, atleta, idEvento):
        cur = self.con.cursor(dictionary=True)
        conl = sqlite3.connect(self.dbOlimpiadas)
        try:
            insert0 = "INSERT INTO participacion(atleta, evento, equipo, edad, medalla) VALUES "
            insertMy = f"{insert0}(%s, %s, %s, %s, %s)"
            insertLite = f"{insert0}(?, ?, ?, ?, ?)"

            cur.execute("SELECT * FROM equipo")
            paises = cur.fetchall()
            for idx, pais in enumerate(paises):
                print(f"\t{idx + 1} - {pais['nombre']}")
            numPais = int(input("Elige el número del país con el que participó: "))
            pais = paises[numPais - 1]
            if not pais or not pais["id"]:
                print("No ha elegido un país válido")
                return

            menuMedallas = """
                Elija la medalla:
                    1. Oro
                    2. Plata
                    3. Bronce
                    4. Ninguna
            """
            selec = BaseDeDatos.__str2int(input(menuMedallas))

            medalla = None
            if selec > 0 and selec < 4:
                medalla = self.meds(selec).name
            elif selec > 4:
                print("No ha seleccionado una medalla válida")
                return

            edad = BaseDeDatos.__str2int(input("Introduzca la edad del deportista en el momento de celebrarse el evento: "))

            cur.execute(insertMy, (atleta.id, idEvento, pais['id'], edad, medalla))
            self.con.commit()

            curl = conl.cursor()
            curl.execute(insertLite, (atleta.id, idEvento, pais['id'], edad, medalla))
            conl.commit()


            print("LOS DATOS SE INSERTARON CON ÉXITO")

        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            cur.close()
            conl.close()
    def __crearDeportista(self):
        try:
            insert0 = "INSERT INTO atleta(nombre, sex, alt, peso) VALUES "
            insertMy = f"{insert0}(%s, %s, %s, %s)"
            insertLite = f"{insert0}(?, ?, ?, ?)"
            dep = (Deportista()
               .setNombre(input("Nombre del nuevo deportista: "))
               .setSex(input("Sexo del nuevo deportista (M/F): "))
               .setAlt(input("Altura del nuevo deportista (cm): "))
               .setPeso(input("Peso del nuevo deportista (kg no decimal): "))
               )

            #MY
            cur = self.con.cursor(dictionary=True)
            cur.execute(insertMy, (dep.nombre, dep.sex, dep.alt, dep.peso))
            dep.setId(cur.lastrowid)
            self.con.commit()
            cur.close()
            # LITE
            conl = sqlite3.connect(self.dbOlimpiadas)
            cur = conl.cursor()
            cur.execute(insertLite, (dep.nombre, dep.sex, dep.alt, dep.peso))
            conl.commit()
            cur.close()
            conl.close()
            print("Se ha creado el deportista")
            return dep
        except Exception as e:
            print(f"ERROR: {e}")
        return None


    def __ejercicio6BuscarDeportista(self, crearSiNoExiste):
        cur = self.con.cursor(dictionary=True)
        try:
            cadena = input("Escriba el deportista: ")
            like = f"%{cadena}%"
            sqlBusqueda = f"SELECT * FROM atleta WHERE LOWER(nombre) LIKE '{like}' ORDER BY nombre"
            cur.execute(sqlBusqueda)
            atletas = cur.fetchall()
            if (len(atletas) == 0 or len(cadena) == 0):
                if crearSiNoExiste:
                    crear = input("No existe el deportista, ¿desea crear uno?: S/N")
                    if crear and crear.lower() == "s":
                        return self.__crearDeportista()
                else:
                    print("No existe el deportista")
                    return None
            else:
                print(f"Resultados para la búsqueda [{cadena}]:")
                for idx, atl in enumerate(atletas):
                    deportista = Deportista.fromDict(atl)
                    print(f"\t{idx + 1} - {deportista}")
                numDep = int(input("Elija el número del deportista"))
                return Deportista.fromDict(atletas[numDep - 1])
        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            cur.close()

    def __ejercicio6Comun(self, conl):
        conexion = conl if conl else self.con
        campo = "%s"
        if conl:
            conexion.row_factory = sqlite3.Row
            campo = "?"
        cur = conexion.cursor(dictionary=True) if not conl else conexion.cursor()

    def __ejercicio7(self):
        self.con.database = "OLIMPIADAS"
        dep = self.__ejercicio6BuscarDeportista(False)
        if dep:
            cur = self.con.cursor(dictionary=True)
            try:
                cur.execute(
                    "SELECT olimpiada.year, olimpiada.city, evento.nombre, evento.id FROM participacion INNER JOIN evento ON evento.id = participacion.evento INNER JOIN olimpiada ON evento.olimpiada = olimpiada.id WHERE atleta = %s",
                    (dep.id,))
                eventos = cur.fetchall()
                if len(eventos) > 0:
                    for idx, ev in enumerate(eventos):
                        print(f"{idx + 1} - {ev['nombre']} | {ev['city']} {ev['year']}")

                    numEv = int(input("Eljia el número del evento: "))
                    ev = eventos[numEv - 1]
                    deleteEvMy = "DELETE FROM participacion WHERE evento = %s AND atleta = %s"
                    deleteEvLite = "DELETE FROM participacion WHERE evento = ? AND atleta = ?"

                    if ev:
                        cur.execute(deleteEvMy, (ev['id'], dep.id))
                        conl = sqlite3.connect(self.dbOlimpiadas)
                        curl = conl.cursor()
                        curl.execute(deleteEvLite, (ev['id'], dep.id))
                        if len(eventos) == 1:
                            deleteAtleta = "DELETE FROM atleta WHERE id = "
                            deleteAtletaMy = f"{deleteAtleta}%s"
                            deleteAtletaLite = f"{deleteAtleta}?"
                            cur.execute(deleteAtletaMy, (dep.id,))
                            conl = sqlite3.connect(self.dbOlimpiadas)
                            curl = conl.cursor()
                            curl.execute(deleteAtletaLite, (dep.id,))

                        self.con.commit()
                        conl.commit()
                        print("Los datos fueron eliminados")
            except Exception as e:
                print(e)
                cur.close()



        else:
            print("No se hallaron participaciones")



    def __noneIfNA(value):
        if value == "NA":
            return None
        return value

    def __str2int(str):
        try:
            return int(str)
        except Exception:
            return None

BaseDeDatos()