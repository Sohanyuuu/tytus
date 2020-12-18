import Gramatica as g
import tablasimbolos as TS
from expresiones import *
from instrucciones import *
from reporteAST import *
from temporal import *
from storageManager import jsonMode as EDD
import Funciones as f
import math
import random
from tkinter import *
import tkinter.filedialog
import tkinter.messagebox


#---------variables globales
listaInstrucciones = []
listaTablas = [] #guarda las cabeceras de las tablas creadas
outputTxt = [] #guarda los mensajes a mostrar en consola
baseActiva = "" #Guarda la base temporalmente activa
#--------Ejecucion Datos temporales-----------
def insertartabla(columnas,nombre):
    nuevaTabla=Tabla_run()
    Tabla_run.nombre=nombre
    Tabla_run.Atributos=columnas

    global listaTablas
    listaTablas.append(nuevaTabla)

def EliminarTablaTemp(baseAc,nombre):
    global listaTablas
    pos=0
    #all para eliminar todas las tablas de una base de datos
    if(nombre=='all'):
        while pos< len(listaTablas):
            if(listaTablas[pos].basepadre==baseAc):
                listaTablas.pop(pos)
            else:
                pos=pos+1
    else:
        while pos< len(listaTablas):
            if(listaTablas[pos].nombre==nombre and listaTablas[pos].basepadre==baseAc):
                listaTablas.pop(pos)
                break
            else:
                pos=pos+1

def agregarMensjae(tipo,mensaje):
    global outputTxt
    txtOut=MensajeOut()
    txtOut.tipo=tipo
    txtOut.mensaje=mensaje
    outputTxt.append(txtOut)

def use_db(nombre):
    global baseActiva
    baseActiva = nombre

'''def elim_use():
    global baseActiva
    baseActiva = ""'''

#---------Ejecucion Funciones EDD-------------
def crear_BaseDatos(instr,ts):
    nombreDB=resolver_operacion(instr.nombre,ts).lower()
    
    msg='Creando base de datos: '+nombreDB
    agregarMensjae('normal',msg)

    #result=0 operacion exitosa
    #result=1 error en la operacion
    #result=2 base de datos existente       
    result = EDD.createDatabase(nombreDB)

    if instr.reemplazar and result==2:
        #eliminar
        EDD.dropDatabase(nombreDB)
        EliminarTablaTemp(nombreDB,'all')#eliminar los temporales
        #crear
        result = EDD.createDatabase(nombreDB)
        if result==1:
            msg='Error en EDD'
            agregarMensjae('error',msg)
        else:
            msg='Fue Reemplazada'
            agregarMensjae('alert',msg)

    elif instr.verificacion:
        if result==0:
            msg='Todo OK'
            agregarMensjae('exito',msg)
        elif result==2 :
            msg='existe pero se omite error'
            agregarMensjae('alert',msg)
            #si retorna error no se muestra
    else:
        if result==0:
            msg='Todo OK'
            agregarMensjae('exito',msg)
        elif result==2:
            msg='Error base de existente: '+nombreDB
            agregarMensjae('error',msg)
        elif result==1:
            msg='Error en EDD'
            agregarMensjae('error',msg)

    #print('reemplazar:',instr.reemplazar,'verificar:',instr.verificacion,'nombre:',instr.nombre,'propietario:',instr.propietario,'modo:',instr.modo)

def eliminar_BaseDatos(instr,ts):
    nombreDB=str(resolver_operacion(instr.nombre,ts)).lower()
    eliminarOK=False;
    #result=0 operacion exitosa
    #result=1 error en la operacion
    #result=2 base de datos no existente  
    result = EDD.dropDatabase(nombreDB)
    msg='Eliminado Base de datos: '+nombreDB;
    agregarMensjae('normal',msg)
    
    if(instr.existencia):
        if(result==0):
            eliminarOK=True;
            msg='Todo OK'
            agregarMensjae('exito',msg)
        else:
            eliminarOK=False
            msg='no se muestra el error'
            agregarMensjae('alert',msg)
            #si retorna error no se muestra
    else:
        if(result==0):
            eliminarOK=True;
            msg='Todo OK'
            agregarMensjae('exito',msg)
        elif(result==1):
            eliminarOK=False
            msg='Error en EDD'
            agregarMensjae('error',msg)
        else:
            msg='Error base de datos no existente: '+nombreDB
            agregarMensjae('error',msg)
    
    if eliminarOK:
        EliminarTablaTemp(nombreDB,'all')#eliminar los temporales
        #elim_use()

    #print('nombre:',instr.nombre,'validarExistencia',instr.existencia)

def mostrar_db(instr,ts):
    #retorna una lista[db1,db2...], si no hay estara vacia[]
    result=EDD.showDatabases()
    msg='Lista de bases de datos'
    agregarMensjae('normal',msg)

    if not result:
        msg='No existen bases de datos ...' 
        agregarMensjae('alert',msg)   
    else:
        for val in result:
            agregarMensjae('exito',val)

def eliminar_Tabla(instr,ts):
    nombreT=''
    nombreT=resolver_operacion(instr.nombre,ts).lower()

    #Valor de retorno: 0 operación exitosa
    # 1 error en la operación, 
    # 2 database no existente, 
    # 3 table no existente.
    result=EDD.dropTable(baseActiva,nombreT)
    eliminarOK=False;

    msg='Eliminar Tabla:'+nombreT
    agregarMensjae('normal',msg)
    if(instr.existencia):
        if(result==0):
            msg='Tabla eliminada'
            agregarMensjae('exito',msg)
            eliminarOK=True
        else:
            msg='se omite error'
            agregarMensjae('alert',msg)
    else:
        if(result==0):
            msg='Tabla eliminada'
            agregarMensjae('exito',msg)
            eliminarOK=True
        elif(result==1):
            msg='Error en EDD'
            agregarMensjae('error',msg)
        elif(result==2):
            msg='no existe la base de datos activa:'+baseActiva
            agregarMensjae('error',msg)
        elif(result==3):
            msg='Tabla no existe:'+nombreT
            agregarMensjae('error',msg)
        
    if eliminarOK:
        EliminarTablaTemp(baseActiva,nombreT)


    #print('nombre:',instr.nombre,'validarExistencia',instr.existencia)

def seleccion_db(instr,ts):
    nombreDB = resolver_operacion(instr.nombre,ts).lower()
    result=EDD.showDatabases()
    msg='Seleccionando base de datos: '+nombreDB
    agregarMensjae('normal',msg)
    if not result: # Lista Vacia
        msg='No existen bases de datos ...'
        agregarMensjae('alert',msg)  
    elif nombreDB in result: # Encontrada
        msg='Base de datos seleccionada'
        agregarMensjae('exito',msg)
        use_db(nombreDB)
    else: # No encontrada
        msg='Base de datos \"'+str(nombreDB)+'\" no registrada'
        agregarMensjae('error',msg)
        
#---------pendientes-----------------------
def crear_Tabla(instr,ts):
    #Pendiente
    # -foraneas
    # -default igual al tipo de la columna
    # -tipo columna TYPE
    # -zonahoraria
    # -check
    # -herencia

    nombreT=resolver_operacion(instr.nombre,ts).lower()
    listaColumnas=[]
    crearOK=True
    pkCompuesta=False
    msg='Creando Tabla:'+nombreT
    agregarMensjae('normal',msg)
    contC=0# variable para contar las columnas a mandar a EDD

    print('padre:',instr.padre)
    #recorrer las columnas
    for colum in instr.columnas :
        colAux=Columna_run()#columna temporal para almacenar
        if isinstance(colum, llaveTabla) :
            if(colum.tipo==True):
                if(pkCompuesta==False):
                    pkCompuesta=True#primer bloque pk(list)
                    #pk compuesta, revisar la lista
                    for pkC in colum.columnas:
                        exCol=False
                        for lcol in listaColumnas:
                            if(lcol.nombre==pkC.lower()):
                                exCol=True
                                if(lcol.primary==None):
                                    lcol.primary=True
                                else:
                                    crearOK=False
                                    msg='primary key repetida:'+pkC.lower()
                                    agregarMensjae('error',msg)   
                        if(exCol==False):
                            crearOK=False
                            msg='No se puede asignar como primaria:'+pkC.lower()
                            agregarMensjae('error',msg)
                else:
                    crearOK=False
                    msg='Solo puede existir un bloque de PK(list)'
                    agregarMensjae('error',msg)
            else:
                #bloque de foraneas
                print('llaves Primaria:',colum.tipo,'lista:',colum.columnas,'tablaref',colum.referencia,'listaref',colum.columnasRef)
        elif isinstance(colum, columnaTabla) :
            contC=contC+1
            colAux.nombre=resolver_operacion(colum.id,ts).lower()#guardar nombre col
            #revisar columnas repetidas
            pos=0
            colOK=True
            while pos< len(listaColumnas):
                if(listaColumnas[pos].nombre==colAux.nombre):
                    crearOK=False;
                    colOK=False
                    msg='nombre de columna repetido:'+colAux.nombre
                    agregarMensjae('error',msg)
                    break;
                else:
                    pos=pos+1
            #si no existe el nombre de la columna revisa el resto de errores
            if(colOK):
                if isinstance(colum.tipo,Operando_ID):
                    colAux.tipo=resolver_operacion(colum.tipo,ts).lower()#guardar tipo col
                    #revisar la lista de Types
                    crearOK=False
                    msg='No existe el tipo '+colAux.tipo+' en la columna '+colAux.nombre
                    agregarMensjae('error',msg)
                else:
                    colAux.tipo=colum.tipo.lower() #guardar tipo col
                if(colum.valor!=False):
                    if(colAux.tipo=='varchar' or colAux.tipo=='char'):
                        if(len(colum.valor)==1):
                            errT=True;#variable error en p varchar(p)
                            if isinstance(colum.valor[0],Operando_Numerico):
                                val=resolver_operacion(colum.valor[0],ts)
                                if(type(val) == int):
                                    colAux.size=val
                                    errT=False#no existe error
                            if errT:
                                crearOK=False
                                msg='el tipo '+colAux.tipo+' acepta enteros como parametro: '+colAux.nombre
                                agregarMensjae('error',msg)
                        else:
                            crearOK=False
                            msg='el tipo '+colAux.tipo+' solo acepta 1 parametro: '+colAux.nombre
                            agregarMensjae('error',msg)
                    elif(colAux.tipo=='decimal' or colAux.tipo=='numeric' or colAux.tipo=='double precision'):
                        if(len(colum.valor)==1):
                            errT=True;#variable error en p varchar(p)
                            if isinstance(colum.valor[0],Operando_Numerico):
                                val=resolver_operacion(colum.valor[0],ts)
                                if(type(val) == int):
                                    colAux.size=val
                                    errT=False#no existe error
                            if errT:
                                crearOK=False
                                msg='el tipo '+colAux.tipo+' acepta enteros como parametro: '+colAux.nombre
                                agregarMensjae('error',msg)
                        elif(len(colum.valor)==2):
                            errT=True;#variable error en p varchar(p)
                            if (isinstance(colum.valor[0],Operando_Numerico) and isinstance(colum.valor[1],Operando_Numerico)):
                                val1=resolver_operacion(colum.valor[0],ts)
                                val2=resolver_operacion(colum.valor[1],ts)
                                if(type(val1) == int and type(val2) == int):
                                    colAux.size=val1
                                    colAux.precision=val2
                                    errT=False#no existe error
                            if errT:
                                crearOK=False
                                msg='el tipo '+colAux.tipo+' acepta enteros como parametro: '+colAux.nombre
                                agregarMensjae('error',msg)
                        else:
                            crearOK=False
                            msg='el tipo '+colAux.tipo+' acepta maximo 2 parametro: '+colAux.nombre
                            agregarMensjae('error',msg)
                    else:
                        crearOK=False
                        msg='el tipo '+colAux.tipo+' no acepta parametros:'+colAux.nombre
                        agregarMensjae('error',msg)
                if(colum.zonahoraria!=False):
                    '''aca se debe verificar la zonahoraria es una lista'''
                    print('zonahoraria',colum.zonahoraria)
                if(colum.atributos!=False):
                    #aca se debe verificar la lista de atributos de una columna
                    for atributoC in colum.atributos :
                        if isinstance(atributoC, atributoColumna):
                            if(atributoC.default!=None):
                                if(colAux.default==None):
                                    colAux.default=resolver_operacion(atributoC.default,ts)#guardar default
                                else:
                                    crearOK=False
                                    msg='atributo default repetido en Col:'+colAux.nombre
                                    agregarMensjae('error',msg)
                            elif(atributoC.constraint!=None):
                                if(colAux.constraint==None):
                                    colAux.constraint=atributoC.constraint#guardar constraint
                                else:
                                    crearOK=False
                                    msg='atributo constraint repetido en Col:'+colAux.nombre
                                    agregarMensjae('error',msg)
                            elif(atributoC.null!=None):
                                if(colAux.anulable==None):
                                    colAux.anulable=atributoC.null#guardar anulable
                                else:
                                    crearOK=False
                                    msg='atributo anulable repetido en Col:'+colAux.nombre
                                    agregarMensjae('error',msg)
                            elif(atributoC.unique!=None):
                                if(colAux.unique==None):
                                    colAux.unique=atributoC.unique#guardar unique
                                else:
                                    crearOK=False
                                    msg='atributo unique repetido en Col:'+colAux.nombre
                                    agregarMensjae('error',msg)
                            elif(atributoC.primary!=None):
                                if(colAux.primary==None):
                                    colAux.primary=atributoC.primary#guardar primary
                                else:
                                    crearOK=False
                                    msg='atributo primary repetido en Col:'+colAux.nombre
                                    agregarMensjae('error',msg)
                            elif(atributoC.check != None):
                                #el atributo check trae otra lista
                                print('check:',atributoC.check)
                                for exp in atributoC.check:
                                    print('resultado: ',resolver_operacion(exp,ts))
                listaColumnas.append(colAux)
 
                
            

    #analisas si las columnas estan bien
    #buscar las tablas de una base de datos retorna una lista de tablas
    if(crearOK):
        result=EDD.showTables(baseActiva)
        if(result!=None):
            for tab in result:
                if tab==nombreT:
                    msg='Error la tabla ya existe:'+nombreT
                    agregarMensjae('error',msg)
                    crearOK=False
                    break
            if crearOK:
                EDD.createTable(baseActiva,nombreT,contC)
                insertartabla(listaColumnas,nombreT)
                msg='Todo OK'
                agregarMensjae('exito',msg)
        else:
            msg='no existe la base de datos activa:'+baseActiva
            agregarMensjae('error',msg)

def crear_Type(instr,ts):
    nombreT=resolver_operacion(instr.nombre,ts).lower()
    msg='Creacion de Type: '+nombreT
    agregarMensjae('normal',msg)
    if baseActiva != "":
        result=EDD.showTables(baseActiva)
        cont=0
        flag=False
        lvalores=[]
        if instr.valores is not None:  
            if nombreT in result: # Repetido
                msg='Nombre repetido ...'
                agregarMensjae('error',msg)
            else:
                for valor in instr.valores: # Verificacion tipos
                    val=resolver_operacion(valor,ts)
                    if isinstance(val, str):
                        lvalores.append(resolver_operacion(valor,ts))
                        cont=cont+1
                if cont != len(instr.valores):
                    msg='No todos los valores son del mismo tipo'
                    agregarMensjae('error',msg)
                else:
                    flag=True
            if(flag): # crea e inserta valores
                respuestatype=EDD.createTable(baseActiva,nombreT,cont)
                if respuestatype==0:
                    msg='Type registrado con exito'
                    agregarMensjae('exito',msg)
                    insertartabla(None,nombreT)
                    respuestavalores=EDD.insert(baseActiva,nombreT,lvalores)
                    if respuestavalores==0:
                        msg='con valores: '+str(lvalores)
                        agregarMensjae('exito',msg)
                    elif respuestavalores==1:
                        msg='Error insertando valores'
                        agregarMensjae('error',msg)
                    elif respuestavalores==2:
                        msg='Base de datos no existe'
                        agregarMensjae('error',msg)
                    elif respuestavalores==3:
                        msg='Type no encontrado'
                        agregarMensjae('error',msg)
                elif respuestatype==1:
                    msg='Error al crear type'
                    agregarMensjae('error',msg)
                elif respuestatype==2:
                    msg='Base de datos no existe'
                    agregarMensjae('error',msg)
                elif respuestatype==3:
                    msg='Nombre repetido ...'
                    agregarMensjae('error',msg)
    else:
        msg='No hay una base de datos activa'
        agregarMensjae('alert',msg)


def insertar_en_tabla(instr,ts):
    print('nombre:',instr.nombre,'valores:',instr.valores)
    nombreT=''
    nombreT=resolver_operacion(instr.nombre,ts)
    values=''

    for val in instr.valores:
        values+=str(resolver_operacion(val,ts))+' '

    global outputTxt
    outputTxt+='\n> Insertado en Tabla: '+nombreT
    outputTxt+='\n> Valores: '+values
    outputTxt+='\n> '+str(len(instr.valores))+' Filas afectadas'

def actualizar_en_tabla(instr,ts):
    print('nombre:',instr.nombre,'condicion:',instr.condicion,'valores:',instr.valores)
    nombreT=''
    nombreT=resolver_operacion(instr.nombre,ts)
    values=''

    for val in instr.valores:
        values+=resolver_operacion(val.nombre,ts)+'='+str(resolver_operacion(val.valor,ts))+' '

    global outputTxt
    outputTxt+='\n> Actualizado en Tabla: '+nombreT
    outputTxt+='\n> Valores: '+values
    outputTxt+='\n> '+str(len(instr.valores))+' Filas afectadas'

def eliminar_de_tabla(instr,ts):
    print('nombre:',instr.nombre,'condicion:',instr.condicion)
    nombreT=''
    nombreT=resolver_operacion(instr.nombre,ts)

    global outputTxt
    outputTxt+='\n> Eliminacion de Tabla: '+nombreT


def AlterDBF(instr,ts):
    print("nombre:",instr.Id,"Tipo:",instr.TipoCon,"Valor:",instr.valor)
     
def AlterTBF(instr,ts):
    print("nombre:",instr.Id,"Cuerpo:",instr.cuerpo)



def resolver_operacion(operacion,ts):
    if isinstance(operacion, Operacion_Logica_Unaria):
        op = resolver_operacion(operacion.op, ts)
        if isinstance(op, bool):
            return not(op)
        else:
            print('Error: No se permite operar los tipos involucrados')
    elif isinstance(operacion, Operacion_Logica_Binaria):
        op1 = resolver_operacion(operacion.op1,ts)
        op2 = resolver_operacion(operacion.op2,ts)
        if isinstance(op1, bool) and isinstance(op2, bool):
            if operacion.operador == OPERACION_LOGICA.AND: return op1 and op2
            elif operacion.operador == OPERACION_LOGICA.OR: return op1 or op2 
        else:
            print('Error: No se permite operar los tipos involucrados')
    elif isinstance(operacion, Operacion_Relacional):
        op1 = resolver_operacion(operacion.op1,ts)
        op2 = resolver_operacion(operacion.op2,ts)
        if isinstance(op1, (int,float)) and isinstance(op2, (int,float)):
            if operacion.operador == OPERACION_RELACIONAL.IGUAL: return op1 == op2
            elif operacion.operador == OPERACION_RELACIONAL.DIFERENTE: return op1 != op2
            elif operacion.operador == OPERACION_RELACIONAL.MAYORIGUALQUE: return op1 >= op2
            elif operacion.operador == OPERACION_RELACIONAL.MENORIGUALQUE: return op1 <= op2
            elif operacion.operador == OPERACION_RELACIONAL.MAYOR_QUE: return op1 > op2
            elif operacion.operador == OPERACION_RELACIONAL.MENOR_QUE: return op1 < op2
        elif isinstance(op1, (str)) and isinstance(op2, (str)):
            if operacion.operador == OPERACION_RELACIONAL.IGUAL: return op1 == op2
            elif operacion.operador == OPERACION_RELACIONAL.DIFERENTE: return op1 != op2
            elif operacion.operador == OPERACION_RELACIONAL.MAYORIGUALQUE: return op1 >= op2
            elif operacion.operador == OPERACION_RELACIONAL.MENORIGUALQUE: return op1 <= op2
            elif operacion.operador == OPERACION_RELACIONAL.MAYOR_QUE: return op1 > op2
            elif operacion.operador == OPERACION_RELACIONAL.MENOR_QUE: return op1 < op2
        else:
            print('Error: No se permite operar los tipos involucrados') 
    elif isinstance(operacion, Operacion_Aritmetica):
        op1 = resolver_operacion(operacion.op1,ts)
        op2 = resolver_operacion(operacion.op2,ts)
        if isinstance(op1, (int,float)) and isinstance(op2, (int,float)):
            if operacion.operador == OPERACION_ARITMETICA.MAS: return op1 + op2
            elif operacion.operador == OPERACION_ARITMETICA.MENOS: return op1 - op2
            elif operacion.operador == OPERACION_ARITMETICA.POR: return op1 * op2
            elif operacion.operador == OPERACION_ARITMETICA.DIVIDIDO: return op1 / op2
            elif operacion.operador == OPERACION_ARITMETICA.POTENCIA: return op1 ** op2
            elif operacion.operador == OPERACION_ARITMETICA.MODULO: return op1 % op2
        else:
            print('Error: No se permite operar los tipos involucrados') 
    elif isinstance(operacion, Operacion_Especial_Binaria):
        op1 = resolver_operacion(operacion.op1,ts)
        op2 = resolver_operacion(operacion.op2,ts)
        if isinstance(op1, int) and isinstance(op2, int):
            if operacion.operador == OPERACION_ESPECIAL.AND2: return op1 & op2
            elif operacion.operador == OPERACION_ESPECIAL.OR2: return op1 | op2
            elif operacion.operador == OPERACION_ESPECIAL.XOR: return op1 ^ op2
            elif operacion.operador == OPERACION_ESPECIAL.DEPDER: return op1 >> op2
            elif operacion.operador == OPERACION_ESPECIAL.DEPIZQ: return op1 << op2
        else:
            print('Error: No se permite operar los tipos involucrados')
    elif isinstance(operacion, Operacion_Especial_Unaria):
        op = resolver_operacion(operacion.op,ts)
        if isinstance(op, (int,float)):
            if operacion.operador == OPERACION_ESPECIAL.SQRT2: return op ** (1/2)
            elif operacion.operador == OPERACION_ESPECIAL.CBRT2: return op ** (1/3)
            elif operacion.operador == OPERACION_ESPECIAL.NOT2: 
                if isinstance(op, int): return ~op
                else: print('Error: No se permite operar los tipos involucrados')
            else:
                print('Error: No se permite operar los tipos involucrados')
    elif isinstance(operacion, Negacion_Unaria):
        op = resolver_operacion(operacion.op,ts)
        if isinstance(op, (int,float)):
            return op * -1
        else:
            print('Error: No se permite operar los tipos involucrados')
    elif isinstance(operacion, Operando_Booleano):
        return operacion.valor
    elif isinstance(operacion, Operando_Numerico):
        return operacion.valor
    elif isinstance(operacion, Operando_Cadena):
        return operacion.valor
    elif isinstance(operacion, Operando_ID):
        return operacion.id 
    elif isinstance(operacion, Operacion_Math_Unaria):
        op = resolver_operacion(operacion.op,ts)
        print("Entre a math unaria")
        if isinstance(op, (int,float)):
            if operacion.operador == OPERACION_MATH.ABS: return abs(op) 
            elif operacion.operador == OPERACION_MATH.CBRT: return f.func_cbrt(op)
            elif operacion.operador == OPERACION_MATH.CEIL: return math.ceil(op)
            elif operacion.operador == OPERACION_MATH.CEILING: return math.ceil(op)
            elif operacion.operador == OPERACION_MATH.DEGREES: return math.degrees(op)
            elif operacion.operador == OPERACION_MATH.EXP: return math.exp(op)
            elif operacion.operador == OPERACION_MATH.FACTORIAL: return math.factorial(op)
            elif operacion.operador == OPERACION_MATH.FLOOR: return math.floor(op)
            elif operacion.operador == OPERACION_MATH.LN: return math.log(op)
            elif operacion.operador == OPERACION_MATH.LOG: return math.log10(op)
            elif operacion.operador == OPERACION_MATH.RADIANS: return math.radians(op)
            elif operacion.operador == OPERACION_MATH.SIGN: return f.func_sign(op)
            elif operacion.operador == OPERACION_MATH.SQRT: return  math.sqrt(op)
            elif operacion.operador == OPERACION_MATH.TRUNC: return math.trunc(op)

            elif operacion.operador == OPERACION_MATH.ACOS: return math.acos(op)
            elif operacion.operador == OPERACION_MATH.ACOSD: return math.acos(math.radians(op))
            elif operacion.operador == OPERACION_MATH.ASIN: return math.asin(op)
            elif operacion.operador == OPERACION_MATH.ASIND: return math.asin(math.radians(op))
            elif operacion.operador == OPERACION_MATH.ATAN: return math.atan(op)
            elif operacion.operador == OPERACION_MATH.ATAND: return math.atan(math.radians(op))
            elif operacion.operador == OPERACION_MATH.ATAN2: return math.atan2(op)
            elif operacion.operador == OPERACION_MATH.ATAN2D: return math.atan2(math.radians(op))
            elif operacion.operador == OPERACION_MATH.COS: return math.cos(op)
            elif operacion.operador == OPERACION_MATH.COSD: return math.cos(math.radians(op))
            elif operacion.operador == OPERACION_MATH.COT: return f.func_cot(op)
            elif operacion.operador == OPERACION_MATH.COTD: return f.func_cot(math.radians(op))
            elif operacion.operador == OPERACION_MATH.SIN: return math.sin(op)
            elif operacion.operador == OPERACION_MATH.SIND: return math.sin(math.radians(op))
            elif operacion.operador == OPERACION_MATH.TAN: return math.tan(op)
            elif operacion.operador == OPERACION_MATH.TAND: return math.tan(math.radians(op))
            elif operacion.operador == OPERACION_MATH.SINH: return math.sinh(op)
            elif operacion.operador == OPERACION_MATH.COSH: return math.cosh(op)
            elif operacion.operador == OPERACION_MATH.TANH: return math.tanh(op)
            elif operacion.operador == OPERACION_MATH.ASINH: return math.asinh(op)
            elif operacion.operador == OPERACION_MATH.ACOSH: return math.acosh(op)
            elif operacion.operador == OPERACION_MATH.ATANH: return math.atanh(op)

    elif isinstance(operacion, Operacion_Math_Binaria):
        op1 = resolver_operacion(operacion.op1,ts)
        op2 = resolver_operacion(operacion.op2,ts)
        if isinstance(op1,(int,float)) and isinstance(op2,(int,float)):
            if operacion.operador == OPERACION_MATH.DIV: return op1//op2
            elif operacion.operador == OPERACION_MATH.MOD: return math.fmod(op1,op2)
            elif operacion.operador == OPERACION_MATH.GCD: return math.gcd(op1,op2)
            elif operacion.operador == OPERACION_MATH.POWER: return math.pow(op1,op2)
            elif operacion.operador == OPERACION_MATH.ROUND: return f.func_round(op1,op2)
            
    elif isinstance(operacion, Operacion_Definida):
        if operacion.operador == OPERACION_MATH.PI: return math.pi
        elif operacion.operador == OPERACION_MATH.RANDOM: return f.func_random() 

    elif isinstance(operacion, Operacion_Strings):
        op = resolver_operacion(operacion.cadena,ts)
        if isinstance (op,(str)):
            if operacion.operador == OPERACION_BINARY_STRING.MD5: return f.func_md5(op)
            elif operacion.operador == OPERACION_BINARY_STRING.SHA256: return f.func_md5(op)
            elif operacion.operador == OPERACION_BINARY_STRING.LENGTH: return f.func_length(op)
    
    elif isinstance(operacion,Operacion_String_Compuesta):
        op1 = resolver_operacion(operacion.op1,ts)
        op2 = resolver_operacion(operacion.op2,ts)
        op3 = resolver_operacion(operacion.op3,ts)
        if isinstance(op1,(str)) and isinstance(op2,(int)) and isinstance(op3,(int)) :
            if operacion.operador == OPERACION_BINARY_STRING.SUBSTR: return f.func_substring(op1,op2,op3)
            elif operacion.operador == OPERACION_BINARY_STRING.SUBSTRING: return f.func_substring(op1,op2,op3)
    

def procesar_instrucciones(instrucciones, ts) :
    ## lista de instrucciones recolectadas
    global listaInstrucciones 
    listaInstrucciones  = instrucciones
    if instrucciones is not None:
        for instr in instrucciones :
            if isinstance(instr, CrearBD) : crear_BaseDatos(instr,ts)
            elif isinstance(instr, CrearTabla) : crear_Tabla(instr,ts)
            elif isinstance(instr, CrearType) : crear_Type(instr,ts)
            elif isinstance(instr, EliminarDB) : eliminar_BaseDatos(instr,ts)
            elif isinstance(instr, EliminarTabla) : eliminar_Tabla(instr,ts)
            elif isinstance(instr, Insertar) : insertar_en_tabla(instr,ts)
            elif isinstance(instr, Actualizar) : actualizar_en_tabla(instr,ts)
            elif isinstance(instr, Eliminar) : eliminar_de_tabla(instr,ts)
            elif isinstance(instr, DBElegida) : seleccion_db(instr,ts)
            elif isinstance(instr, MostrarDB) : mostrar_db(instr,ts)
            elif isinstance(instr, ALTERDBO) : AlterDBF(instr,ts)
            elif isinstance(instr, ALTERTBO) : AlterTBF(instr,ts)
            else : print('Error: instrucción no válida')
    else:
        agregarMensjae('error','El arbol no se genero debido a un error en la entrada')







def Analisar(input):
    global outputTxt
    outputTxt=[]
    EDD.dropAll() #eliminar para ir haciendo pruebas
    instrucciones = g.parse(input)
    print(instrucciones)
    ts_global = TS.TablaDeSimbolos()
    procesar_instrucciones(instrucciones,ts_global)

    #crea la consola y muestra el resultado
    '''consola = tkinter.Tk() # Create the object
    consola.geometry('950x200')
    text = tkinter.Text(consola,height=200, width=1280)
    consola.title("Consola")
    text.pack()
    text.insert(END,outputTxt)'''
    return outputTxt

#Metodos para graficar el ast 
def generarAST():
    global listaInstrucciones
    astGraph = DOTAST()
    astGraph.getDot(listaInstrucciones)

