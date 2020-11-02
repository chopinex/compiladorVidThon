import re


class Token:
	palabra=""
	indice=-1
	tipo=''

	def toString(self):
		return "<\""+self.palabra+"\","+str(self.indice)+","+self.tipo+">"

def reconoceNumero(linea,idx):
	m=re.match("[-+]?\d*\.?\d*",linea[idx:])
	#m=re.match("\d+",linea[idx:])
	token=Token()
	token.palabra=m.group(0)
	token.indice=idx+m.start()
	if token.palabra.find(".")<0:
		token.tipo='int'
	else:
		token.tipo='flt'
	return token,idx+m.end()

def reconoceVariable(linea,idx):
	clave=["for","while","if","else","break","import","export","and","or","not","play","return","function"]
	tkClv=["for","whl","if","els","brk","imp","exp","and","or","not","ply","ret","fun"]
	m=re.match("(\_*[a-zA-Z][\_a-zA-Z0-9]*)+",linea[idx:])
	token=Token()
	token.palabra=m.group(0)
	token.indice=idx+m.start()
	if token.palabra in clave:
		token.tipo=tkClv[clave.index(token.palabra)]	
	else:
		token.tipo='id'
	return token,idx+m.end()

def reconoceCadena(linea,idx):
	m=re.match("\"[^\"']*\"",linea[idx:])
	token=Token()
	token.palabra=m.group(0)[1:-1]
	token.indice=idx+m.start()+1
	token.tipo='str'
	return token,idx+m.end()

def reconoceCaracter(linea,idx):
	m=re.match("'\\?[^\"']'",linea[idx:])
	token=Token()
	token.palabra=m.group(0)[1:-1]
	token.indice=idx+m.start()+1
	token.tipo='chr'
	return token,idx+m.end()		

def analizadorLexico(linea):
	simbolos=['{','}','(',')','+','-','*','/','=',";",":",","]
	tkSim=["liz","lde","piz","pde","sum","res","mul","div","igl","pyc","dps","com"]
	tokens=[]
	idx=0
	while idx<len(linea):
		if linea[idx].isdigit():
			token,idx=reconoceNumero(linea,idx)
			tokens.append(token)
		elif linea[idx]=='"':
			token,idx=reconoceCadena(linea,idx)
			tokens.append(token)
		elif linea[idx].isalpha():
			token,idx=reconoceVariable(linea,idx)
			tokens.append(token)
		elif linea[idx]==' ':
			idx=idx+1
		elif linea[idx] in simbolos:
			token=Token()
			token.palabra=linea[idx]
			token.indice=idx
			token.tipo=tkSim[simbolos.index(token.palabra)]
			tokens.append(token)
			idx=idx+1
	return tokens

class Produccion:
	izq=""
	der=""

	def __init__(self,i,d):
		self.izq=i
		self.der=d

	def toString(self):
		return self.izq+" := "+self.der

class Gramatica:
	producciones=[]
	terminales=[]
	noterminales=[]

	def cargar(self,texto):
		lineas =texto.splitlines()
		for linea in lineas:
			n=linea.find(" := ")
			self.producciones.append(Produccion(linea[:n],linea[n+4:]))
			self.noterminales.append(linea[:n])
			tokens=linea[n+4:].split()
			for token in tokens:
				if token[0].isupper():
					self.noterminales.append(token)
				else:
					self.terminales.append(token)

	def getProduccion(self,izquierda):
		ret=[]
		for prod in self.producciones:
			if prod.izq == izquierda:
					ret.append(prod.der)
		return ret

	def print(self):
		for prod in self.producciones:
			print(prod.toString())

class TAS:
	tablaSintactica={}
	def llenarEstaticamente(self):
		self.tablaSintactica["P"]={}
		self.tablaSintactica["P"]["liz"]=["S"]
		self.tablaSintactica["P"]["pyc"]=["S"]
		self.tablaSintactica["P"]["if"]=["S"]
		self.tablaSintactica["P"]["piz"]=["S"]
		self.tablaSintactica["P"]["whl"]=["S"]
		self.tablaSintactica["P"]["ret"]=["S"]
		self.tablaSintactica["P"]["fun"]=["S"]
		self.tablaSintactica["P"]["id"]=["S"]
		self.tablaSintactica["P"]["int"]=["S"]
		self.tablaSintactica["P"]["flt"]=["S"]
		self.tablaSintactica["P"]["str"]=["S"]
		self.tablaSintactica["P"]["chr"]=["S"]
		self.tablaSintactica["P"]["$"]=["S"]
		self.tablaSintactica["S"]={}
		self.tablaSintactica["S"]["liz"]=["liz","S","lde"]
		self.tablaSintactica["S"]["lde"]=["ES"]
		self.tablaSintactica["S"]["pyc"]=["pyc"]
		self.tablaSintactica["S"]["if"]=["IS"]
		self.tablaSintactica["S"]["piz"]=["ES"]
		self.tablaSintactica["S"]["whl"]=["WS"]
		self.tablaSintactica["S"]["ret"]=["RS"]
		self.tablaSintactica["S"]["fun"]=["FS"]
		self.tablaSintactica["S"]["id"]=["ES"]
		self.tablaSintactica["S"]["int"]=["ES"]
		self.tablaSintactica["S"]["flt"]=["ES"]
		self.tablaSintactica["S"]["$"]=["ES"]
		self.tablaSintactica["ES"]={}
		self.tablaSintactica["ES"]["lde"]=["lambda"]
		self.tablaSintactica["ES"]["pde"]=["E","pyc","S"]
		self.tablaSintactica["ES"]["id"]=["E","pyc","S"]
		self.tablaSintactica["ES"]["int"]=["E","pyc","S"]
		self.tablaSintactica["ES"]["flt"]=["E","pyc","S"]
		self.tablaSintactica["ES"]["$"]=["lambda"]
		self.tablaSintactica["IS"]={}
		self.tablaSintactica["IS"]["if"]=["if","piz","E","pde","S"]
		self.tablaSintactica["WS"]={}
		self.tablaSintactica["WS"]["whl"]=["whl","piz","E","pde","S"]
		self.tablaSintactica["RS"]={}
		self.tablaSintactica["RS"]["ret"]=["ret","E","pyc"]
		self.tablaSintactica["FS"]={}
		self.tablaSintactica["FS"]["fun"]=["fun","V","(","PR",")","S"]
		self.tablaSintactica["E"]={}
		self.tablaSintactica["E"]["piz"]=["piz","E","pde"]
		self.tablaSintactica["E"]["id"]=["V","ET"]
		self.tablaSintactica["E"]["int"]=["int","ET"]
		self.tablaSintactica["E"]["flt"]=["flt","ET"]
		self.tablaSintactica["E"]["imp"]=["IE"]
		self.tablaSintactica["E"]["exp"]=["XE"]
		self.tablaSintactica["V"]={}
		self.tablaSintactica["V"]["id"]=["id"]
		self.tablaSintactica["ET"]={}
		self.tablaSintactica["ET"]["pyc"]=["lambda"]
		self.tablaSintactica["ET"]["pde"]=["lamdba"]
		self.tablaSintactica["ET"]["id"]=["V"]
		self.tablaSintactica["ET"]["sum"]=["O","E"]
		self.tablaSintactica["ET"]["res"]=["O","E"]
		self.tablaSintactica["ET"]["mul"]=["O","E"]
		self.tablaSintactica["ET"]["div"]=["O","E"]
		self.tablaSintactica["ET"]["igl"]=["Q","ET"]
		self.tablaSintactica["ET"]["int"]=["int"]
		self.tablaSintactica["ET"]["flt"]=["flt"]
		self.tablaSintactica["ET"]["str"]=["str"]
		self.tablaSintactica["ET"]["chr"]=["chr"]
		self.tablaSintactica["O"]={}
		self.tablaSintactica["O"]["sum"]=["sum"]
		self.tablaSintactica["O"]["res"]=["res"]
		self.tablaSintactica["O"]["mul"]=["mul"]
		self.tablaSintactica["O"]["div"]=["div"]
		self.tablaSintactica["Q"]={}
		self.tablaSintactica["Q"]["igl"]=["igl"]
		self.tablaSintactica["PR"]={}
		self.tablaSintactica["PR"]["pde"]=["lambda"]
		self.tablaSintactica["PR"]["id"]=["V", "PR"]
		self.tablaSintactica["PR"]["com"]=["com","V", "PR"]
		self.tablaSintactica["IE"]={}
		self.tablaSintactica["IE"]["imp"]=["imp","piz","str","pde"]
		self.tablaSintactica["XE"]={}
		self.tablaSintactica["XE"]["exp"]=["exp","piz","str","pde"]
	def print(self):
		for noter, ter in self.tablaSintactica.items():
			for key in ter:
				print(noter+" vs "+key+" =>", end= ' ')
				print(ter[key])

gram=("P := S\nS := { S }\nS := IS\nS := ES\nS := WS\nS := RS\nS := FS\nS := ;\nES := E ; S\nES := lambda\nIS := if ( E ) S\nWS := whl ( E ) S\nRS := ret E ; S\n"
      "FS := fun V ( PR ) S\nE := V ET\nE := int ET\nE := flt ET\nE := ( E )\nV := id\nET := O E\nET := int\nET := flt\nET := V\nET := lambda\nO := +\nO := =\n"
	  "PR := V PR\nPR := , V PR\nPR := lambda")
g=Gramatica()
g.cargar(gram)
t=TAS()
t.llenarEstaticamente()

tokens=analizadorLexico("accum+1+0.5;")

cola=[]
for token in tokens:
	cola.insert(0,token.tipo)
cola.insert(0,"$")
pila=[]
pila.append("$")
pila.append("P")
arbol="P"
while pila and cola:
	print(arbol)
	if cola[-1]==pila[-1]:
		#print("out: "+cola[-1])
		cola.pop()
		pila.pop()
	else:
		tmp = pila.pop()
		#print(tmp + " -> ", end=' ')
		artmp=""
		t.tablaSintactica[tmp][cola[-1]].reverse()
		for symbol in t.tablaSintactica[tmp][cola[-1]]:
			if symbol != "lambda":
				artmp= symbol+' '+artmp
				pila.append(symbol)
		t.tablaSintactica[tmp][cola[-1]].reverse()
		arbol=arbol.replace(tmp,artmp)
		arbol = " ".join(arbol.split())
		#print()


