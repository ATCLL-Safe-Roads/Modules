from here_api_service import HereApiService
from mqtt import Consumer, Producer
from pothole_service import PotholeService
from process_service import ProcessService
from scheduler import Scheduler


def main():
    # Aveiro Information
    latitude = 40.63733
    longitude = -8.64850
    radius = 5000  # meters

    # SLP Information
    p_ids = {1, 3, 4, 10, 11, 12, 14, 15, 18, 19, 21, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 33, 35, 36, 37, 38, 39,
             40, 41, 44}
    p_names = {1: 'Rua da Pega', 3: 'Ponte da Dobadoura', 4: 'Rotunda Monumento ao Marnoto e à Salineira',
               10: 'Avenida Dr. Lourenço Peixinho, cruzamento frente à Segurança social',
               11: 'Avenida Dr. Lourenço Peixinho, cruzamento com a Rua do Eng. Oudinot',
               12: 'Avenida Dr. Lourenço Peixinho, entroncamento com a Rua Luis G. Carvalho',
               14: 'Avenida Dr. Lourenço Peixinho, entroncamento com a Rua Luis G. Carvalho',
               15: 'Cais de São Roque', 18: 'Rua Combatentes da Grande Guerra',
               19: 'Parque dos Remadores Olímpicos', 21: 'Rotunda do Oita', 22: 'Cais da Fonte Nova',
               23: 'Rotunda do Hospital', 24: 'Quiosque ao lado do Hospital', 25: 'Escola da Glória',
               27: 'Sé', 28: 'José Estevão', 29: 'S. Martinho II', 30: 'Avenida 25 de Abril',
               31: ' Dr. Mario Sacramento II', 32: 'Convivio', 33: 'Rua Doutor Mário Sacramento',
               35: 'Avenida da Universidade', 36: 'Rotunda do Pingo Doce', 38: 'Parque da CP',
               39: 'Rotunda de Esgueira', 41: 'Quartel I', 37: 'Rotunda Forca', 40: 'Quartel II', 44: 'Ria'}
    p_points = {1: (40.63476, -8.66038), 3: (40.64074, -8.65705), 4: (40.64154, -8.65802),
                10: (40.64283, -8.64828), 11: (40.64310, -8.64675), 12: (40.64330, -8.64427),
                14: (40.64237, -8.65064), 15: (40.64416, -8.65616), 18: (40.63970, -8.65295),
                19: (40.64339, -8.65847), 21: (40.64244, -8.64628), 22: (40.63972, -8.64352),
                23: (40.63475, -8.65592), 24: (40.63319, -8.65590), 25: (40.63693, -8.65324),
                27: (40.63946, -8.64960), 28: (40.63733, -8.64850), 29: (40.63646, -8.64986),
                30: (40.63605, -8.64657), 31: (40.63609, -8.64438), 32: (40.63443, -8.64882),
                33: (40.63245, -8.64859), 35: (40.63028, -8.65423), 36: (40.64121, -8.64286),
                37: (40.64088, -8.63959), 38: (40.64344, -8.63981), 39: (40.64551, -8.64249),
                40: (40.64480, -8.64288), 41: (40.64550, -8.64597), 44: (40.64602, -8.65285)}

    # Producer
    mqtt_producer = Producer()

    # Process Service
    process_service = ProcessService(p_ids, p_names, p_points, mqtt_producer)

    # Consumer Thread
    mqtt_consumer = Consumer(process_service)
    mqtt_consumer.start()

    # HERE API Service
    here_api_service = HereApiService(latitude, longitude, radius, mqtt_producer)

    # Pothole Service
    pothole_service = PotholeService(p_ids, p_names, p_points, mqtt_producer)

    # Scheduler Thread
    scheduler = Scheduler(here_api_service, pothole_service)
    scheduler.start()


if __name__ == '__main__':
    main()
