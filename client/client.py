#!/usr/bin/env python
import pika
import threading
import time

#------------------- VARIABLES GLOBALES  ---------------------

index = []
index.append(0)     #index[0] = ID mensaje

#-------------------------------------------------------------
#-------------------------------------------------------------

#-------------------_Thread que escucha ---------------------

def escuchar():
    time.sleep(1)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    result = channel.queue_declare(queue=nombre, exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='logs', queue=queue_name)

    print(' [*] Escuchando. Para salir CTRL+Z')

    def callback(ch, method, properties, body):
        if body[:26] == " Desplegando instruccion @":
            if body[:(26 + len(nombre))] == " Desplegando instruccion @" + nombre:
                print(" [x] %r" % body)
        else:
            print(" [x] %r" % body)

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()


#-------------------_Thread que habla ---------------------

def hablar():
    while True:
        time.sleep(1)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='serverChannel')
        mensaje = raw_input()
        mensaje = nombre + "$$$$$" + mensaje + "$$$$$" + str(index[0])
        channel.basic_publish(exchange='', routing_key='serverChannel', body=mensaje)
        index[0] = index[0] + 1
        connection.close()


time.sleep(10)

#-------------------ANTES DE THREADS INICIO ---------------------
print("Bienvendo, por favor, escriba su nombre (no pueden repetirse):")
nombre = raw_input()
mensajeInicio = "Nuevo_Usuario " + nombre
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='serverChannel')
channel.basic_publish(exchange='', routing_key='serverChannel', body=mensajeInicio)
print(" **** Servidor contactado ****")
connection.close()

#-------------------ANTES DE THREADS FIN  ---------------------
threadEscuchar = threading.Thread(target=escuchar)
threadHablar = threading.Thread(target=hablar)
threadEscuchar.start()
threadHablar.start()
