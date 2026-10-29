'''
PRIMEIRO EXERCICIO WHILE TRUE
n = s = q = 0
while True:
    n = int(input('Digte um número: '))
    if n == 999:
        break
    q = q + 1
    s += n
print(f'A soma vale {s} e você digitou {q}.')





nome = 'José'
idade = 33
print(f' O {nome} tem {idade} anos.')

PROGAMA TABUADA::::

n = 0
while True:
    n = int(input('Digite um número para saber a tabuada: '))
    if n < 0:
        break
    else:
        print('{} x 1 = {}'.format(n, (n * 1)))
        print('{} x 2 = {}'.format(n, (n * 2)))
        print('{} x 3 = {}'.format(n, (n * 3)))
        print('{} x 4 = {}'.format(n, (n * 4)))
        print('{} x 5 = {}'.format(n, (n * 5)))
        print('{} x 6 = {}'.format(n, (n * 6)))
        print('{} x 7 = {}'.format(n, (n * 7)))
        print('{} x 8 = {}'.format(n, (n * 8)))
        print('{} x 9 = {}'.format(n, (n * 9)))
        print('{} x 10 = {}'.format(n, (n * 10)))
        
        if produto / 2 == 0:
                print('par')
            else 
                print('par')



PROGRAMA IMPAR PAR
import random

produto = 0
escolha = 0
while True:
    print('==============INICIO DA PARTIDA =============')
    numero = random.randint(1, 100)
    n = int(input('Jogue um número: '))
    escolha = int(input('Escolha 1 para impar e 2 para par '))
    produto = n + numero
    if escolha == 1:
        print('Você escolheu impar')
        if produto % 2 != 0:
            
            print('RESULTADOS DA PARTIDA-----------------')
            print('O número escolhido pelo computador foi ',numero)
            print('O número escolhido pelo jogador foi ',n)
            print('A soma dos números é ',produto)
            print('Impar ganhou!')
            print('-----------------')
        else:
            print('Você perdeu e o programa foi interrompido')
            break
    elif escolha == 2:
        print('Você escolheu par')
        if produto % 2 == 0:
            print('RESULTADOS DA PARTIDA-----------------')
            print('O número escolhido pelo computador foi ',numero)
            print('O número escolhido pelo jogador foi ',n)
            print('A soma dos números é ',produto)
            print('Par ganhou!')
            print('-----------------')
        else:
            print('Você perdeu e o programa foi interrompido')
            break
    else:
        print('Opção inválida! Tente novamente.')
        continue
        







        PROGRAMA CADASTRAR PESSOAS
people_cadastradas = 0
idade = sexo = 0
validar = 0
cont_18 = 0
cont_homens = 0
cont_mulher_menor = 0
while True:
    people_cadastradas = people_cadastradas + 1
    print('+=======CADASTRAR PESSOAS=====+')
    idade = int(input('Idade: '))
    if idade >= 18:
         cont_18 = cont_18 + 1
    sexo = str(input('[M ou F]: ')).strip().upper()
    while sexo != 'M' and sexo != 'F':
            sexo = str(input('[M ou F]: ')).strip().upper()
    if sexo == 'M':
             cont_homens = cont_homens + 1
    elif sexo == 'F' and idade < 20:
          cont_mulher_menor = cont_mulher_menor + 1
    print('+=======FIM CADASTRAR PESSOAS=====+')
    print('Quer cadastrar mais pessoas?')
    validar = str(input('[S ou N]: ')).strip().upper()
    while validar != 'S' and validar != 'N':
        validar = str(input('[S ou N]: ')).strip().upper()

    if validar == 'N':
         break
print('Você cadastrou {} pessoas'.format(people_cadastradas))
print('Você cadastrou {} pessoas maior de 18'.format(cont_18))
print('Você cadastrou {} homens'.format(cont_homens))
print('Você cadastrou {} mulhers menos de 20'.format(cont_mulher_menor))



programa estatiscas em produtos


contador = 0
nome = preco = 0
continuar = 0
total_gasto = 0
preco_maior1000 = 0
nome_produto_maisbarato = 0
menor_preco = 0
while True:
    contador = contador + 1
    print('+=======CADASTRAR PRODUTOS=====+')
    nome = str(input('Digite o nome do produto: '))
    preco = float(input('Digite o preço do produto: '))
    menor_preco = preco
    nome_produto_maisbarato = nome
    if preco < menor_preco:
        menor_preco = preco
        nome_produto_maisbarato = nome
    if preco >= 1000:
        preco_maior1000 = preco_maior1000 + 1
    total_gasto = total_gasto + preco
    continuar = str(input('Quer continuar? [S/N]')).strip().upper()
    if continuar == 'N':
        break
    elif continuar == 'S':
        continue
    while continuar != 'S' or continuar != 'N':
       continuar = str(input('Quer continuar? [S/N]')).strip().upper()
print('O total gasto é: ', total_gasto)
print('O número de produtos com valor maior que R$1000,00 é: ', preco_maior1000)
print('O nome do produto mais barato é {} e o seu valor é {}'.format(nome_produto_maisbarato, menor_preco))






lanche = ('Hambúguer', 'Suco', 'Pizza', 'Pudim')
for cont in range (0, len(lanche)):
    print(lanche[cont])



TUPLAS

      

cont = ('zero', 'um', 'dois', 'tres', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove', 'dez', 'onze', 'doze', 'treze', 'quatorze', 'quinze', 'dezesseis', 'dezessete', 'dezoito', 'dezenove', 'vinte')
while True:
    num = int(input('Digite um número de 0 a 20: '))
    if 0 <= num <= 20:
        break   
    print('Tente novamente. ', end='')
print('Você digitou o número: ', {cont[num]})

  '''


times = (
    "Flamengo",
    "Palmeiras",
    "Athletico-PR",
    "Fluminense",
    "Bahia",
    "Cruzeiro",
    "Atlético-MG",
    "Santos",
    "Bragantino",
    "São Paulo",
    "Coritiba",
    "Vitória",
    "Botafogo",
    "Vasco",
    "Mirassol",
    "Corinthians",
    "Internacional",
    "Grêmio",
    "Remo",
    "Chapecoense",
)

print('Esses são os 5 primeiros', times[0:5])

print('Esses são os 5 ultimos', times[-5:])

print(f'Times em ordem alfabetica: {sorted(times)}')