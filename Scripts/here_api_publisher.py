import ast
import os

from here_api_service_modded import HereApiServiceModded


def load_traffic_incident():
    if not os.path.exists('incident'):
        print('Folder incident/ does not exist')
    for filename in os.listdir('incident'):
        with open('incident/' + filename, encoding='utf-8') as f:
            try:
                yield ast.literal_eval(f.read())
            except SyntaxError:
                pass


def load_traffic_flow():
    if not os.path.exists('flow'):
        print('Folder flow/ does not exist')
    for filename in os.listdir('flow'):
        with open('flow/' + filename, encoding='utf-8') as f:
            try:
                yield ast.literal_eval(f.read())
            except SyntaxError:
                pass


def main():
    here_api_service_modded = HereApiServiceModded()

    for ti_data in load_traffic_incident():
        here_api_service_modded.publish_incident_data(ti_data)
    for tf_data in load_traffic_flow():
        here_api_service_modded.publish_flow_data(tf_data)


if __name__ == '__main__':
    main()
