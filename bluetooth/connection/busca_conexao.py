# """
# Scan/Discovery
# --------------

# Example showing how to scan for BLE devices.

# Updated on 2019-03-25 by hbldh <henrik.blidh@nedomkull.com>

# """
# import time
# import argparse
# import asyncio

# from bleak import BleakScanner, BleakClient


# class Args(argparse.Namespace):
#     macos_use_bdaddr: bool
#     services: list[str]


# async def main(args: Args):
#     print("scanning for 5 seconds, please wait...")

#     devices = await BleakScanner.discover(
#         return_adv=True,
#         service_uuids=args.services,
#         cb={"use_bdaddr": args.macos_use_bdaddr},
#     )

#     for d, a in devices.values():
#         if None == d.name:
#             continue
#         print(f"{d.name} ({d.address})")
        
#         # print()
#         # print(d)
#         # print("-" * len(str(d)))
#         # print(a)

#     # async def main(address):
#     #     async with BleakClient(address) as client:
#     #         model_number = await client.read_gatt_char(MODEL_NBR_UUID)
#     #         print(f"Model Number: {model_number.decode()}")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()

#     parser.add_argument(
#         "--services",
#         metavar="<uuid>",
#         nargs="*",
#         help="UUIDs of one or more services to filter for",
#     )

#     parser.add_argument(
#         "--macos-use-bdaddr",
#         action="store_true",
#         help="when true use Bluetooth address instead of UUID on macOS",
#     )

#     args = parser.parse_args(namespace=Args())

#     vezes = 0
#     thora = time.perf_counter()

#     while True:
#         hora = time.perf_counter()
#         if (hora - thora > 5): 
#             thora = hora
#             asyncio.run(main(args))
#             vezes += 1
#         if vezes > 20:
#             break

import asyncio
from bleak import BleakScanner

async def procurar_dispositivos():
    print("Procurando dispositivos Bluetooth...")
    # Descobre os dispositivos próximos (leva cerca de 5 segundos)
    dispositivos = await BleakScanner.discover()
    
    for d in dispositivos:
        if None == d.name:
            continue
        print(f"Nome: {d.name} | Endereço: {d.address}")# | RSSI: {d.details}dBm")

# Executa a função assíncrona
asyncio.run(procurar_dispositivos())


import asyncio
from bleak import BleakClient

# Substitua por um endereço MAC real encontrado no passo anterior
# Exemplo no Windows/Linux: "24:71:89:cc:09:05"
# Exemplo no macOS: "243E23AE-4A99-406C-B317-18F1BD7B4C84"
ENDERECO_MAC = "XX:XX:XX:XX:XX:XX" 

async def conectar(endereco):
    print(f"Tentando conectar a {endereco}...")
    
    # O bloco 'async with' garante que a conexão será fechada corretamente no final
    async with BleakClient(endereco) as cliente:
        conectado = cliente.is_connected
        print(f"Conectado: {conectado}")
        
        if conectado:
            print("Conexão estabelecida com sucesso!")
            
            # Aqui você pode listar os serviços disponíveis no dispositivo
            servicos = await cliente.get_services()
            print("Serviços encontrados:")
            for servico in servicos:
                print(f"- {servico.uuid}")

asyncio.run(conectar(ENDERECO_MAC))


# import asyncio
# from bleak import BleakClient

# # O endereço do dispositivo que você encontrou no Scanner
# ENDERECO_MAC = "XX:XX:XX:XX:XX:XX" 

# # UUIDs fictícios (você deve usar os reais do seu dispositivo)
# CHARACTERISTIC_UUID_LEITURA = "00002a37-0000-1000-8000-00805f9b34fb" 
# CHARACTERISTIC_UUID_ESCRITA = "00002a39-0000-1000-8000-00805f9b34fb"

# async def interagir_com_dispositivo(endereco):
#     async with BleakClient(endereco) as cliente:
#         if not cliente.is_connected:
#             print("Falha ao conectar.")
#             return

#         print("Conectado com sucesso!")

#         # ==========================================
#         # 1. LENDO DADOS (Read)
#         # ==========================================
#         try:
#             print(f"Lendo dados da característica: {CHARACTERISTIC_UUID_LEITURA}")
            
#             # Lê os dados em formato de bytes (bytearray)
#             dados_lidos = await cliente.read_gatt_char(CHARACTERISTIC_UUID_LEITURA)
            
#             print(f"Dados brutos recebidos (bytes): {dados_lidos}")
            
#             # Se for um texto, você decodifica assim:
#             # texto = dados_lidos.decode('utf-8')
#             # print(f"Texto recebido: {texto}")
            
#             # Se for um número (ex: 1 byte inteiro), converte assim:
#             # numero = int.from_bytes(dados_lidos, byteorder='little')
#             # print(f"Número recebido: {numero}")
            
#         except Exception as e:
#             print(f"Erro ao ler: {e}")

#         # ==========================================
#         # 2. ESCREVENDO DADOS (Write)
#         # ==========================================
#         try:
#             print(f"Escrevendo dados na característica: {CHARACTERISTIC_UUID_ESCRITA}")
            
#             # Exemplo A: Enviando um texto
#             texto_para_enviar = "Ola Mundo"
#             dados_para_enviar = texto_para_enviar.encode('utf-8') # Converte para bytes
            
#             # Exemplo B: Enviando números (ex: comando liga/desliga '0x01')
#             # dados_para_enviar = bytearray([0x01])
            
#             # O parâmetro 'response=True' pede que o dispositivo confirme que recebeu (Write with Response)
#             await cliente.write_gatt_char(CHARACTERISTIC_UUID_ESCRITA, dados_para_enviar, response=True)
#             print("Dados enviados com sucesso!")
            
#         except Exception as e:
#             print(f"Erro ao escrever: {e}")

# # Executa a função
# asyncio.run(interagir_com_dispositivo(ENDERECO_MAC))