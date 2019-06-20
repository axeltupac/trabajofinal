#!/usr/bin/env python
# -*- coding: utf-8 -*-
import PySimpleGUI as sg
import leiauts
import random, string, json, sys
from pattern.web import Wiktionary
from pattern.es import conjugate, attributive, parse, split, INFINITIVE, NEUTRAL

BOX_SIZE = 25


def definirColor(cantUbicaciones):
    """Recibe como parametro la cantidad total de las ubicaciones y calcula el promedio de temperaturas de una ubicacion al azar.
    Retorna el color de la interfaz dependiendo de la temperatura promedio."""
    try:
        ubicacion = random.choice(range(0, cantUbicaciones))
        archivoTemperaturas = open('temperatura_' + str(ubicacion) + '.json', 'r')
        lista_temperaturas = json.load(archivoTemperaturas)

        cantTotal = 0
        cantTemperatura = 0
        for dic in lista_temperaturas:
            cantTemperatura = cantTemperatura + dic['temperatura']
            cantTotal = cantTotal + 1

        if ((cantTemperatura / cantTotal) < 15):
            return 'blue'
        else:
            return 'red'
    except:
        return 'blue'
def ayudaa(listap, defis):
    """esta funcion se encarga de devolver todas las definiciones de las palabras para luego ser utilizadas en la ayuda"""
    def buscardef(palabra, defi):
        """esta funcion se encarga de buscar las deficiones/etimologias de las palabras"""
        try:
            articulo = Wiktionary(language="es").search(palabra)
            for elemento in articulo.sections:
                if "Etimología" in elemento.title:
                    if "Si puedes," in elemento.content:
                        defi[
                            palabra.title()] = palabra.title()  # Se puede poner que no tenga ayuda. No se encuentra en wiktionary
                    else:
                        defi[palabra.title()] = elemento.content.split("[editar]")[1].split("\n\n")[1]
                        if "[" in elemento.content.split("[editar]")[1].split("\n\n")[1]:
                            defi[palabra.title()] = defi[palabra.title()].split("[")[0]
                    break
                else:
                    defi[palabra.title()] = palabra.title()
        except:
            defi[palabra.title()] = palabra.title()
        return defi
    for palabra in listap:
        buscardef(palabra, defis)
    return defis


def guardarArchivo(dic):
    """esta funcion es para guardar en un archivos las palabras que fueron elegidas"""
    archivoPalabras = open('archivoDeConfiguracion.json', 'w', encoding="utf8")
    json.dump(dic, archivoPalabras)
    archivoPalabras.close()


def modificarPalabra(dicPalabras, palabraActual):
    """esta funcion chequea que una palabra este en el diccionario la cambia por la palabra que queremos"""
    palabraModificada = sg.PopupGetText('Modificar nombre: ', default_text=palabraActual)
    if (palabraModificada != palabraActual):
        if (ingresarPalabra(dicPalabras, palabraModificada)):
            eliminarPalabra(dicPalabras, palabraActual)
            return True
    return False


def eliminarPalabra(dicPalabras, palabra):
    """esta funcion es para buscar una palabra dentro del diccionario y luego eliminarla"""
    if (palabra in list(dicPalabras['NN'].keys())):
        del dicPalabras['NN'][palabra]
    elif (palabra in list(dicPalabras['JJ'].keys())):
        del dicPalabras['JJ'][palabra]
    elif (palabra in list(dicPalabras['VB'].keys())):
        del dicPalabras['VB'][palabra]


def esPalabraValida(palabra):
    """Esta funcion es para verificar si una palabra se encuentra en wiktionary"""
    if (Wiktionary().search(palabra) == None):
        return False
    else:
        return True


def GenerarReporte(texto):
    """esta funcion es para guardar en el archvio de reportes en el caso que no se encuentre"""
    try:
        archivoReporte = open('ArchivoReporte.txt', 'r+')
    except FileNotFoundError:
        archivoReporte = open('ArchivoReporte.txt', 'w')

    archivoReporte.write(texto + "\n")
    archivoReporte.close()


def ingresarPalabra(dicPalabras, text):
    """esta funcion verifica si es una palabra valida y cual es su clasificacion, y la agrega al diccionario"""
    try:
        clasificacion = parse(text).split('/')[1][0:2]

        if esPalabraValida(text):
            if (clasificacion == 'VB'):
                enInfinitivo = conjugate(text, INFINITIVE)
                articulo = Wiktionary(language='es').search(enInfinitivo)
            elif (clasificacion == 'JJ'):
                adjetivo = attributive(text, gender=NEUTRAL)
                articulo = Wiktionary(language='es').search(adjetivo)
            elif (clasificacion == 'NN'):
                articulo = Wiktionary(language='es').search(text)
            aux = str(articulo.sections)
            if 'ADJ' in aux.upper() and clasificacion == 'JJ':
                print('La palabra es un adjetivo')
            elif 'VERB' in aux.upper() and clasificacion == 'VB':
                print('La palabra es un verbo')
            elif 'SUST' in aux.upper() and clasificacion == 'NN':
                print('La palabra es un sustantivo')

            if (clasificacion != 'JJ' and clasificacion != 'NN' and clasificacion != 'VB'):
                GenerarReporte('La palabra ' + text + ' no existe en pattern.')

            print('La palabra es valida y es un', articulo.sections[3].title)
            dicPalabras[clasificacion][text] = buscarDefinicion(text)
            print(dicPalabras[clasificacion][text])

            return True
        else:
            if (clasificacion == 'JJ' or clasificacion == 'NN' or clasificacion == 'VB'):
                GenerarReporte(
                    'La palabra ' + text + ' no fue encontrada en Wiktionary, pero sí en pattern siendo un ' + clasificacion)
                dicPalabras[clasificacion][text] = sg.PopupGetText('Definicion: ')
                return True
            else:
                GenerarReporte('La palabra ' + text + ' no fue encontrada en Wiktionary y tampoco en pattern.')

    except TypeError:
        GenerarReporte('La palabra ' + text + ' no es valida.')
        print('La palabra ingresada no es valida.')

    return False


def clasificarPalabra(palabra):
    """esta funcion es para determinar que tipo de palabra es"""
    return parse(palabra).split('/')[1][0:2]


def DibujarGrilla(g, diccionario, coordenadas, dicSeleccion, configurado):
    """Esta funcion dibuja la sopa de letras"""
    def DefinirRango(clave):
        """Esta funcion sirve para saber el tamaño de la sopa de letras"""
        if int(configurado[clave]['cantidad']) > len(list(diccionario['clases'][clave].keys())):
            return len(diccionario['clases'][clave])
        else:
            return int(configurado[clave]['cantidad'])

    listaDePalabrasRandom = []
    copia = dict(diccionario.copy())

    def LlenarLista(clave):
        for i in range(0, DefinirRango(clave)):
            aux = random.choice(list(copia['clases'][clave].keys()))
            listaDePalabrasRandom.append(aux)
            del copia['clases'][clave][aux]

    # TAL VEZ PUSE AL REVES 'LARGO' Y 'ANCHO' EN ALGUN MOMENTO PUES EL LARGO DE VERTICAL ES EL ANCHO DE HORIZONTAL Y VISCEVERSA PERO ME DIO PAJA CAMBIARLO, JAJA SALUDOS
    # BOX_SIZE = 15
    # DIBUJA LOS CUADRADOS DE LA GRILLA
    orientacion = diccionario['orientacion']
    minus = diccionario['minusculas']
    cantidadTotal = configurado['NN']['cantidad'] + configurado['JJ']['cantidad'] + configurado['VB']['cantidad']

    for clases in diccionario['clases'].keys():
        LlenarLista(clases)

    palabraMasLarga = len(max(listaDePalabrasRandom, key=len))

    for filas in range(palabraMasLarga):
        for columnas in range(cantidadTotal * 2):
            if orientacion == 'horizontal':
                x = filas
                y = columnas
            else:
                x = columnas
                y = filas
            coordenadas[(x, y)] = {'letra': '', 'color': '',
                                   'casillero': g.DrawRectangle((x * BOX_SIZE + 5, y * BOX_SIZE + 3), (
                                   x * BOX_SIZE + BOX_SIZE + 5, y * BOX_SIZE + BOX_SIZE + 3), line_color='black'),
                                   'habilitado': True, 'seleccionado': False}

    posiblesFilas = list(range(0, cantidadTotal * 2))  # Filas en las que puede agregarse palabras

    for elemento in listaDePalabrasRandom:

        filaRandom = int(random.choice(posiblesFilas))  # fila o columna al azar para agregar la palabra
        r = int(random.randrange(
            (1 + (palabraMasLarga) - len(elemento))))  # posicion random dentro de la fila o columna elegida antes

        for pos in range(0,
                         r):  # en este primer for se completa con letras random los casilleros hasta que se llegue a la posicion para empezar a agregar la palabra
            if orientacion == 'vertical':
                # se cambia las coordenadas si es vertical u horizontal
                x = filaRandom
                y = pos
            else:
                x = pos
                y = filaRandom
            if minus:
                letraRandom = random.choice(string.ascii_lowercase)
            else:
                letraRandom = random.choice(string.ascii_uppercase)
            g.DrawText('{}'.format(letraRandom), (x * BOX_SIZE + 13, (y * BOX_SIZE + 20)), font='Courier 15')
            coordenadas[(x, y)]['letra'] = letraRandom

        listaTuplas = []
        for letra in range(0, len(elemento)):  # en este for se dibuja la palabra
            if orientacion == 'vertical':
                x = filaRandom
                y = (r + letra)
            else:
                x = (r + letra)
                y = filaRandom
            if minus:
                g.DrawText((elemento[letra].lower()), (x * BOX_SIZE + 13, (y * BOX_SIZE + 20)), font='Courier 15')
            else:
                g.DrawText((elemento[letra].upper()), (x * BOX_SIZE + 13, (y * BOX_SIZE + 20)), font='Courier 15')
            coordenadas[(x, y)]['letra'] = elemento[letra]
            listaTuplas.append((x, y))

        dicSeleccion[clasificarPalabra(elemento)]['palabras'].append(listaTuplas)

        for pos in range((r + len(elemento)),
                         (palabraMasLarga)):  # en este for se termina de completar con letras random
            if orientacion == 'vertical':
                x = filaRandom
                y = pos
            else:
                x = pos
                y = filaRandom
            if minus:
                letraRandom = random.choice(string.ascii_lowercase)
            else:
                letraRandom = random.choice(string.ascii_uppercase)
            g.DrawText('{}'.format(letraRandom), (x * BOX_SIZE + 13, (y * BOX_SIZE + 20)), font='Courier 15')
            coordenadas[(x, y)]['letra'] = letraRandom

        posiblesFilas.remove(filaRandom)

    for fila in range(0, palabraMasLarga):  # en este se llenan las filas y columnas que quedaron vacias
        for pos in posiblesFilas:
            if orientacion == 'vertical':
                x = pos
                y = fila
            else:
                x = fila
                y = pos
            if minus:
                letraRandom = random.choice(string.ascii_lowercase)
            else:
                letraRandom = random.choice(string.ascii_uppercase)
            g.DrawText('{}'.format(letraRandom), (x * BOX_SIZE + 13, (y * BOX_SIZE + 20)), font='Courier 15')
            coordenadas[(x, y)]['letra'] = letraRandom
    return listaDePalabrasRandom



def cuadradoHabilitado(coordenadas, tuplaClave):
    """Esta funcion sirve para corrobar que se pueda hacer click sobre el cuadrado"""
    return (coordenadas[tuplaClave]['habilitado'])


def Seleccionar(coordenadas, tuplaClave):
    """Esta funcion es para poder seleccionar un cuadrado habilitado"""
    if not coordenadas[tuplaClave]['seleccionado']:
        coordenadas[tuplaClave]['seleccionado'] = True
        return True

    coordenadas[tuplaClave]['seleccionado'] = False
    return False


def verificarPalabras(coordenadas, dicSeleccion):
    """Esta funcion es para verificar si la palabra ya fue encontrada en la sopa de letras"""
    listaEliminacion = []
    auxstr = ""
    for clases in dicSeleccion.keys():
        for lista in dicSeleccion[clases]['palabras']:
            listaTuplas = []
            for tuplas in lista:
                if (coordenadas[tuplas]['seleccionado']) and (
                        coordenadas[tuplas]['color'] == dicSeleccion[clases]['color']):
                    listaTuplas.append(tuplas)
            if (lista == listaTuplas):
                listaEliminacion.append(listaTuplas)
                auxstr = ''
                for letra in listaTuplas:
                    coordenadas[letra]['habilitado'] = False
                    auxstr = auxstr + coordenadas[letra]['letra']

    if (len(listaEliminacion) != 0):
        for clases in dicSeleccion.keys():
            for indice in listaEliminacion:
                if (indice in dicSeleccion[clases]['palabras']):
                    dicSeleccion[clases]['palabras'].remove(indice)
    return auxstr


def ganarJuego(dicSeleccion):
    """Esta funcion sirve para verificar cuando se gana el juego"""
    palabrasFaltantes = 0
    for clases in dicSeleccion.keys():
        for lista in dicSeleccion[clases]['palabras']:
            palabrasFaltantes = palabrasFaltantes + 1

    return palabrasFaltantes


def buscarDefinicion(palabra):
    """Esta funcion sirve para encontrar la definicion de la palabra"""
    try:
        articulo = Wiktionary(language="es").search(palabra)
        for elemento in articulo.sections:
            if "Etimología" in elemento.title:
                if "Si puedes," in elemento.content:
                    definicion = palabra.title()  # Se puede poner que no tenga ayuda. No se encuentra en wiktionary
                else:
                    definicion = elemento.content.split("[editar]")[1].split("\n\n")[1]
                    if "[" in elemento.content.split("[editar]")[1].split("\n\n")[1]:
                        definicion = definicion.split("[")[0]
                break
            else:
                definicion = palabra.title()
    except:
        definicion = palabra.title()

    return definicion


windowInicio = sg.Window('Bienvenido').Layout(leiauts.Inicio(sg))

while True:

    event, values = windowInicio.Read()

    if event is None or event == 'salir':

        break

    elif event == 'jugar':
        try:
            archivoConfig = open('archivoDeConfiguracion.json', 'r')
            diccionario = json.load(archivoConfig)
            archivoConfig.close()

            windowJugar = sg.Window('Sopa de letras').Layout(leiauts.Jugar(sg, diccionario['clases'])).Finalize()

            while True:
                eventos, val = windowJugar.Read()
                if eventos is None:
                    break
                elif eventos == 'fuera':
                    windowJugar.Hide()
                    break

                elif eventos == 'jugando':
                    ayuda = diccionario['ayuda']
                    palabras = list(diccionario['clases']['VB'].keys()) + list(
                        diccionario['clases']['JJ'].keys()) + list(diccionario['clases']['NN'].keys())

                    if (len(palabras) != 0):
                        cantidadDeFilas = len(
                            palabras) * 2  # si es en vertical, esto es el ancho de la grilla, si es horizontal, es el largo
                        palabraMasLarga = len(max(palabras,
                                                  key=len))  # si es vertical, esto define el largo, si es horizontal, define el ancho
                        conf = {'NN': {'cantidad': int(windowJugar.FindElement('cantSustantivos').Get()),
                                       'color': windowJugar.FindElement('auxSustantivos').Get()},
                                'JJ': {'cantidad': int(windowJugar.FindElement('cantAdjetivos').Get()),
                                       'color': windowJugar.FindElement('auxAdjetivos').Get()},
                                'VB': {'cantidad': int(windowJugar.FindElement('cantVerbos').Get()),
                                       'color': windowJugar.FindElement('auxVerbos').Get()}}
                        doblepalabras = (conf['NN']['cantidad'] + conf['JJ']['cantidad'] + conf['VB']['cantidad'])*2
                        X, Y = doblepalabras * (BOX_SIZE+1), palabraMasLarga * (BOX_SIZE+1)
                        visi = True
                        if diccionario["orientacion"] == "horizontal":
                            X, Y = Y, X
                        tuplatam = (X, Y)
                        if (conf['NN']['cantidad'] == 0 and conf['JJ']['cantidad'] == 0 and conf['VB'][
                            'cantidad'] == 0):
                            sg.Popup('Debe existir al menos una palabra para buscar en la sopa de letras.')
                        else:
                            if diccionario['orientacion'] == 'vertical':
                                windowJugando = sg.Window('Sopa de letras', size=(1300, 600), location=(0, 0)).Layout(
                                    leiauts.Jugando(sg, cantidadDeFilas, palabraMasLarga, diccionario['clases'], conf,
                                                    [], tuplatam, visi)).Finalize()
                            else:
                                windowJugando = sg.Window('Sopa de letras', size=(1300, 600), location=(0, 0)).Layout(
                                    leiauts.Jugando(sg, palabraMasLarga, cantidadDeFilas, diccionario['clases'], conf, [], tuplatam, visi)).Finalize()
                            g = windowJugando.FindElement('_GRAPH_')
                            coordenadas = {}
                            dicSeleccion = {
                                'NN': {'color': windowJugando.FindElement('NN').BackgroundColor, 'palabras': []},
                                'VB': {'color': windowJugando.FindElement('VB').BackgroundColor, 'palabras': []},
                                'JJ': {'color': windowJugando.FindElement('JJ').BackgroundColor, 'palabras': []}}
                            palabrasGrilla = DibujarGrilla(g, diccionario, coordenadas, dicSeleccion, conf)
                            dicGrilla = dict()
                            dicGrilla = ayudaa(palabrasGrilla, dicGrilla)
                            windowJugando.FindElement("lbox").Update(disabled=False)
                            windowJugando.FindElement("lbox").Update(values=dicGrilla.values())
                            windowJugando.FindElement("lbox").Update(disabled=True)
                            while True:
                                e, v = windowJugando.Read()
                                if e is None:
                                    break
                                elif e == 'out':

                                    sys.exit()
                                    break
                                elif e == 'NN' or e == 'VB' or e == 'JJ':
                                    colorSel = e

                                mouse = v['_GRAPH_']

                                if e == '_GRAPH_':
                                    if mouse == (None, None):
                                        continue
                                    try:
                                        box_x = mouse[0] // BOX_SIZE
                                        box_y = mouse[1] // BOX_SIZE
                                        tuplaClave = (box_x, box_y)

                                        if (cuadradoHabilitado(coordenadas, tuplaClave)):
                                            if (Seleccionar(coordenadas, tuplaClave)):

                                                g.TKCanvas.itemconfig(coordenadas[tuplaClave]['casillero'],
                                                                      fill=dicSeleccion[colorSel][
                                                                          'color'])  # pinta el cuadrado
                                                coordenadas[tuplaClave]['color'] = dicSeleccion[colorSel]['color']
                                            else:
                                                g.TKCanvas.itemconfig(coordenadas[tuplaClave]['casillero'],
                                                                      fill=g.BackgroundColor)
                                                coordenadas[tuplaClave]['color'] = g.BackgroundColor
                                    except NameError:
                                        sg.Popup('Debes seleccionar un color.')
                                    except KeyError:
                                        sg.Popup('Debes seleccionar dentro del rango de la sopa de letras.')



                                elif e == 'verificar':
                                    pal = verificarPalabras(coordenadas, dicSeleccion)
                                    palabrasFaltantes = ganarJuego(dicSeleccion)
                                    if pal.title() in dicGrilla.keys():
                                        del dicGrilla[pal.title()]
                                        sg.Popup("Bien! Solo te faltan "+str(
                                                     palabrasFaltantes) + ' palabras')
                                    else:
                                        sg.Popup("Segui participando, todavia te faltan "+str(
                                                     palabrasFaltantes) + ' palabras')
                                    windowJugando.FindElement("lbox").Update(disabled=False)
                                    windowJugando.FindElement("lbox").Update(values=dicGrilla.values())
                                    windowJugando.FindElement("lbox").Update(disabled=True)
                                    if (palabrasFaltantes == 0):
                                        sg.Popup('Felicitaciones', 'Has completado la sopa de letras correctamente')
                                elif e == 'ayuda':
                                    if ayuda:
                                        visi = not visi
                                        windowJugando.FindElement("lbox").Update(disabled=False)
                                        windowJugando.FindElement("lbox").Update(visible=visi)
                                        windowJugando.FindElement("lbox").Update(values=dicGrilla.values())
                                        windowJugando.FindElement("lbox").Update(disabled=True)
                                    else:
                                        sg.Popup('La ayuda se encuentra deshabilitada.')
                                elif e == 'pals':
                                    if ayuda:
                                        visi = not visi
                                        windowJugando.FindElement("lbox").Update(disabled=False)
                                        windowJugando.FindElement("lbox").Update(values=dicGrilla.keys())
                                        windowJugando.FindElement("lbox").Update(visible=visi)
                                        windowJugando.FindElement("lbox").Update(disabled=True)
                                    else:
                                        sg.Popup('La ayuda se encuentra deshabilitada.')
                    else:
                        sg.Popup(
                            'No hay ninguna palabra en la sopa de letras, configurala desde el boton "Configuracion"')
        except (FileNotFoundError):
            sg.Popup('No se ha configurado la sopa de letras. Por favor, hagalo clickeando el boton "Configuracion"')



    elif event == 'configuracion':

        try:
            archivoConfig = open('archivoDeConfiguracion.json', 'r', encoding="utf8")
            dicConfig = json.load(archivoConfig)

            listaPalabras = list(dicConfig['clases']['VB'].keys()) + list(dicConfig['clases']['JJ'].keys()) + list(
                dicConfig['clases']['NN'].keys())
            archivoConfig.close()

        except FileNotFoundError:

            listaPalabras = []
            dicConfig = {"clases": {"JJ": {}, "VB": {}, "NN": {}}, "orientacion": "horizontal", "ayuda": False,
                         "minusculas": False}

        windowConfig = sg.Window('Configuracion').Layout(leiauts.Configuracion(sg, listaPalabras, dicConfig))

        while True:
            e, v = windowConfig.Read()

            if e is None:
                break
            if e == 'volver':
                windowConfig.Hide()
                break
            elif e == 'cargar':
                try:
                    if (ingresarPalabra(dicConfig['clases'], v['palabra'])):
                        listaPalabras.append(v['palabra'])
                        windowConfig.FindElement('palabra').Update('')
                        windowConfig.FindElement('lista').Update(values=listaPalabras)
                        guardarArchivo(dicConfig)
                except IndexError:
                    sg.Popup('No escribiste ninguna palabra.')
            elif e == 'modificar':
                try:
                    if (modificarPalabra(dicConfig['clases'], v['lista'][0])):
                        listaPalabras = list(dicConfig['clases']['VB'].keys()) + list(
                            dicConfig['clases']['JJ'].keys()) + list(dicConfig['clases']['NN'].keys())
                        windowConfig.FindElement('lista').Update(values=listaPalabras)
                        guardarArchivo(dicConfig)
                except IndexError:
                    sg.Popup('Debes seleccionar una palabra.')
            elif e == 'eliminar':
                try:
                    eliminarPalabra(dicConfig['clases'], v['lista'][0])
                    listaPalabras.remove(v['lista'][0])
                    windowConfig.FindElement('lista').Update(values=listaPalabras)
                    guardarArchivo(dicConfig)
                except IndexError:
                    sg.Popup('Debes seleccionar una palabra.')

            elif e == 'guardar':

                if v['horizontal']:
                    dicConfig['orientacion'] = 'horizontal'
                else:
                    dicConfig['orientacion'] = 'vertical'

                dicConfig['ayuda'] = v['si']
                dicConfig['minusculas'] = v['minusculas']
                guardarArchivo(dicConfig)