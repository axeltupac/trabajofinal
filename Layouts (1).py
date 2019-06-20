def Inicio(sg):
    """esta funcion es la pantalla de inicio de la sopa de letras"""
    inicio = [[sg.Frame('Inicio', layout=[
        [sg.Txt('Bienvenido al juego interactivo...')],
        [sg.ReadButton('Jugar', size=(20, 2), key='jugar')],
        [sg.ReadButton('Configuracion', size=(20, 2), key='configuracion')],
        [sg.ReadButton('Salir', size=(20, 2), key='salir')],
        [sg.Txt('                  ')]])]]

    return inicio


def Configuracion(sg, listaPalabras, diccionario):
    """Esta funcion tiene todas las posibles configuraciones de la sopa de letra"""
    configuracion = [[sg.Frame('Ingreso de datos', layout=[
        [sg.Txt('Ingrese las palabras a encontrar en la sopa de letras')],
        [sg.InputText(key='palabra'), sg.ReadButton('Cargar', key='cargar')],
        [sg.Listbox(values=listaPalabras, size=(15, 3), key='lista'), sg.ReadButton('Modificar', key='modificar'),
         sg.ReadButton('Eliminar', key='eliminar')]])],
                     [sg.Frame('Orientacion de las palabras', layout=[
                         [sg.Radio(group_id=0, text='Horizontal', key='horizontal',
                                   default=diccionario['orientacion'] == 'horizontal')],
                         [sg.Radio(group_id=0, text='Vertical', key='vertical',
                                   default=diccionario['orientacion'] == 'vertical')]]), sg.Frame('Formato', layout=[
                         [sg.Radio(group_id=1, text='Minusculas', key='minusculas', default=diccionario['minusculas'])],
                         [sg.Radio(group_id=1, text='Mayusculas', key='mayusculas',
                                   default=not diccionario['minusculas'])]])],
                     [sg.Txt(
                         'Desea brindarle ayuda al jugador En caso afirmativo, se mostrara en pantalla la definicion de la palabra a encontrar. De lo contrario, solo se mostrara la cantidad de palabras a buscar.')],
                     [sg.Radio(group_id=2, text='Si', key='si', default=diccionario['ayuda'])],
                     [sg.Radio(group_id=2, text='No', key='no', default=not diccionario['ayuda']),
                      sg.ReadButton('Guardar', key='guardar'), sg.ReadButton('Volver', key='volver')]]

    return configuracion


def Jugar(sg, diccionario):
    """"esta funcion es para elegir las opciones de la sopa de letras y genera la sopa de letras"""
    canS = 'La cantidad maxima de sustantivos posibles es:' + str(len(list(diccionario['NN'].keys())))
    canA = 'La cantidad maxima de adjetivos posibles es:' + str(len(list(diccionario['JJ'].keys())))
    canV = 'La cantidad maxima de verbos posibles es:' + str(len(list(diccionario['VB'].keys())))
    wjugar = [[sg.Text('Sopa de letras'), background_color=colorInterfaz, sg.Text('', key='_OUTPUT_')],
              [sg.Frame('Defina los colores', layout=[
                  [sg.Txt('Sustantivos'), sg.ColorChooserButton('Seleccionar', target=(0, 2), key='ColorSustantivos'),
                   sg.InputText('#ffff80', key='auxSustantivos', visible=False)],
                  [sg.Txt('Verbos'), sg.ColorChooserButton('Seleccionar', target=(1, 2), key='ColorVerbos'),
                   sg.Input('#00ffff', key='auxVerbos', visible=False)],
                  [sg.Txt('Adjetivos'), sg.ColorChooserButton('Seleccionar', target=(2, 2), key='ColorAdjetivos'),
                   sg.Input('#c0c0c0', key='auxAdjetivos', visible=False)]]),
               sg.Frame('Cantidad de palabras a encontrar', layout=[
                   [sg.Txt('Sustantivos'),
                    sg.InputText(str(len(list(diccionario['NN'].keys()))), key='cantSustantivos', size=(10, 1)),
                    sg.Txt(canS)],
                   [sg.Txt('Verbos'),
                    sg.InputText(str(len(list(diccionario['VB'].keys()))), key='cantVerbos', size=(10, 1)),
                    sg.Txt(canV)],
                   [sg.Txt('Adjetivos'),
                    sg.InputText(str(len(list(diccionario['JJ'].keys()))), key='cantAdjetivos', size=(10, 1)),
                    sg.Txt(canA)]])],
              [sg.Txt('')],
              [sg.ReadButton('Jugar', key='jugando'), sg.ReadButton('Salir', key='fuera')]]

    return wjugar


def Jugando(sg, cantFilas, mayor, diccionario, conf, listayuda, tuplatam, visi):
    """Esta funcion es la jugabilidad de la sopa de letras"""
    colorInterfaz = definirColor(diccionario['oficina'])
    windowJugando = [[sg.Text('Primero debes seleccionar el color de la palabra que vas a marcar (clickea sobre el color)')],
                     [sg.Text('Verbos'), sg.Text('', enable_events=True, click_submits=True, size=(5, 1),
                                                 background_color=conf['VB']['color'], key='VB'),
                      sg.Text('Sustantivos'),
                      sg.Text('', enable_events=True, size=(5, 1), background_color=conf['NN']['color'], key='NN'),
                      sg.Text('Adjetivos'),
                      sg.Text('', enable_events=True, size=(5, 1), key='JJ', background_color=conf['JJ']['color']),
                      sg.ReadButton('Verificar', key='verificar'), sg.ReadButton('Ayudas', key='ayuda'),sg.ReadButton('Palabras', key='pals')],
                     [sg.Graph(tuplatam, (0, tuplatam[1]), (tuplatam[0], 0), key='_GRAPH_', change_submits=True, drag_submits=False,
                               background_color='white'), sg.Listbox(values=listayuda, background_color="#090470", font="Times", disabled=True,
                          size=(50, len(listayuda)), visible=visi, key="lbox")],
                     [sg.ReadButton('Salir', key='out')]]
    return windowJugando