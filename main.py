import sys

from Samples.geocoder import get_coordinates, get_nearest_object


def main():
    # Забираем адресную точку из параметров запуска.
    address = ''
    try:
        address = " ".join(sys.argv[1:])
    except:
        print('No data')
        exit(1)

    if not address:
        print('No data')
        exit(1)

    # Получаем координаты точки
    address_point = get_coordinates(address)

    # Получаем район.
    district_name = get_nearest_object(address_point, "district")
    print(district_name)


if __name__ == "__main__":
    main()