# -*- coding: UTF-8 -*-

class Tabla:
	def __init__(self,padre):
		self.dic = {}
		self.padre = padre

	def insert(self,clave,valor,tipo):
		if not(clave in self.dic.keys()):
			self.dic[clave] = [valor,tipo]

	def delete(self,clave):
		if (clave in self.dic.keys()):
			del self.dic[clave]

	def update(self,clave,valor,tipo):
		if (clave in self.dic.keys()):
			self.dic[clave] = [valor,tipo]
		else: 
			if (self.padre != None):
				self.padre.update(clave,valor,tipo)

	def contains(self,clave):
		if not(self.isInTable(clave)):
			return self.padre.contains(clave)
		return self.isInTable(clave)

	def isInTable(self,clave):
		return clave in self.dic.keys()

	def lookup(self,clave):
		if (clave in self.dic.keys()):
			return self.dic[clave]
		else:
			if (self.padre != None):
				return self.padre.lookup(clave)
		return None

	def conectFather(self,tabla):
		self.padre = tabla

	def isValue(self,tipo):
		claves = self.dic.keys()
		for i in claves:
			if (self.dic[i][1]==tipo):
				return True
		return False

	def obtainKey(self,tipo):
		claves = self.dic.keys()
		for i in claves:
			if (self.dic[i][1]==tipo):
				return i
		return None
