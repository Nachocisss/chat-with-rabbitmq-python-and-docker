#!/usr/bin/env python
import pika
import threading
from datetime import datetime
import time

#------------------- VARIABLES GLOBALES  ---------------------

usuariosID = []

#-------------------------------------------------------------
#-------------------------------------------------------------
    

try:
    time.sleep(10)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='serverChannel')


    def callback(ch, method, properties, body):

        print("recibido: " + str(body).replace("$$$$$", " "))

#----------------- ingreso nuevo usuarioa ---------------------
        
        if body[:14] == "Nuevo_Usuario ":
            usuariosID.append(str(body[14:]))

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost'))
            channel = connection.channel()

            channel.exchange_declare(exchange='logs', exchange_type='fanout')

            result = channel.queue_declare(queue=body[14:], exclusive=True)
            queue_name = result.method.queue

            channel.queue_bind(exchange='logs', queue=body[14:])
            connection.close()

            now = now = datetime.now()
            current_time = now.strftime("%H:%M:%S")            

            log = open("log.txt","a")
            log.write("Ingreso el usuario " + str(body[14:]) + "     ID: " + str(usuariosID.index(body[14:])) + "       TIME: "+current_time +"\n")
            log.close()
            #print("NUEVO USUARIO")


#---------------------------------------------------------------------------------------
# ------------- todos los casos restantes,  requieren separar el mensaje ---------------

        else:
            recibidoUsuario = str(body).split("$$$$$")  # [0] contiene nombre usuario [1] contiene mensaje, [2] contiene ID Mensaje
            mensaje = recibidoUsuario[0] + ": " + recibidoUsuario[1]
            idmensaje = str(usuariosID.index(recibidoUsuario[0])) + "." + recibidoUsuario[2]
            log = open("log.txt","a")
            now = now = datetime.now()
            current_time = now.strftime("%H:%M:%S")            
            log.write(mensaje + "      ID: " + idmensaje +"        TIME: " + current_time +"\n")
            log.close()

    # ------------- FUNCION HISTORIAL ---------------

            if recibidoUsuario[1] == "@historial":
                historial = " Desplegando instruccion @" + str(recibidoUsuario[0] + "\n")  
                log = open("log.txt","r")
                largonombre = len(recibidoUsuario[0])
                for linea in log:
                    if linea[:largonombre] == recibidoUsuario[0]:        #si mensaje comienza con su nombre:
                        historial = historial + "      [H]" + linea + "\n"
                log.close()
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='localhost'))
                channel = connection.channel()

                channel.exchange_declare(exchange='logs', exchange_type='fanout')

                channel.basic_publish(exchange='logs', routing_key='', body=historial)
                connection.close()

    # ------------- FUNCION USUARIOS ---------------

            if recibidoUsuario[1] == "@users":
                disponibles = " Desplegando instruccion @" + str(recibidoUsuario[0] + "\n")
                for usuario in usuariosID:
                    disponibles = disponibles + "       *" + str(usuario) + "ID: " + str(usuariosID.index(usuario))

                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='localhost'))
                channel = connection.channel()

                channel.exchange_declare(exchange='logs', exchange_type='fanout')

                channel.basic_publish(exchange='logs', routing_key='', body=disponibles)
                connection.close()
                
    # ------------- mensaje normal ---------------
            else:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='localhost'))
                channel = connection.channel()

                channel.exchange_declare(exchange='logs', exchange_type='fanout')

                channel.basic_publish(exchange='logs', routing_key='', body=mensaje)
                connection.close()

# ------------------------------------------------------
# ------------- FIN CALLBACK ---------------------------
# ------------------------------------------------------

    channel.basic_consume(
        queue='serverChannel', on_message_callback=callback, auto_ack=True)
    print(' [X] Esperando mensajes. Para salir presione CTRL+C')
    channel.start_consuming()

finally:
    channel.close()
