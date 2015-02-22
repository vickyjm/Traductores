# -*- coding: UTF-8 -*-

##########################################
# CI3715 Traductores e Interpretadores   #
# Entrega 3. Grupo 6                     #
# Maria Victoria Jorge 11-10495          #
# Enrique Iglesias 11-10477              # 
##########################################

from SymTable import *
global errorDeclaracion
global TS
global numero
numero = 0
TS = None
errorDeclaracion = []

class Program:
    def __init__(self,inst):
        self.inst = inst

    def toString(self,tabs):
        return 'PROGRAM\n' + self.inst.toString(2)

    def check(self,line):
        return self.inst.check(line)

    def printSymTable(self,tabs):
        return self.inst.printSymTable(tabs)

class Bloque:
    def __init__(self,dec,exp):
        self.exp = exp
        self.dec = dec

    def toString(self,tabs):
        string = ' '*tabs + 'BLOCK_BEGIN\n'
        if (self.dec!=None):
            string += self.dec.toString(tabs + 2) 
        if (self.exp!=None):
            string += self.exp.toString(tabs + 2)
        string += ' '*tabs + 'BLOCK_END\n'
        return string

    def check(self,line):
        global TS
        if (self.dec != None):
            self.dec.check(line)
        if (self.exp != None):
            self.exp.check(line)
        if (self.dec != None):
            TS = TS.getFather()

    def printSymTable(self,tabs):
        if (isinstance(self.dec, Declarar)):
            string = ' '*tabs + 'SCOPE\n'
            string += self.dec.printSymTable(tabs + 2)
            if (self.exp != None):
                string += self.exp.printSymTable(tabs + 2)
            string += ' '*tabs + 'END_SCOPE\n'
            return string
        if (self.exp != None):
            self.exp.printSymTable(tabs)

class Declarar:
    def __init__(self,lista):
        self.lista = lista

    def toString(self,tabs):
        string = ' '*tabs + 'USING\n'
        string += self.lista.toString(tabs + 2) 
        string += ' '*tabs + 'IN\n'
        return string

    def check(self,line):
        global TS
        TS = Tabla(TS) #Enlazo las tablas
        self.lista.check(line)

    def printSymTable(self,tabs):
        return self.lista.printSymTable(tabs)


class Condicional:
    def __init__(self, cond, inst, inst2,linea,columna):
        self.cond = cond
        self.inst = inst
        self.inst2 = inst2
        self.linea = linea
        self.colum = columna

    def toString(self,tabs):
        string = ' '*tabs + 'IF\n'
        string += ' '*(tabs + 2) + 'condition\n'
        string += self.cond.toString(tabs + 4) 
        string += ' '*(tabs + 2) + 'THEN\n'
        string += self.inst.toString(tabs + 4) 
        if (self.inst2 != None):
            string += ' '*(tabs + 2) + 'ELSE\n'
            string += self.inst2.toString(tabs + 4) 
        return string

    def check(self,line):
        global errorDeclaracion
        global TS
        self.cond.check(line)
        if (isinstance(self.cond,Simple)):
            valores = TS.lookup(self.cond.valor)
            if (self.cond.tipo == 'id') and (valores != None) and (valores[1] != 'bool'):
                msg = "Error en linea "+str(self.linea - line) + ", columna " + str(self.colum)
                msg += ": Instruccion 'if' espera expresiones de tipo bool y no "+ valores[1] + "\n"
                errorDeclaracion.append(msg)    
            elif ((self.cond.tipo == 'int') or (self.cond.tipo == 'set')):
                msg = "Error en linea "+str(self.linea - line) + ", columna " + str(self.colum)
                msg += ": Instruccion 'if' espera expresiones de tipo bool y no "+ self.cond.tipo + "\n"
                errorDeclaracion.append(msg)    
        elif (self.cond.tipoExpresion() != 'bool'):
            msg = "Error en linea "+str(self.linea - line) + ", columna " + str(self.colum)
            msg += ": Instruccion 'if' espera expresiones de tipo bool y no "+ self.cond.tipoExpresion() + "\n"
            errorDeclaracion.append(msg)
        self.inst.check(line)
        if (self.inst2 != None):
            self.inst2.check(line)
        
    def printSymTable(self,tabs):
        string = self.inst.printSymTable(tabs)
        if (self.inst2 != None):
            string += self.inst2.printSymTable(tabs)
        return string

class Asignacion:
    def __init__(self,var,valor,linea,columna):
        self.var = var
        self.valor = valor
        self.linea = linea
        self.colum = columna

    def toString(self,tabs):
        string = ' '*tabs + 'ASSIGN\n'
        string += self.var.toString(tabs + 2) 
        string += ' '*(tabs + 2) + 'value\n'
        string += self.valor.toString(tabs + 4) 
        return string

    def check(self,line):
        global errorDeclaracion
        global TS
        if not(TS.contains(self.var.valor)):
            msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
            msg += ": La variable "+str(self.var.valor)+" no ha sido declarada\n"
            errorDeclaracion.append(msg)
        else:
            self.valor.check(line)
            info = TS.lookup(self.var.valor)
            if (isinstance(self.valor,Simple)):
                infoAsig = TS.lookup(self.valor.valor)
                if (self.valor.tipo == 'id') and (infoAsig != None) and (infoAsig[1] != info[1]):
                    msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                    msg += ": No puede asignar algo de tipo "+infoAsig[1]+" a una variable de tipo "+info[1]+"\n"
                    errorDeclaracion.append(msg)
                elif (self.valor.tipo != 'id') and (self.valor.tipo != info[1]):
                    msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                    msg += ": No puede asignar algo de tipo "+self.valor.tipo+" a una variable de tipo "+info[1]+"\n"
                    errorDeclaracion.append(msg)
            else:
                self.valor.check(line) #Reviso primero que la expresión sea correcta
                tipoOperador = self.valor.tipoExpresion()
                if (tipoOperador != info[1]):
                    msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                    msg += ": No puede asignar algo de tipo "+tipoOperador+"a una variable de tipo "+info[1]+"\n"
                    errorDeclaracion.append(msg)

    def printSymTable(self,tabs):
        return ''

class For:
    def __init__(self, id1, direc, exp, inst,linea,columna):
        self.id1 = id1
        self.direc = direc
        self.exp = exp
        self.inst = inst
        self.linea = linea
        self.colum = columna

    def toString(self,tabs):
        string = ' '*tabs + 'FOR\n'
        string += self.id1.toString(tabs + 2) 
        string += ' '*(tabs + 2) + 'direction\n'
        string += ' '*(tabs + 4) + self.direc.lower() +'\n'
        string += ' '*(tabs + 2) + 'IN\n'
        string += self.exp.toString(tabs + 4) 
        string += ' '*(tabs + 2) + 'DO\n'
        string += self.inst.toString(tabs + 4)
        return string

    def check(self,line):
        global errorDeclaracion
        global TS
        TS = Tabla(TS)
        TS.insert(self.id1.valor,0,'int')
        self.exp.check(line)
        if (isinstance(self.exp,Simple)):
            valores = TS.lookup(self.exp.valor)
            if (self.exp.tipo == 'id') and (valores != None) and (valores[1] != 'set'):
                msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                msg += ": Solo acepta expresiones de tipo 'set' no "+valores[1]+"\n"
                errorDeclaracion.append(msg)

            elif ((self.exp.tipo == 'bool') or (self.exp.tipo == 'int')):
                msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                msg += ": Solo acepta expresiones de tipo 'set' no "+self.exp.tipo+"\n"
                errorDeclaracion.append(msg)
        else:
            if (self.exp.tipoExpresion() != 'set'):
                msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                msg += ": Solo acepta expresiones de tipo 'set' no "+self.exp.tipoExpresion()+"\n"
                errorDeclaracion.append(msg)
        self.inst.check(line)
        TS = TS.getFather()

    def printSymTable(self,tabs):
        string = ' '*tabs + 'SCOPE\n'
        string += ' '*(tabs +2) + 'Variable: ' + self.id1.valor + ' | Type: int' 
        string += ' | Value: 0\n'
        string += self.inst.printSymTable(tabs + 2)
        string += ' '*tabs + 'END_SCOPE\n'
        return string


class While:
    def __init__(self,exp,inst,linea,columna):
        self.exp = exp
        self.inst = inst
        self.linea = linea
        self.colum = columna

    def toString(self,tabs):
        string = ' '*tabs + 'WHILE\n'
        string += ' '*(tabs + 2) + 'condition\n'
        string += self.exp.toString(tabs + 4) 
        string += ' '*tabs + 'DO\n' 
        string += self.inst.toString(tabs + 2)
        return string

    def check(self,line):
        global errorDeclaracion
        self.exp.check(line)
        if (isinstance(self.exp,Simple)): 
            valores = TS.lookup(self.exp.valor)
            if (self.exp.tipo == 'id') and (valores != None) and (valores[1] != 'bool'):
                msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                msg += ": Solo acepta expresiones de tipo 'bool' no"+valores[1]+"\n"
                errorDeclaracion.append(msg)
            elif ((self.exp.tipo == 'int') or (self.exp.tipo == 'set')):
                msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                msg += ": Solo acepta expresiones de tipo 'bool' no"+self.exp.tipo+"\n"
                errorDeclaracion.append(msg)
        else:
            if (self.exp.tipoExpresion() != 'bool'):
                msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                msg += ": Solo acepta expresiones de tipo 'bool' no"+self.exp.tipoExpresion()+"\n"
                errorDeclaracion.append(msg)
        self.inst.check(line)

    def printSymTable(self,tabs):
        return self.inst1.printSymTable(tabs)

class EntradaSalida:
    def __init__(self,flag,exp):
        self.flag = flag
        self.exp = exp

    def toString(self,tabs):
        string = ' '*tabs + self.flag.upper() + '\n'
        if (self.flag =='scan'):
            string += self.exp.toString(tabs + 2)
        else:
            string += ' '*(tabs + 2) + 'elements\n'
            string += self.exp.toString(tabs + 4) 
            if (self.flag =='println'):
                string += ' '*(tabs + 4) + 'string\n'
                string += ' '*(tabs + 6) + '"\\n"' + '\n'
        return string

    def check(self,line):
        global errorDeclaracion
        global TS
        if (self.flag == 'scan'):
            valores = TS.lookup(self.exp)
            if (valores != None):
                if (valores[1] == 'set'):
                    msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                    msg += ": La instrucción 'scan' solo acepta variables de tipo 'int' y 'bool' no "+valores[1]+"\n"
                    errorDeclaracion.append(msg)
        self.exp.check(line)

    def printSymTable(self,tabs):
        return ''

class Opbin:
    def __init__(self,izq,op,der,linea,columna):
        self.izq = izq
        self.op = op
        self.der = der
        self.opMixtos = set(['<+>','<->','<*>','</>','@'])
        self.linea = linea
        self.colum = columna

    def tipoExpresion(self):
        operadores = {
            '+'     : 'int',
            '-'     : 'int',
            '*'     : 'int',
            '/'     : 'int',
            '%'     : 'int',
            '++'    : 'set',
            '><'    : 'set',
            '\\'    : 'set',
            '<+>'   : 'set',
            '<->'   : 'set',
            '<*>'   : 'set',
            '</>'   : 'set',
            '<%>'   : 'set',
            '<'     : 'bool',
            '<='    : 'bool',
            '>'     : 'bool',
            '>='    : 'bool',
            '=='    : 'bool',
            '/='    : 'bool',
            '@'     : 'bool',
            'or'    : 'bool',
            'and'   : 'bool'
        }
        return operadores.get(self.op)

    def toString(self,tabs):
        operadores = {
            '+'     : 'PLUS',
            '-'     : 'MINUS',
            '*'     : 'TIMES',
            '/'     : 'DIVIDE',
            '%'     : 'MODULE',
            '++'    : 'UNION',
            '><'    : 'INTERSECTION',
            '\\'    : 'DIFERENCE',
            '<+>'   : 'PLUS_MAP',
            '<->'   : 'MINUS_MAP',
            '<*>'   : 'TIMES_MAP',
            '</>'   : 'DIVIDE_MAP',
            '<%>'   : 'MODULE_MAP',
            '<'     : 'LESS',
            '<='    : 'LESS_EQUAL',
            '>'     : 'GREATER',
            '>='    : 'GREATER_EQUAL',
            '=='    : 'EQUALS',
            '/='    : 'NOT_EQUAL',
            '@'     : 'AT',
            'or'    : 'Or',
            'and'   : 'And'
        }
        string = ' '*tabs + operadores[self.op] +' ' + self.op + '\n'
        if (isinstance(self.izq,Simple)):
            if (self.izq.tipo=='id'):
                string += ' '*(tabs + 2) + 'variable\n'
                string += ' '*(tabs + 4) + self.izq.valor + '\n'
            else:
                string += self.izq.toString(tabs + 2) 
        else:
            string += self.izq.toString(tabs + 2) 

        if (isinstance(self.der,Simple)):
            if (self.der.tipo=='id'):
                string += ' '*(tabs + 2) + 'variable\n'
                string += ' '*(tabs + 4) + self.der.valor + '\n'
            else:
                string += self.der.toString(tabs + 2) 
        else:
            string += self.der.toString(tabs + 2) 
        return string

    def check(self,line):
        global errorDeclaracion
        global TS
        tipoOperador = self.tipoExpresion()

        if (isinstance(self.izq,Simple)):
            valores = TS.lookup(self.izq.valor)
            if (self.izq.tipo == 'id') and (valores != None):
                if (self.op in self.opMixtos) and (valores[1] != 'int'):
                    msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                    msg += ": El operador "+self.op+" espera una expresion de tipo int no " + valores[1] + "\n"
                    errorDeclaracion.append(msg)    
                elif (valores[1] != tipoOperador):
                    msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                    msg += ": El operador "+self.op+" solo acepta expresiones de tipo '"+tipoOperador+"' no "+valores[1]+"\n"
                    errorDeclaracion.append(msg)
            elif (self.op in self.opMixtos) and (self.izq.tipo != 'int'):
                msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                msg += ": El operador "+self.op+" espera una expresion de tipo int no " + self.izq.tipo + "\n"
                errorDeclaracion.append(msg)
            elif (self.izq.tipo != tipoOperador):
                    msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                    msg += ": El operador "+self.op+" solo acepta expresiones de tipo '"+tipoOperador+"' no "+self.izq.tipo+"\n"
                    errorDeclaracion.append(msg)
            if (isinstance(self.der,Simple)):
                valores = TS.lookup(self.der.valor)
                if (self.der.tipo == 'id') and (valores != None):
                    if (self.op in self.opMixtos) and (valores[1] != 'int'):
                        msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                        msg += ": El operador "+self.op+" espera una expresion de tipo int no " + valores[1] + "\n"
                        errorDeclaracion.append(msg)    
                    elif (valores[1] != tipoOperador):
                        msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                        msg += ": El operador "+self.op+" solo acepta expresiones de tipo '"+tipoOperador+"' no "+valores[1]+"\n"
                        errorDeclaracion.append(msg)
                elif (self.op in self.opMixtos) and (self.der.tipo != 'set'):
                    msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                    msg += ": El operador "+self.op+" espera una expresion de tipo set no " + self.der.tipo + "\n"
                    errorDeclaracion.append(msg)
                elif (self.der.tipo != tipoOperador):
                    msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                    msg += ": El operador "+self.op+" solo acepta expresiones de tipo '"+tipoOperador+"' no "+self.der.tipo+"\n"
                    errorDeclaracion.append(msg) 
            else:
                if (self.op in self.opMixtos) and (self.der.tipoExpresion() != 'set'):
                    msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                    msg += ": El operador "+self.op+" espera una expresion de tipo set no " + self.der.tipoExpresion() + "\n"
                    errorDeclaracion.append(msg)
                elif (self.der.tipoExpresion() == tipoOperador):
                    self.der.check(line)
                else:
                    msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                    msg += ": El operador "+self.op+" solo acepta expresiones de tipo '"+tipoOperador+"' no "+self.der.tipoExpresion()+"\n"
                    errorDeclaracion.append(msg)
        else:
            if (self.op in self.opMixtos) and (self.izq.tipoExpresion() != 'int'):
                msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                msg += ": El operador "+self.op+" espera una expresion de tipo int no " + self.izq.tipoExpresion() + "\n"
                errorDeclaracion.append(msg)
            elif (self.izq.tipoExpresion() == tipoOperador):
                self.izq.check(line)
            else:
                msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                msg += ": El operador "+self.op+" solo acepta expresiones de tipo '"+tipoOperador+"' no "+self.izq.tipoExpresion()+"\n"
                errorDeclaracion.append(msg)
            if (isinstance(self.der,Simple)):
                valores = TS.lookup(self.der.valor)
                if (self.der.tipo == 'id') and (valores != None):
                    if (self.op in self.opMixtos) and (valores[1] != 'int'):
                        msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                        msg += ": El operador "+self.op+" espera una expresion de tipo int no " + valores[1] + "\n"
                        errorDeclaracion.append(msg)    
                    elif (valores[1] != tipoOperador):
                        msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                        msg += ": El operador "+self.op+" solo acepta expresiones de tipo '"+tipoOperador+"' no "+valores[1]+"\n"
                        errorDeclaracion.append(msg)
                elif (self.op in self.opMixtos) and (self.der.tipo != 'set'):
                    msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                    msg += ": El operador "+self.op+" espera una expresion de tipo set no " + self.der.tipo + "\n"
                    errorDeclaracion.append(msg)
                elif (self.der.tipo != tipoOperador):
                    msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                    msg += ": El operador "+self.op+" solo acepta expresiones de tipo '"+tipoOperador+"' no "+self.der.tipoExpresion()+"\n"
                    errorDeclaracion.append(msg) 
            else:
                if (self.op in self.opMixtos) and (self.der.tipoExpresion() != 'set'):
                    msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                    msg += ": El operador "+self.op+" espera una expresion de tipo set no " + self.der.tipoExpresion() + "\n"
                    errorDeclaracion.append(msg)
                elif (self.der.tipoExpresion() == tipoOperador):
                    self.der.check(line)
                else:
                    msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                    msg += ": El operador "+self.op+" solo acepta expresiones de tipo '"+tipoOperador+"' no "+self.der.tipoExpresion()+"\n"
                    errorDeclaracion.append(msg)

    def printSymTable(self,tabs):
        return ''


class Simple:
    def __init__(self,tipo,valor,linea,columna):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.colum = columna

    def toString(self,tabs):
        if (self.tipo=='id'):
            string = ' '*tabs + 'variable' + '\n'
            string += ' '*(tabs + 2) + str(self.valor) + '\n'
        elif (self.tipo=='set'):
            string = ' '*tabs + self.tipo + '\n'
            if (self.valor != None):
                string += self.valor.toString(tabs + 2)
        else:    
            string = ' '*tabs + self.tipo + '\n'
            string += ' '*(tabs + 2) + str(self.valor) + '\n'
        return string

    def check(self,line):
        global errorDeclaracion
        global TS
        if (self.tipo == 'id') and (TS.contains(self.valor) == None):
            msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.column)
            msg += ": La variable "+self.valor+" no ha sido declarada\n"
            errorDeclaracion.append(msg)

    def printSymTable(self,tabs):
        return ''


class Repeat:
    def __init__(self,inst1,exp,inst2,linea,columna):
        self.inst1 = inst1
        self.exp = exp
        self.inst2 = inst2
        self.linea = linea
        self.colum = columna

    def toString(self,tabs):
        string = ' '*tabs + 'REPEAT\n'
        string += self.inst1.toString(tabs + 2) 
        string += ' '*tabs + 'WHILE\n'
        string += ' '*(tabs + 2) + 'condition\n'
        string += self.exp.toString(tabs + 4) 
        if (self.inst2!=None):
            string += ' '*tabs + 'DO\n'
            string += self.inst2.toString(tabs + 2)
        return string

    def check(self,line):
        global errorDeclaracion
        global TS
        self.inst1.check(line)
        if (isinstance(self.exp,Simple)):
            valores = TS.lookup(self.exp.valor)
            if (self.exp.tipo == 'id') and (valores != None) and (valores[1]!='bool'):
                msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                msg += ": Solo acepta expresiones de tipo 'bool' no"+valores[1]+"\n"
                errorDeclaracion.append(msg)
            elif ((self.exp.tipo == 'set') or (self.exp.tipo == 'int')):
                msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                msg += ": Solo acepta expresiones de tipo 'bool' no"+self.exp.tipoExpresion()+"\n"
                errorDeclaracion.append(msg)
        else:
            if (self.exp.tipoExpresion() == 'bool'):
                self.exp.check(line)
            else:
                msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                msg += ": Solo acepta expresiones de tipo 'bool' no"+self.exp.tipoExpresion()+"\n"
                errorDeclaracion.append(msg)
        if (self.inst2 != None):
            self.inst2.check(line)

    def printSymTable(self,tabs):
        string = self.inst1.printSymTable(tabs)
        if (self.inst2 != None):
            string += self.inst2.printSymTable(tabs)
        return string

class Uniop:
    def __init__(self,op,val,linea,columna):
        self.val = val
        self.op = op
        self.linea = linea
        self.colum = columna

    def tipoExpresion(self):
        operadores = {
            '-'     : 'int',
            '<?'    : 'set',
            '>?'    : 'set',
            '$?'    : 'set',
            'not'   : 'bool'
        }
        return operadores.get(self.op)

    def toString(self,tabs):
        operadores = {
            '-'     : 'UMINUS',
            '<?'    : 'MIN_SET',
            '>?'    : 'MAX_SET',
            '$?'    : 'SIZE',
            'not'   : 'Not'
        }
        string = ' '*tabs + operadores[self.op] + '\n'
        string += self.val.toString(tabs + 2) 
        return string

    def check(self,line):
        global errorDeclaracion
        global TS
        tipoOperador = self.tipoExpresion()
        if (isinstance(self.val,Simple)):
            valores = TS.lookup(self.val.valor)
            if (self.val.tipo == 'id') and (valores != None) and (valores[1] != tipoOperador):
                msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                msg += ": "+self.op+" solo acepta expresiones de tipo '"+tipoOperador+"' no "+valores[1]+"\n"
                errorDeclaracion.append(msg)
            elif (self.val.tipo != tipoOperador) and (self.val.tipo != 'id'):
                msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                msg += ": "+self.op+" solo acepta expresiones de tipo '"+tipoOperador+"' no "+self.val.tipo+"\n"
                errorDeclaracion.append(msg)
        else:
            if (self.val.tipoExpresion() != tipoOperador):
                msg = "Error en la linea "+str(self.linea - line)+", columna "+str(self.colum)
                msg += ": "+self.op+" solo acepta expresiones de tipo '"+tipoOperador+"' no "+self.val.tipoExpresion()+"\n"
                errorDeclaracion.append(msg)
        self.val.check(line)

    def printSymTable(self,tabs):
        return ''


class CadenaString:
    def __init__(self,string):
        self.string = string

    def toString(self,tabs):
        string = ' '*tabs + 'string\n'
        string += ' '*(tabs + 2) + '"' + self.string + '"' + '\n'
        return string

    def check(self,line):
        pass

    def printSymTable(self,tabs):
        return ''

class ListaInstruccion:
    def __init__(self,inst1,inst2):
        self.inst1 = inst1
        self.inst2 = inst2

    def toString(self,tabs):
        string = self.inst1.toString(tabs)
        if (self.inst2 != None):
            string += self.inst2.toString(tabs)
        return string

    def check(self,line):
        self.inst1.check(line)
        if (self.inst2 != None):
            self.inst2.check(line)

    def printSymTable(self,tabs):
        string = self.inst1.printSymTable(tabs)
        if (self.inst2 != None):
            string += self.inst2.printSymTable(tabs)
        return string

class ListaDeclaracion:
    def __init__(self, tipo, idList, decList):
        self.tipo = tipo
        self.idList = idList
        self.decList = decList

    def toString(self,tabs):
        string = ' '*tabs + self.tipo + '\n'
        string += self.idList.toString(tabs + 2)
        if (self.decList!=None):
            string += self.decList.toString(tabs)
        return string

    def check(self,line):
        global TS
        global errorDeclaracion
        valDefecto = {
            'int'   :   0,
            'bool'  :   False,
            'set'   :   set()
        }
        lista = self.idList
        if (TS.isInTable(lista.id1.valor)):
                msg = "Error en linea "+ lista.id1.getLinea() + ", columna " + lista.id1.getColumna()
                msg += ": La variable "+ lista.id1.valor +" ya se encuentra declarada en este alcance\n"
                errorDeclaracion.append(msg)
        else:
            TS.insert(lista.id1.valor,valDefecto.get(self.tipo),self.tipo)

        if (isinstance(lista.idList,ListaID)):
            while (lista.idList != None):
                if (TS.isInTable(lista.idList.id1.valor)):
                    msg = "Error en linea "+ lista.idList.getLinea() + ", columna " + lista.idList.getColumna()
                    msg += ": La variable "+ lista.idList.id1.valor +" ya se encuentra declarada en este alcance\n"
                    errorDeclaracion.append(msg)
                else:
                    TS.insert(lista.idList.id1.valor,valDefecto.get(self.tipo),self.tipo)
                lista = lista.idList

        if (isinstance(self.decList,ListaDeclaracion)):
            self.decList.check(line)

    def printSymTable(self,tabs):
        valDefecto = {
            'int'   :   0,
            'bool'  :   False,
            'set'   :   '{}'
        }
        lista = self.idList
        string = ' '*tabs + 'Variable: ' + lista.id1.valor + ' | Type: ' + self.tipo
        string += ' | Value: ' + str(valDefecto.get(self.tipo)) + '\n'
        if (isinstance(lista.idList,ListaID)):
            while (lista.idList != None):
                string += ' '*tabs + 'Variable: ' + lista.idList.id1.valor + ' | Type: ' + self.tipo
                string += ' | Value: ' + str(valDefecto.get(self.tipo)) + '\n'
                lista = lista.idList

        if (isinstance(self.decList,ListaDeclaracion)):
            string += self.decList.printSymTable(tabs)
        return string

class ListaID:
    def __init__(self,idList,id1):
        self.idList = idList
        self.id1 = id1

    def toString(self,tabs):
        string = ''
        if (self.idList != None):
            string += self.idList.toString(tabs)
        string += self.id1.toString(tabs)
        return string

    def check(self,line):
        pass

    def printSymTable(self,tabs):
        return ''

class ListaNumero:
    def __init__(self,numList,num):
        self.numList = numList
        self.num = num

    def toString(self,tabs):
        string = ''
        if (self.numList!=None):
            string += self.numList.toString(tabs)
        string += self.num.toString(tabs)
        return string

    def check(self,line):
        global TS
        global errorDeclaracion
        if (isinstance(num,Simple)): 
            if ((self.num.tipo == 'bool') or (self.num.tipo == 'set')):
                msg = "Error en linea "+ self.num.getLinea() + ", columna " + self.num.getColumna() #ESTO HAY QUE CAMBIARLO
                msg += ": Los conjuntos solo aceptan elementos de tipo 'int' no de tipo "+ self.num.tipo + '\n'
                errorDeclaracion.append(msg)
            elif (num.tipo == 'id'): # Chequear si corresponde a un entero
                tipo = TS.lookup(self.num.valor)
                if (tipo != None): #Existe en alguna tabla
                    if (tipo[1] != 'int'):
                        msg = "Error en linea "+ self.num.getLinea() + ", columna " + self.num.getColumna() #ESTO HAY QUE CAMBIARLO
                        msg += ": Los conjuntos solo aceptan elementos de tipo 'int' no de tipo "+ tipo[1] + '\n'
                        errorDeclaracion.append(msg)
                else:
                    msg = "Error en la linea "+self.num.getLinea()+", columna "+self.num.getColumna() #ESTO HAY QUE CAMBIARLO
                    msg += ": La variable "+self.num.valor+" no ha sido declarada\n"
                    errorDeclaracion.append(msg)

        self.numList.check(line)

    def printSymTable(self,tabs):
        return ''

class ListaImpresion:
    def __init__(self,listExp,exp):
        self.listExp = listExp
        self.exp = exp

    def toString(self,tabs):
        string = ''
        if (self.listExp!=None):
            string += self.listExp.toString(tabs)
        string += self.exp.toString(tabs)
        return string

    def check(self,line):
        self.exp.check(line)
        self.listExp.check(line)

    def printSymTable(self,tabs):
        return ''
        
precedence = (
    ('right','ELSE'),
    ('left', 'Or'),
    ('left', 'And'),        
    ('right', 'Not'),
    ('nonassoc','Greater','GreaterEqual', 'Less','LessEqual'),    
    ('right', 'MinSet', 'MaxSet', 'Size'),
    ('left', 'TimesMap','DivideMap','ModuleMap'),
    ('left','PlusMap','MinusMap'),
    ('left','Intersection'),
    ('left','Union','Diference'),
    ('left', 'Plus', 'Minus'),
    ('left','Times','Divide','Module'),
    ('left','Equals','NotEqual'),
    ('nonassoc','At'),
    ('right', 'UMINUS')
    )

def p_program(p):
    '''PROGRAM : Program INST'''
    p[0] = Program(p[2])

def p_tipos(p):
    ''' TIPOS   : Int 
                | Set 
                | Boolean '''
    p[0] = p[1]

def p_enumList(p): 
    '''ENUM_LIST    : String
                    | EXP
                    | ENUM_LIST Comma EXP
                    | ENUM_LIST Comma String'''
    if (len(p)==2):
        if (isinstance(p[1],str)):
            p[0] = CadenaString(p[1])
        else:
            p[0] = p[1]
    else:
        if (isinstance(p[3],str)):
            p[0] = ListaImpresion(p[1],CadenaString(p[3]))
        else:
            p[0] = ListaImpresion(p[1],p[3])


def p_declarar(p):
    '''DECLARAR : Using DEC_LIST In'''
    p[0] = Declarar(p[2])

def p_epsilon(p):
    ''' EPSILON : '''
    pass

def p_decList(p):
    '''DEC_LIST   : TIPOS ID_LIST Semicolon DEC_LIST
                  | TIPOS ID_LIST Semicolon '''

    if (len(p)==4):
        p[0] = ListaDeclaracion(p[1],p[2],None)
    else:
        p[0] = ListaDeclaracion(p[1],p[2],p[4])


def p_instList(p):
    '''INST_LIST    : INST Semicolon INST_LIST
                    | EPSILON '''
    if (len(p)==4):
        p[0] = ListaInstruccion(p[1],p[3])
    elif (len(p)==2):
        pass


def p_idList(p):
    '''ID_LIST    : ID_LIST Comma ID 
                    | ID '''
    if (len(p)==2):
        p[0] = ListaID(None,Simple('id',p[1],p.lineno(1),p.lexpos(1)))
    else:
        p[0] = ListaID(p[1],Simple('id',p[3],p.lineno(1),0))

def p_exp(p):
    '''EXP  : Number
            | ID
            | OpenCurly NUMBER_LIST CloseCurly
            | OpenCurly CloseCurly
            | Lparen EXP Rparen
            | Minus EXP %prec UMINUS
            | EXP Plus EXP
            | EXP Minus EXP
            | EXP Times EXP
            | EXP Divide EXP
            | EXP Module EXP
            | EXP PlusMap EXP
            | EXP MinusMap EXP
            | EXP TimesMap EXP
            | EXP DivideMap EXP
            | EXP ModuleMap EXP
            | EXP Union EXP
            | EXP Intersection EXP
            | EXP Diference EXP
            | MaxSet EXP
            | MinSet EXP
            | Size EXP
            | True
            | False 
            | EXP And EXP
            | EXP Or EXP
            | Not EXP
            | EXP Equals EXP
            | EXP Greater EXP
            | EXP GreaterEqual EXP
            | EXP Less EXP
            | EXP LessEqual EXP
            | EXP NotEqual EXP
            | EXP At EXP '''

    if (len(p)==2):
        if (isinstance(p[1],int)):
            tipo = 'int'
        elif (p[1]=='true') or (p[1]=='false'):
            tipo = 'bool'
        else:
            tipo = 'id'
        p[0] = Simple(tipo,p[1],p.lineno(1),0)

    elif (len(p)==3):
        if (p[1] == '{'):
            p[0] = Simple('set',None,p.lineno(1),0)
        else:
            p[0] = Uniop(p[1],p[2],p.lineno(1),0)

    else:
        if (p[1]=='('):
            p[0] = p[2]
        elif (p[1]=='{'):
            p[0] = Simple('set',p[2],p.lineno(1),0)
        else:
            p[0] = Opbin(p[1],p[2],p[3],p.lineno(1),0)


def p_inst(p):
    '''INST : ID Assign EXP
            | OpenCurly DECLARAR INST_LIST CloseCurly
            | OpenCurly INST_LIST CloseCurly
            | Scan ID
            | Print ENUM_LIST
            | Println ENUM_LIST
            | IF Lparen EXP Rparen INST
            | IF Lparen EXP Rparen INST ELSE INST
            | FOR ID DIRECCION EXP DO INST
            | REPEAT INST WHILE EXP
            | REPEAT INST WHILE EXP DO INST
            | WHILE EXP DO INST'''
    if (len(p)==3):
        if (p[1]=='scan'):
            p[0] = EntradaSalida(p[1],Simple('id',p[2],p.lineno(1),0))
        else:
            p[0] = EntradaSalida(p[1],p[2])

    elif (len(p)==4):
        if (p[1]=='{'):
            p[0] = Bloque(None,p[2])
        else:
            p[0] = Asignacion(Simple('id',p[1],p.lineno(1),0),p[3],p.lineno(1),0)
    elif (len(p)==5):
        if (p[1]=='{'):
            p[0] = Bloque(p[2],p[3])
        elif (p[1]=='repeat'):
            p[0] = Repeat(p[2],p[4],None,p.lineno(1),0)
        else:
            p[0] = While(p[2],p[4],p.lineno(1),0)

    elif (len(p)==6):
        p[0] = Condicional(p[3],p[5],None,p.lineno(1),0)

    elif (len(p)==7):
        if (p[1]=='for'):
            p[0] = For(Simple('int',p[2],p.lineno(1),0),p[3],p[4],p[6],p.lineno(1),0)
        else:
            p[0] = Repeat(p[2],p[4],p[6],p.lineno(1),0)
    else:
        p[0] = Condicional(p[3],p[5],p[7],p.lineno(1),0)

def p_direccion(p):
    ''' DIRECCION : MIN
                  | MAX '''
    p[0] = p[1]

def p_numberList(p):
    '''NUMBER_LIST  : NUMBER_LIST Comma EXP 
                    | EXP '''
    if (len(p)==2):
        p[0] = p[1]
    else:
        p[0] = ListaNumero(p[1],p[3])

def find_row(input):
    nro_linea = 0
    with open(input,'r') as archivo:
        for linea in archivo:
            nro_linea += 1
    return nro_linea

# Permite encontrar el numero de columna de la linea actual
def find_column(input,token):
    last_cr = input.rfind('\n',0,token.lexpos)
    if last_cr < 0:
        last_cr = -1
    column = token.lexpos - last_cr
    return column 

